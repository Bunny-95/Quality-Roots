"""
Organic Roots Supply Chain Routes
API endpoints for supply chain event management
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from database import get_db
from models.batch import Batch
from models.supply_chain import SupplyChainEvent
from models.user import User
from utils.security import get_current_active_user
from ai.fraud_detector import fraud_detector
from blockchain.chain import blockchain_manager

router = APIRouter(prefix="/supply", tags=["supply_chain"])

# Pydantic models
class SupplyChainEventCreate(BaseModel):
    batch_id: int
    event_type: str
    actor_name: str
    actor_role: str
    location: str
    notes: str = None

class SupplyChainEventResponse(BaseModel):
    id: int
    batch_id: int
    event_type: str
    actor_name: str
    actor_role: str
    location: str
    notes: str = None
    timestamp: datetime
    blockchain_block_index: int = None
    fraud_score: float = None
    is_flagged: bool

class BatchTimeline(BaseModel):
    batch_code: str
    product_name: str
    total_events: int
    events: List[SupplyChainEventResponse]

@router.post("/event", response_model=SupplyChainEventResponse, status_code=status.HTTP_201_CREATED)
async def add_supply_chain_event(
    event_data: SupplyChainEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new supply chain event"""
    
    # Validate batch exists
    batch = db.query(Batch).filter(Batch.id == event_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Validate event type
    valid_event_types = [
        "CREATED", "QUALITY_CHECKED", "DISPATCHED", "IN_TRANSIT", 
        "RECEIVED_DISTRIBUTOR", "RECEIVED_RETAILER", "SOLD"
    ]
    if event_data.event_type not in valid_event_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type. Must be one of: {', '.join(valid_event_types)}"
        )
    
    # Validate actor role
    valid_roles = ["farmer", "distributor", "retailer", "consumer", "admin"]
    if event_data.actor_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid actor role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Create supply chain event
    new_event = SupplyChainEvent(
        batch_id=event_data.batch_id,
        event_type=event_data.event_type,
        actor_name=event_data.actor_name,
        actor_role=event_data.actor_role,
        location=event_data.location,
        notes=event_data.notes
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    # Run fraud detection on the event
    try:
        # Create transaction data for fraud detection
        transaction_data = {
            "transaction_id": f"EVENT_{new_event.id}",
            "price_per_kg": 50.0,  # Default price - would come from actual data
            "quantity_kg": batch.quantity_kg,
            "transit_days": 3.0,  # Default - would calculate from timestamps
            "temperature_reported": 25.0,  # Default - would come from sensor data
            "location_jump_km": 100.0,  # Default - would calculate from locations
            "time_since_last_event_hours": 24.0  # Default - would calculate
        }
        
        fraud_result = fraud_detector.detect_fraud(transaction_data)
        
        # Update event with fraud detection results
        if fraud_result['is_anomaly']:
            new_event.fraud_score = fraud_result['anomaly_score']
            new_event.is_flagged = True
            db.commit()
    
    except Exception as e:
        print(f"Fraud detection failed for event {new_event.id}: {e}")
    
    # Record on blockchain
    try:
        blockchain_data = {
            "event_type": event_data.event_type,
            "batch_code": batch.batch_code,
            "batch_id": event_data.batch_id,
            "actor_name": event_data.actor_name,
            "actor_role": event_data.actor_role,
            "location": event_data.location,
            "notes": event_data.notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        block = blockchain_manager.add_supply_chain_event(blockchain_data)
        new_event.blockchain_block_index = block.index
        db.commit()
    
    except Exception as e:
        print(f"Blockchain recording failed for event {new_event.id}: {e}")
    
    db.refresh(new_event)
    return new_event

@router.get("/batch/{batch_code}", response_model=BatchTimeline)
async def get_batch_timeline(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Get complete timeline for a batch"""
    
    # Find batch
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get all supply chain events for this batch
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch.id
    ).order_by(SupplyChainEvent.timestamp).all()
    
    # Convert to response format
    event_responses = []
    for event in events:
        event_responses.append(SupplyChainEventResponse(
            id=event.id,
            batch_id=event.batch_id,
            event_type=event.event_type,
            actor_name=event.actor_name,
            actor_role=event.actor_role,
            location=event.location,
            notes=event.notes,
            timestamp=event.timestamp,
            blockchain_block_index=event.blockchain_block_index,
            fraud_score=event.fraud_score,
            is_flagged=event.is_flagged
        ))
    
    return BatchTimeline(
        batch_code=batch.batch_code,
        product_name=batch.product.name if batch.product else "Unknown",
        total_events=len(event_responses),
        events=event_responses
    )

@router.get("/events")
async def get_supply_chain_events(
    batch_id: Optional[int] = None,
    event_type: Optional[str] = None,
    actor_role: Optional[str] = None,
    is_flagged: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get supply chain events with optional filtering"""
    
    query = db.query(SupplyChainEvent)
    
    # Apply filters
    if batch_id:
        query = query.filter(SupplyChainEvent.batch_id == batch_id)
    
    if event_type:
        query = query.filter(SupplyChainEvent.event_type == event_type)
    
    if actor_role:
        query = query.filter(SupplyChainEvent.actor_role == actor_role)
    
    if is_flagged is not None:
        query = query.filter(SupplyChainEvent.is_flagged == is_flagged)
    
    # Order by timestamp (most recent first)
    events = query.order_by(desc(SupplyChainEvent.timestamp)).offset(skip).limit(limit).all()
    
    # Convert to response format
    event_responses = []
    for event in events:
        event_responses.append(SupplyChainEventResponse(
            id=event.id,
            batch_id=event.batch_id,
            event_type=event.event_type,
            actor_name=event.actor_name,
            actor_role=event.actor_role,
            location=event.location,
            notes=event.notes,
            timestamp=event.timestamp,
            blockchain_block_index=event.blockchain_block_index,
            fraud_score=event.fraud_score,
            is_flagged=event.is_flagged
        ))
    
    return {
        "total_events": len(event_responses),
        "events": event_responses
    }

@router.get("/event/{event_id}", response_model=SupplyChainEventResponse)
async def get_supply_chain_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific supply chain event"""
    
    event = db.query(SupplyChainEvent).filter(SupplyChainEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return SupplyChainEventResponse(
        id=event.id,
        batch_id=event.batch_id,
        event_type=event.event_type,
        actor_name=event.actor_name,
        actor_role=event.actor_role,
        location=event.location,
        notes=event.notes,
        timestamp=event.timestamp,
        blockchain_block_index=event.blockchain_block_index,
        fraud_score=event.fraud_score,
        is_flagged=event.is_flagged
    )

@router.put("/event/{event_id}")
async def update_supply_chain_event(
    event_id: int,
    notes: str = None,
    location: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a supply chain event"""
    
    event = db.query(SupplyChainEvent).filter(SupplyChainEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update fields
    if notes is not None:
        event.notes = notes
    
    if location is not None:
        event.location = location
    
    db.commit()
    db.refresh(event)
    
    return {"message": "Event updated successfully"}

@router.get("/stats")
async def get_supply_chain_stats(
    db: Session = Depends(get_db)
):
    """Get supply chain statistics"""
    
    # Event type distribution
    event_stats = db.query(
        SupplyChainEvent.event_type,
        func.count(SupplyChainEvent.id).label('count')
    ).group_by(SupplyChainEvent.event_type).all()
    
    event_distribution = {event_type: count for event_type, count in event_stats}
    
    # Actor role distribution
    actor_stats = db.query(
        SupplyChainEvent.actor_role,
        func.count(SupplyChainEvent.id).label('count')
    ).group_by(SupplyChainEvent.actor_role).all()
    
    actor_distribution = {role: count for role, count in actor_stats}
    
    # Flagged events
    total_events = db.query(SupplyChainEvent).count()
    flagged_events = db.query(SupplyChainEvent).filter(SupplyChainEvent.is_flagged == True).count()
    
    # Blockchain coverage
    blockchain_events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.blockchain_block_index.isnot(None)
    ).count()
    
    # Recent activity (last 24 hours)
    recent_events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    return {
        "total_events": total_events,
        "flagged_events": flagged_events,
        "blockchain_coverage": blockchain_events,
        "flagged_percentage": (flagged_events / total_events * 100) if total_events > 0 else 0,
        "blockchain_percentage": (blockchain_events / total_events * 100) if total_events > 0 else 0,
        "recent_activity": recent_events,
        "event_distribution": event_distribution,
        "actor_distribution": actor_distribution
    }

@router.get("/flagged-events")
async def get_flagged_events(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all flagged supply chain events"""
    
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.is_flagged == True
    ).order_by(desc(SupplyChainEvent.timestamp)).offset(skip).limit(limit).all()
    
    flagged_events = []
    for event in events:
        flagged_events.append(SupplyChainEventResponse(
            id=event.id,
            batch_id=event.batch_id,
            event_type=event.event_type,
            actor_name=event.actor_name,
            actor_role=event.actor_role,
            location=event.location,
            notes=event.notes,
            timestamp=event.timestamp,
            blockchain_block_index=event.blockchain_block_index,
            fraud_score=event.fraud_score,
            is_flagged=event.is_flagged
        ))
    
    return {
        "total_flagged": len(flagged_events),
        "events": flagged_events
    }

@router.post("/batch/{batch_id}/event")
async def add_batch_event(
    batch_id: int,
    event_type: str,
    actor_name: str,
    actor_role: str,
    location: str,
    notes: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add an event to a specific batch (simplified endpoint)"""
    
    # Validate batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Create event data
    event_data = SupplyChainEventCreate(
        batch_id=batch_id,
        event_type=event_type,
        actor_name=actor_name,
        actor_role=actor_role,
        location=location,
        notes=notes
    )
    
    # Add event using the main endpoint logic
    return await add_supply_chain_event(event_data, current_user, db)

@router.get("/event-types")
async def get_event_types():
    """Get all available event types"""
    
    event_types = [
        "CREATED",
        "QUALITY_CHECKED", 
        "DISPATCHED",
        "IN_TRANSIT",
        "RECEIVED_DISTRIBUTOR",
        "RECEIVED_RETAILER",
        "SOLD"
    ]
    
    return {
        "event_types": event_types,
        "descriptions": {
            "CREATED": "Batch initially created by farmer",
            "QUALITY_CHECKED": "Quality assessment completed",
            "DISPATCHED": "Batch sent from farm",
            "IN_TRANSIT": "Batch currently in transportation",
            "RECEIVED_DISTRIBUTOR": "Batch received by distributor",
            "RECEIVED_RETAILER": "Batch received by retailer",
            "SOLD": "Batch sold to end consumer"
        }
    }

@router.get("/actor-roles")
async def get_actor_roles():
    """Get all available actor roles"""
    
    roles = [
        "farmer",
        "distributor", 
        "retailer",
        "consumer",
        "admin"
    ]
    
    return {
        "actor_roles": roles,
        "descriptions": {
            "farmer": "Primary producer/grower",
            "distributor": "Middle-tier logistics provider",
            "retailer": "Final point of sale",
            "consumer": "End customer",
            "admin": "System administrator"
        }
    }
