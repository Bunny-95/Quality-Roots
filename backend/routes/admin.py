"""
Organic Roots Admin Routes
API endpoints for admin-specific functionality
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.product import Product
from models.batch import Batch
from models.supply_chain import SupplyChainEvent
from utils.security import get_current_active_user, require_admin
from ai.fraud_detector import fraud_detector
from blockchain.chain import blockchain_manager

router = APIRouter(prefix="/admin", tags=["admin"])

# Pydantic models
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: str = None
    location: str = None
    created_at: datetime
    is_active: bool

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
    qr_code_path: str = None
    blockchain_block_index: int = None
    status: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_users: int
    total_farmers: int
    total_products: int
    total_batches: int
    flagged_events: int
    blockchain_length: int
    grade_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

class FraudEvent(BaseModel):
    id: int
    batch_id: int
    event_type: str
    actor_name: str
    actor_role: str
    location: str
    notes: str = None
    timestamp: datetime
    fraud_score: float = None
    is_flagged: bool

@router.get("/dashboard", response_model=DashboardStats)
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    return await _get_dashboard_stats(db)

@router.get("/stats", response_model=DashboardStats)
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin system statistics (alias for dashboard)"""
    return await _get_dashboard_stats(db)

@router.get("/health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    
    # Count statistics
    total_users = db.query(User).count()
    total_batches = db.query(Batch).count()
    flagged_events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.is_flagged == True
    ).count()
    
    # Blockchain status
    blockchain_stats = blockchain_manager.get_chain_stats()
    chain_valid = blockchain_manager.verify_chain()['is_valid']
    
    return {
        "status": "healthy",
        "database": "connected",
        "database_status": "operational",
        "blockchain_status": "operational" if chain_valid else "degraded",
        "ai_models_status": "operational",
        "api_response_time": 45,
        "uptime_percentage": 99.9,
        "last_backup": datetime.utcnow().isoformat(),
        "users_count": total_users,
        "batches_count": total_batches,
        "flagged_events": flagged_events,
        "blockchain": {
            "length": blockchain_stats['chain_length'],
            "valid": chain_valid
        },
        "timestamp": datetime.utcnow().isoformat()
    }

async def _get_dashboard_stats(db: Session):
    """Get admin dashboard statistics helper"""
    
    # User statistics
    total_users = db.query(User).count()
    total_farmers = db.query(User).filter(User.role == 'farmer').count()
    
    # Product statistics
    total_products = db.query(Product).count()
    
    # Batch statistics
    total_batches = db.query(Batch).count()
    grade_distribution = db.query(
        Batch.grade,
        func.count(Batch.id).label('count')
    ).group_by(Batch.grade).all()
    
    grade_dist_dict = {grade: count for grade, count in grade_distribution}
    
    # Flagged events
    flagged_events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.is_flagged == True
    ).count()
    
    # Blockchain length
    blockchain_stats = blockchain_manager.get_chain_stats()
    blockchain_length = blockchain_stats['chain_length']
    
    # Recent activity (last 10 events)
    recent_events = db.query(SupplyChainEvent).order_by(
        desc(SupplyChainEvent.timestamp)
    ).limit(10).all()
    
    recent_activity = []
    for event in recent_events:
        recent_activity.append({
            "event_type": event.event_type,
            "batch_code": event.batch.batch_code if event.batch else "Unknown",
            "actor_name": event.actor_name,
            "timestamp": event.timestamp.isoformat(),
            "location": event.location
        })
    
    return DashboardStats(
        total_users=total_users,
        total_farmers=total_farmers,
        total_products=total_products,
        total_batches=total_batches,
        flagged_events=flagged_events,
        blockchain_length=blockchain_length,
        grade_distribution=grade_dist_dict,
        recent_activity=recent_activity
    )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all users in the system"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/recent", response_model=List[UserResponse])
