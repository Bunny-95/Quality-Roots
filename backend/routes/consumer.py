"""
Organic Roots Consumer Routes
API endpoints for consumer verification and product journey
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from database import get_db
from models.batch import Batch
from models.product import Product
from models.user import User
from models.supply_chain import SupplyChainEvent
from blockchain.chain import blockchain_manager

router = APIRouter(prefix="/consumer", tags=["consumer"])

# Default retail price per kg (₹) when DB value is missing
_GRADE_PRICE_MAP = {"A": 450, "B": 280, "C": 150}


def _effective_price_per_kg(batch: Batch) -> float:
    if batch.price_per_kg is not None and batch.price_per_kg > 0:
        return float(batch.price_per_kg)
    return float(_GRADE_PRICE_MAP.get(batch.grade, 200))


def _ai_confidence_from_blockchain(batch: Batch) -> Optional[float]:
    """Return AI grading confidence as 0.0–1.0 from genesis block data, if present."""
    if batch.blockchain_block_index is None:
        return None
    block = blockchain_manager.get_block(batch.blockchain_block_index)
    if not block:
        return None
    data = block.get("data")
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict):
        return None
    raw = data.get("ai_confidence")
    if raw is None:
        raw = data.get("confidence")
    if raw is None:
        raw = data.get("confidence_score")
    if raw is None:
        return None
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    if v > 1.0:
        v = v / 100.0
    return v


def _farmer_display(user: Optional[User]) -> tuple:
    if not user:
        return "Unknown", "Unknown"
    name = (user.name or "").strip()
    if not name:
        name = (user.email or "").strip() or "Unknown"
    location = (user.location or "").strip() or "Unknown"
    return name, location


def _batch_status_display(batch: Batch) -> str:
    s = (batch.status or "").strip()
    return s if s else "Active"


# Pydantic models
class ProductJourneyEvent(BaseModel):
    id: int
    event_type: str
    actor_name: str
    actor_role: str
    location: str
    notes: str = None
    timestamp: datetime
    blockchain_verified: bool = False

class ProductJourney(BaseModel):
    batch_code: str
    product_name: str
    product_type: str
    origin_state: str
    farmer_name: str
    farmer_location: str
    harvest_date: datetime
    grade: str
    quality_score: float
    quantity_kg: float
    price_per_kg: Optional[float] = 0.0
    ai_confidence: Optional[float] = None
    status: str = "Active"
    qr_code_url: str
    journey_events: List[ProductJourneyEvent]
    blockchain_verified: bool
    fraud_free: bool
    created_at: datetime

class VerificationResponse(BaseModel):
    success: bool
    message: str
    product_journey: Optional[ProductJourney] = None

@router.get("/verify/{batch_code}", response_model=VerificationResponse)
async def verify_product(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Verify a product by batch code - public endpoint (no auth required)"""
    
    # Find batch
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    
    if not batch:
        return VerificationResponse(
            success=False,
            message=f"Product with batch code {batch_code} not found"
        )
    
    # Get product information
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    if not product:
        return VerificationResponse(
            success=False,
            message="Product information not found"
        )
    
    farmer = db.query(User).filter(User.id == batch.farmer_id).first()
    farmer_name, farmer_location = _farmer_display(farmer)
    
    # Get supply chain events
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch.id
    ).order_by(SupplyChainEvent.timestamp).all()
    
    # Build journey events
    journey_events = []
    fraud_free = True
    
    for event in events:
        # Check if event is blockchain verified
        blockchain_verified = event.blockchain_block_index is not None
        
        # Check for fraud flags
        if event.is_flagged:
            fraud_free = False
        
        journey_events.append(ProductJourneyEvent(
            id=event.id,
            event_type=event.event_type,
            actor_name=event.actor_name,
            actor_role=event.actor_role,
            location=event.location,
            notes=event.notes,
            timestamp=event.timestamp,
            blockchain_verified=blockchain_verified
        ))
    
    # Verify blockchain integrity for this batch
    blockchain_verified = True
    try:
        # Get blockchain blocks for this batch
        batch_blocks = []
        for event in events:
            if event.blockchain_block_index:
                block = blockchain_manager.get_block(event.blockchain_block_index)
                if block:
                    batch_blocks.append(block)
        
        # Verify chain integrity
        if batch_blocks:
            verification = blockchain_manager.verify_chain()
            blockchain_verified = verification['is_valid']
    
    except Exception as e:
        blockchain_verified = False
    
    # Generate QR code URL
    qr_code_url = f"/qr/{batch_code}"
    
    price_per_kg = _effective_price_per_kg(batch)
    ai_confidence = _ai_confidence_from_blockchain(batch)
    status_display = _batch_status_display(batch)

    product_journey = ProductJourney(
        batch_code=batch.batch_code,
        product_name=product.name,
        product_type=product.type,
        origin_state=product.origin_state,
        farmer_name=farmer_name,
        farmer_location=farmer_location,
        harvest_date=batch.harvest_date,
        grade=batch.grade,
        quality_score=batch.quality_score,
        quantity_kg=batch.quantity_kg,
        price_per_kg=price_per_kg,
        ai_confidence=ai_confidence,
        status=status_display,
        qr_code_url=qr_code_url,
        journey_events=journey_events,
        blockchain_verified=blockchain_verified,
        fraud_free=fraud_free,
        created_at=batch.created_at
    )
    
    return VerificationResponse(
        success=True,
        message="Product verified successfully",
        product_journey=product_journey
    )

