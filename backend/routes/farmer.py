"""
Organic Roots Farmer Routes
API endpoints for farmer-specific functionality
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.product import Product
from models.batch import Batch
from models.supply_chain import SupplyChainEvent
from utils.security import get_current_active_user, require_farmer, require_farmer_or_admin
from ai.quality_grader import quality_grader
from ai.demand_forecaster import demand_forecaster
from utils.qr_generator import qr_generator
from blockchain.chain import blockchain_manager

router = APIRouter(prefix="/farmer", tags=["farmer"])

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    type: str  # spice/coffee/tea/millet/organic
    description: str = None
    origin_state: str

class ProductResponse(BaseModel):
    id: int
    name: str
    type: str
    description: str = None
    origin_state: str
    farmer_id: int
    created_at: datetime

class BatchCreate(BaseModel):
    product_id: int
    quantity_kg: float
    harvest_date: datetime
    moisture_level: float
    color_score: float
    aroma_score: float
    defect_percentage: float
    weight_per_unit: float

class BatchResponse(BaseModel):
    id: int
    batch_code: str
    product_id: int
    farmer_id: int
    quantity_kg: float
    harvest_date: datetime
    moisture_level: float
    color_score: float
    aroma_score: float
    defect_percentage: float
    weight_per_unit: float
    grade: str
    quality_score: float
    price_per_kg: Optional[float] = 0.0 
    qr_code_path: str = None
    blockchain_block_index: int = None
    status: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_batches: int
    total_products: int
    grade_a_percentage: float
    avg_quality_score: float
    flagged_batches: int
    recent_batches: List[Dict[str, Any]]

@router.get("/dashboard", response_model=DashboardStats)
async def get_farmer_dashboard(
    current_user: User = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Get farmer dashboard statistics (admins see all data)"""
    
    # If admin, show all data; if farmer, show only their data
    if current_user.role == "admin":
        batches = db.query(Batch).all()
        products = db.query(Product).all()
    else:
        # Get farmer's batches
        batches = db.query(Batch).filter(Batch.farmer_id == current_user.id).all()
        
        # Get farmer's products
        products = db.query(Product).filter(Product.farmer_id == current_user.id).all()
    
    # Calculate statistics
    total_batches = len(batches)
    total_products = len(products)
    
    if total_batches > 0:
        grade_a_count = sum(1 for batch in batches if batch.grade == 'A')
        grade_a_percentage = (grade_a_count / total_batches) * 100
        
        avg_quality_score = sum(batch.quality_score for batch in batches) / total_batches
        flagged_batches = sum(1 for batch in batches if batch.status == 'FLAGGED')
    else:
        grade_a_percentage = 0.0
        avg_quality_score = 0.0
        flagged_batches = 0
    
    # Get recent batches (last 5)
    recent_batches = []
    for batch in sorted(batches, key=lambda x: x.created_at, reverse=True)[:5]:
        recent_batches.append({
            "batch_code": batch.batch_code,
            "product_name": batch.product.name if batch.product else "Unknown",
            "grade": batch.grade,
            "quality_score": batch.quality_score,
            "status": batch.status,
            "created_at": batch.created_at.isoformat()
        })
    
    return DashboardStats(
        total_batches=total_batches,
        total_products=total_products,
        grade_a_percentage=grade_a_percentage,
        avg_quality_score=avg_quality_score,
        flagged_batches=flagged_batches,
        recent_batches=recent_batches
    )

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    
    # Validate product type
    valid_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
    if product_data.type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid product type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create product
    new_product = Product(
        name=product_data.name,
        type=product_data.type,
        description=product_data.description,
        origin_state=product_data.origin_state,
        farmer_id=current_user.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.get("/products", response_model=List[ProductResponse])
async def get_farmer_products(
    current_user: User = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Get all products for the current farmer (admin sees all)"""
    
    if current_user.role == "admin":
        products = db.query(Product).all()
    else:
        products = db.query(Product).filter(Product.farmer_id == current_user.id).all()
    return products

@router.post("/batches", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_data: BatchCreate,
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db)
):
    """Create a new batch with AI grading and QR code generation"""
    
    # Verify product belongs to farmer
    product = db.query(Product).filter(
        Product.id == batch_data.product_id,
        Product.farmer_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or doesn't belong to you"
        )
    
    # Generate unique batch code
    batch_code = f"{product.type.upper()}{datetime.now().strftime('%Y%m%d')}{len(product.batches) + 1:03d}"
    
    # AI quality grading
    grading_input = {
        "batch_code": batch_code,
        "product_type": product.type,
        "moisture_level": batch_data.moisture_level,
        "color_score": batch_data.color_score,
        "aroma_score": batch_data.aroma_score,
        "defect_percentage": batch_data.defect_percentage,
        "weight_per_unit": batch_data.weight_per_unit
    }
    
    grade_result = quality_grader.grade_batch(grading_input)
    
    # Calculate price based on grade (A = ₹75/kg, B = ₹55/kg, C = ₹40/kg)
    grade_prices = {'A': 75.0, 'B': 55.0, 'C': 40.0}
    price_per_kg = grade_prices.get(grade_result['grade'], 40.0)
    
    # Create batch
    new_batch = Batch(
        batch_code=batch_code,
        product_id=batch_data.product_id,
        farmer_id=current_user.id,
        quantity_kg=batch_data.quantity_kg,
        harvest_date=batch_data.harvest_date,
        moisture_level=batch_data.moisture_level,
        color_score=batch_data.color_score,
        aroma_score=batch_data.aroma_score,
        defect_percentage=batch_data.defect_percentage,
        weight_per_unit=batch_data.weight_per_unit,
        grade=grade_result['grade'],
        quality_score=grade_result['quality_score'],
        price_per_kg=price_per_kg,
        status="CREATED"
    )
    
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    
    # Generate QR code
    qr_result = qr_generator.create_qr_code(batch_code)
    new_batch.qr_code_path = qr_result['relative_path']
    
    # Record blockchain event
    blockchain_data = {
        "event_type": "BATCH_CREATED",
        "batch_code": batch_code,
        "product_id": batch_data.product_id,
        "farmer_id": current_user.id,
        "quantity_kg": batch_data.quantity_kg,
        "grade": grade_result['grade'],
        "quality_score": grade_result['quality_score'],
        "ai_confidence": grade_result['confidence'],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    block = blockchain_manager.add_supply_chain_event(blockchain_data)
    new_batch.blockchain_block_index = block.index
    
    # Create supply chain event
    supply_event = SupplyChainEvent(
        batch_id=new_batch.id,
        event_type="CREATED",
        actor_name=current_user.name,
        actor_role="farmer",
        location=current_user.location or "Farm Location",
        notes=f"Batch created with Grade {grade_result['grade']}",
        blockchain_block_index=block.index
    )
    
    db.add(supply_event)
    db.commit()
    db.refresh(new_batch)
    
    return new_batch

@router.get("/batches", response_model=List[BatchResponse])
async def get_farmer_batches(
    current_user: User = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all batches for the current farmer (admin sees all)"""
    
    if current_user.role == "admin":
        batches = db.query(Batch).offset(skip).limit(limit).all()
    else:
        batches = db.query(Batch).filter(
            Batch.farmer_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return batches

@router.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch_detail(
    batch_id: int,
    current_user: User = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific batch"""
    
    if current_user.role == "admin":
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
    else:
        batch = db.query(Batch).filter(
            Batch.id == batch_id,
            Batch.farmer_id == current_user.id
        ).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    return batch

@router.get("/demand-forecast")
async def get_demand_forecast(
    product_type: str,
    current_user: User = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Get demand forecast (admins see system-wide, farmers see their products)"""
    
    # Validate product type
    valid_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
    if product_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid product type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Generate sample historical data (in real app, this would come from actual sales)
    historical_prices = [45.2, 46.1, 44.8, 47.3, 48.1, 46.9, 47.5, 48.2, 49.1, 47.8, 
                        48.5, 49.3, 50.1, 48.9, 49.7, 50.5, 51.2, 50.0, 50.8, 51.5,
                        52.3, 51.1, 51.9, 52.7, 53.4, 52.2, 53.0, 53.8, 54.5, 53.3]
    
    historical_demand = [850, 870, 840, 890, 910, 880, 900, 920, 940, 910, 
                         930, 950, 970, 940, 960, 980, 1000, 970, 990, 1010,
                         1030, 1000, 1020, 1040, 1060, 1030, 1050, 1070, 1090, 1060]
    
    # Get forecast
    season = "summer"  # Could be determined by current date
    forecast = demand_forecaster.forecast(product_type, historical_prices, historical_demand, season)
    
    return forecast

@router.get("/quality-insights")
async def get_quality_insights(
    current_user: User = Depends(require_farmer_or_admin),
    db: Session = Depends(get_db)
):
    """Get quality insights for farmer's batches (admin sees all)"""
    
    if current_user.role == "admin":
        batches = db.query(Batch).all()
    else:
        batches = db.query(Batch).filter(Batch.farmer_id == current_user.id).all()
    
    if not batches:
        return {"message": "No batches found"}
    
    # Quality distribution
    grade_counts = {'A': 0, 'B': 0, 'C': 0}
    quality_scores = []
    
    for batch in batches:
        grade_counts[batch.grade] += 1
        quality_scores.append(batch.quality_score)
    
    # Calculate insights
    total_batches = len(batches)
    grade_distribution = {
        grade: (count / total_batches) * 100 for grade, count in grade_counts.items()
    }
    
    avg_quality = sum(quality_scores) / len(quality_scores)
    quality_trend = "improving" if len(quality_scores) > 1 and quality_scores[-1] > quality_scores[0] else "stable"
    
    # Feature importance from AI model
    feature_importance = quality_grader.get_feature_importance()
    
    return {
        "total_batches": total_batches,
        "grade_distribution": grade_distribution,
        "average_quality_score": avg_quality,
        "quality_trend": quality_trend,
        "feature_importance": feature_importance,
        "recommendations": [
            "Focus on reducing moisture content to improve grade",
            "Maintain consistent color scores for better quality",
            "Monitor defect rates closely"
        ]
    }

@router.put("/batches/{batch_id}/status")
async def update_batch_status(
    batch_id: int,
    new_status: str,
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db)
):
    """Update batch status"""
    
    valid_statuses = ["CREATED", "QUALITY_CHECKED", "DISPATCHED", "IN_TRANSIT", "RECEIVED", "SOLD"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    batch = db.query(Batch).filter(
        Batch.id == batch_id,
        Batch.farmer_id == current_user.id
    ).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Update status
    batch.status = new_status
    batch.updated_at = datetime.utcnow()
    
    # Record blockchain event
    blockchain_data = {
        "event_type": new_status,
        "batch_code": batch.batch_code,
        "actor_name": current_user.name,
        "actor_role": "farmer",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    block = blockchain_manager.add_supply_chain_event(blockchain_data)
    
    # Create supply chain event
    supply_event = SupplyChainEvent(
        batch_id=batch.id,
        event_type=new_status,
        actor_name=current_user.name,
        actor_role="farmer",
        location=current_user.location or "Farm Location",
        notes=f"Status updated to {new_status}",
        blockchain_block_index=block.index
    )
    
    db.add(supply_event)
    db.commit()
    
    return {"message": f"Batch {batch.batch_code} status updated to {new_status}"}