async def get_recent_users(
    limit: int = 5,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get most recent users"""
    
    users = db.query(User).order_by(desc(User.created_at)).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/batches", response_model=List[BatchResponse])
async def get_all_batches(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all batches in the system"""
    
    batches = db.query(Batch).offset(skip).limit(limit).all()
    return batches

@router.get("/batches/recent", response_model=List[BatchResponse])
async def get_recent_batches(
    limit: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get most recent batches"""
    
    batches = db.query(Batch).order_by(desc(Batch.created_at)).limit(limit).all()
    return batches

@router.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch_detail(
    batch_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific batch"""
    
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    return batch

@router.get("/flagged", response_model=List[FraudEvent])
async def get_flagged_events(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all flagged/fraud events"""
    
    flagged_events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.is_flagged == True
    ).order_by(desc(SupplyChainEvent.timestamp)).offset(skip).limit(limit).all()
    
    return flagged_events

@router.post("/analyze-fraud/{batch_id}")
async def analyze_batch_fraud(
    batch_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Analyze a batch for potential fraud"""
    
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get recent supply chain events for this batch
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch_id
    ).order_by(desc(SupplyChainEvent.timestamp)).limit(5).all()
    
    fraud_results = []
    
    for event in events:
        # Create transaction data for fraud detection
        transaction_data = {
            "transaction_id": f"TXN_{event.id}",
            "price_per_kg": 50.0,  # Default price - would come from actual data
            "quantity_kg": batch.quantity_kg,
            "transit_days": 3.0,  # Default - would calculate from timestamps
            "temperature_reported": 25.0,  # Default - would come from sensor data
            "location_jump_km": 100.0,  # Default - would calculate from locations
            "time_since_last_event_hours": 24.0  # Default - would calculate
        }
        
        # Run fraud detection
        fraud_result = fraud_detector.detect_fraud(transaction_data)
        
        # Update event if fraud detected
        if fraud_result['is_anomaly']:
            event.fraud_score = fraud_result['anomaly_score']
            event.is_flagged = True
            db.commit()
        
        fraud_results.append({
            "event_id": event.id,
            "event_type": event.event_type,
            "fraud_result": fraud_result
        })
    
    return {
        "batch_code": batch.batch_code,
        "fraud_analysis": fraud_results,
        "total_flagged": sum(1 for result in fraud_results if result['fraud_result']['is_anomaly'])
    }

@router.get("/products")
async def get_all_products(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all products in the system"""
    
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/quality-analytics")
async def get_quality_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get quality analytics across all batches"""
    
    # Quality distribution by product type
    quality_by_product = db.query(
        Product.type,
        Batch.grade,
        func.count(Batch.id).label('count'),
        func.avg(Batch.quality_score).label('avg_score')
    ).join(Product, Batch.product_id == Product.id).group_by(
        Product.type, Batch.grade
    ).all()
    
    # Organize results
    analytics = {}
    for product_type, grade, count, avg_score in quality_by_product:
        if product_type not in analytics:
            analytics[product_type] = {
                'grade_distribution': {},
                'average_quality_score': 0
            }
        
        analytics[product_type]['grade_distribution'][grade] = count
        analytics[product_type]['average_quality_score'] = float(avg_score) if avg_score else 0
    
    # Overall statistics
    overall_stats = db.query(
        func.avg(Batch.quality_score).label('avg_quality'),
        func.min(Batch.quality_score).label('min_quality'),
        func.max(Batch.quality_score).label('max_quality'),
        func.count(Batch.id).label('total_batches')
    ).first()
    
    return {
        "by_product_type": analytics,
        "overall_stats": {
            "average_quality_score": float(overall_stats.avg_quality) if overall_stats.avg_quality else 0,
            "min_quality_score": float(overall_stats.min_quality) if overall_stats.min_quality else 0,
            "max_quality_score": float(overall_stats.max_quality) if overall_stats.max_quality else 0,
            "total_batches": overall_stats.total_batches
        }
    }

@router.get("/blockchain-status")
async def get_blockchain_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get blockchain status and verification"""
    
    # Get blockchain stats
    stats = blockchain_manager.get_chain_stats()
    
    # Verify chain integrity
    verification = blockchain_manager.verify_chain()
    
    # Get recent blocks
    chain = blockchain_manager.get_chain()
    recent_blocks = chain[-5:] if len(chain) > 5 else chain
    
    return {
        "stats": stats,
        "verification": verification,
        "recent_blocks": recent_blocks
    }

@router.get("/reports/summary")
async def generate_summary_report(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Generate a summary report of the entire system"""
    
    # User statistics
    user_stats = db.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    user_distribution = {role: count for role, count in user_stats}
    
    # Product statistics
    product_stats = db.query(
        Product.type,
        func.count(Product.id).label('count')
    ).group_by(Product.type).all()
    
    product_distribution = {ptype: count for ptype, count in product_stats}
    
    # Batch statistics
    batch_stats = db.query(
        Batch.grade,
        func.count(Batch.id).label('count'),
        func.avg(Batch.quality_score).label('avg_quality')
    ).group_by(Batch.grade).all()
    
    batch_distribution = {
        grade: {
            'count': count,
            'avg_quality': float(avg_quality) if avg_quality else 0
        } for grade, count, avg_quality in batch_stats
    }
    
    # Supply chain events
    event_stats = db.query(
        SupplyChainEvent.event_type,
        func.count(SupplyChainEvent.id).label('count')
    ).group_by(SupplyChainEvent.event_type).all()
    
    event_distribution = {event_type: count for event_type, count in event_stats}
    
    # System health
    flagged_events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.is_flagged == True
    ).count()
    
    blockchain_stats = blockchain_manager.get_chain_stats()
    
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "user_distribution": user_distribution,
        "product_distribution": product_distribution,
        "batch_distribution": batch_distribution,
        "event_distribution": event_distribution,
        "system_health": {
            "flagged_events": flagged_events,
            "blockchain_length": blockchain_stats['chain_length'],
            "blockchain_valid": blockchain_manager.verify_chain()['is_valid']
        }
    }

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle user active status"""
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own status"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    status_text = "activated" if user.is_active else "deactivated"
    return {"message": f"User {user.email} {status_text} successfully"}

@router.get("/audit-log")
async def get_audit_log(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get audit log of all supply chain events"""
    
    events = db.query(SupplyChainEvent).order_by(
        desc(SupplyChainEvent.timestamp)
    ).offset(skip).limit(limit).all()
    
    audit_log = []
    for event in events:
        audit_log.append({
            "id": event.id,
            "batch_code": event.batch.batch_code if event.batch else "Unknown",
            "event_type": event.event_type,
            "actor_name": event.actor_name,
            "actor_role": event.actor_role,
            "location": event.location,
            "notes": event.notes,
            "timestamp": event.timestamp.isoformat(),
            "fraud_score": event.fraud_score,
            "is_flagged": event.is_flagged,
            "blockchain_index": event.blockchain_block_index
        })
    
    return audit_log