@router.get("/verify-qr/{batch_code}")
async def verify_by_qr(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Verify product by scanning QR code - redirects to main verification"""
    
    # This endpoint is typically called from QR code scan
    # It redirects to the main verification endpoint
    verification_result = await verify_product(batch_code, db)
    
    return verification_result

@router.get("/product-info/{batch_code}")
async def get_product_info(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Get basic product information without full journey"""
    
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    farmer = db.query(User).filter(User.id == batch.farmer_id).first()
    
    return {
        "batch_code": batch.batch_code,
        "product_name": product.name if product else "Unknown",
        "product_type": product.type if product else "Unknown",
        "origin_state": product.origin_state if product else "Unknown",
        "farmer_name": farmer.name if farmer else "Unknown",
        "grade": batch.grade,
        "quality_score": batch.quality_score,
        "harvest_date": batch.harvest_date.isoformat(),
        "created_at": batch.created_at.isoformat()
    }

@router.get("/batch-events/{batch_code}")
async def get_batch_events(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Get supply chain events for a batch"""
    
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch.id
    ).order_by(desc(SupplyChainEvent.timestamp)).all()
    
    event_list = []
    for event in events:
        event_list.append({
            "id": event.id,
            "event_type": event.event_type,
            "actor_name": event.actor_name,
            "actor_role": event.actor_role,
            "location": event.location,
            "notes": event.notes,
            "timestamp": event.timestamp.isoformat(),
            "blockchain_index": event.blockchain_block_index,
            "fraud_score": event.fraud_score,
            "is_flagged": event.is_flagged
        })
    
    return {
        "batch_code": batch_code,
        "total_events": len(event_list),
        "events": event_list
    }

@router.get("/blockchain-verify/{batch_code}")
async def verify_blockchain_for_batch(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Verify blockchain integrity for a specific batch"""
    
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get all blockchain blocks for this batch
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch.id,
        SupplyChainEvent.blockchain_block_index.isnot(None)
    ).all()
    
    if not events:
        return {
            "batch_code": batch_code,
            "blockchain_verified": False,
            "message": "No blockchain records found for this batch"
        }
    
    # Get blockchain blocks
    blocks = []
    for event in events:
        block = blockchain_manager.get_block(event.blockchain_block_index)
        if block:
            blocks.append({
                "index": block["index"],
                "hash": block["hash"],
                "timestamp": block["timestamp"],
                "event_type": event.event_type,
                "verified": True
            })
    
    # Verify chain integrity
    chain_verification = blockchain_manager.verify_chain()
    
    return {
        "batch_code": batch_code,
        "blockchain_verified": chain_verification["is_valid"],
        "total_blocks": len(blocks),
        "blocks": blocks,
        "chain_integrity": chain_verification
    }

@router.get("/quality-details/{batch_code}")
async def get_quality_details(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Get detailed quality information for a batch"""
    
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    return {
        "batch_code": batch.batch_code,
        "grade": batch.grade,
        "quality_score": batch.quality_score,
        "quality_attributes": {
            "moisture_level": batch.moisture_level,
            "color_score": batch.color_score,
            "aroma_score": batch.aroma_score,
            "defect_percentage": batch.defect_percentage,
            "weight_per_unit": batch.weight_per_unit
        },
        "grade_explanation": {
            "A": "Premium quality - Excellent attributes, minimal defects",
            "B": "Good quality - Above average attributes, minor defects",
            "C": "Standard quality - Acceptable attributes, some defects"
        }.get(batch.grade, "Unknown grade"),
        "quality_recommendations": [
            "Store in cool, dry conditions",
            "Check for any signs of spoilage before use",
            "Follow best practices for this product type"
        ]
    }

@router.get("/search")
async def search_products(
    query: str = None,
    product_type: str = None,
    grade: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search for products with optional filters"""
    
    # Start with base query
    batches_query = db.query(Batch).join(Product, Batch.product_id == Product.id)
    
    # Apply filters
    if query:
        batches_query = batches_query.filter(
            Product.name.contains(query) |
            Batch.batch_code.contains(query) |
            Product.origin_state.contains(query)
        )
    
    if product_type:
        batches_query = batches_query.filter(Product.type == product_type)
    
    if grade:
        batches_query = batches_query.filter(Batch.grade == grade)
    
    # Get results
    batches = batches_query.limit(limit).all()
    
    results = []
    for batch in batches:
        product = batch.product
        farmer = batch.farmer
        
        results.append({
            "batch_code": batch.batch_code,
            "product_name": product.name,
            "product_type": product.type,
            "origin_state": product.origin_state,
            "farmer_name": farmer.name,
            "grade": batch.grade,
            "quality_score": batch.quality_score,
            "harvest_date": batch.harvest_date.isoformat(),
            "created_at": batch.created_at.isoformat()
        })
    
    return {
        "query": query,
        "filters": {
            "product_type": product_type,
            "grade": grade
        },
        "total_results": len(results),
        "results": results
    }

@router.get("/product-types")
async def get_product_types(db: Session = Depends(get_db)):
    """Get all available product types"""
    
    product_types = db.query(Product.type).distinct().all()
    
    return {
        "product_types": [ptype[0] for ptype in product_types]
    }

@router.get("/grades")
async def get_available_grades():
    """Get all available grade options"""
    
    return {
        "grades": ["A", "B", "C"],
        "descriptions": {
            "A": "Premium quality - Excellent attributes, minimal defects",
            "B": "Good quality - Above average attributes, minor defects", 
            "C": "Standard quality - Acceptable attributes, some defects"
        }
    }

@router.get("/journey/{batch_code}")
async def get_product_journey(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Get complete product journey - no auth required for consumers"""
    
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    farmer = db.query(User).filter(User.id == batch.farmer_id).first()
    farmer_name, farmer_location = _farmer_display(farmer)

    # Get supply chain events
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch.id
    ).order_by(SupplyChainEvent.timestamp).all()
    
    # Build journey events
    journey_events = []
    for event in events:
        journey_events.append({
            "id": event.id,
            "event_type": event.event_type,
            "actor_name": event.actor_name,
            "actor_role": event.actor_role,
            "location": event.location,
            "notes": event.notes,
            "timestamp": event.timestamp.isoformat(),
            "blockchain_verified": event.blockchain_block_index is not None
        })
    
    price_per_kg = _effective_price_per_kg(batch)
    ai_confidence = _ai_confidence_from_blockchain(batch)
    status_display = _batch_status_display(batch)

    return {
        "batch_code": batch.batch_code,
        "product_name": product.name,
        "product_type": product.type,
        "origin_state": product.origin_state,
        "farmer_name": farmer_name,
        "farmer_location": farmer_location,
        "harvest_date": batch.harvest_date.isoformat(),
        "grade": batch.grade,
        "quality_score": batch.quality_score,
        "quantity_kg": batch.quantity_kg,
        "price_per_kg": price_per_kg,
        "ai_confidence": ai_confidence,
        "status": status_display,
        "qr_code_url": f"/qr_codes/qr_{batch.batch_code}.png",
        "journey_events": journey_events,
        "blockchain_verified": batch.blockchain_block_index is not None,
        "fraud_free": not any(event.is_flagged for event in events),
        "created_at": batch.created_at.isoformat()
    }

@router.get("/stats")
async def get_consumer_stats(db: Session = Depends(get_db)):
    """Get general statistics for consumers"""
    
    # Total products
    total_batches = db.query(Batch).count()
    
    # Grade distribution
    grade_distribution = db.query(
        Batch.grade,
        func.count(Batch.id).label('count')
    ).group_by(Batch.grade).all()
    
    grade_stats = {grade: count for grade, count in grade_distribution}
    
    # Product type distribution
    type_distribution = db.query(
        Product.type,
        func.count(Product.id).label('count')
    ).join(Batch, Product.id == Batch.product_id).group_by(Product.type).all()
    
    type_stats = {ptype: count for ptype, count in type_distribution}
    
    # Recent activity
    recent_batches = db.query(Batch).order_by(
        desc(Batch.created_at)
    ).limit(5).all()
    
    recent_activity = []
    for batch in recent_batches:
        recent_activity.append({
            "batch_code": batch.batch_code,
            "product_name": batch.product.name,
            "grade": batch.grade,
            "created_at": batch.created_at.isoformat()
        })
    
    return {
        "total_products": total_batches,
        "grade_distribution": grade_stats,
        "type_distribution": type_stats,
        "recent_activity": recent_activity
    }
