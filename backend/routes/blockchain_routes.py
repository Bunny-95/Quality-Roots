"""
Organic Roots Blockchain Routes
API endpoints for blockchain operations and verification
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.batch import Batch
from models.supply_chain import SupplyChainEvent
from blockchain.chain import blockchain_manager

from blockchain.models import BlockchainBlock

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

# Pydantic models
class BlockResponse(BaseModel):
    index: int
    timestamp: str
    data: Dict[str, Any]
    previous_hash: str
    hash: str
    nonce: int

class ChainResponse(BaseModel):
    chain: List[BlockResponse]
    length: int
    last_verified: str

class VerificationResponse(BaseModel):
    is_valid: bool
    chain_length: int
    verified_at: str
    message: str
    invalid_blocks: List[int] = []

@router.get("/chain", response_model=ChainResponse)
async def get_blockchain(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get the complete blockchain"""
    
    try:
        chain = blockchain_manager.get_chain()
        
        # Apply pagination
        paginated_chain = chain[offset:offset + limit]
        
        # Convert to response format
        blocks = []
        for block_data in paginated_chain:
            blocks.append(BlockResponse(
                index=block_data["index"],
                timestamp=block_data["timestamp"],
                data=block_data["data"],
                previous_hash=block_data["previous_hash"],
                hash=block_data["hash"],
                nonce=block_data["nonce"]
            ))
        
        return ChainResponse(
            chain=blocks,
            length=len(chain),
            last_verified=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blockchain: {str(e)}"
        )

@router.get("/blocks")
async def get_blocks(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get blockchain blocks with pagination - returns DB blocks"""
    
    try:
        blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.index).offset(offset).limit(limit).all()
        total = db.query(BlockchainBlock).count()
        
        return {
            "blocks": [
                {
                    "index": block.index,
                    "timestamp": block.timestamp.isoformat() if block.timestamp else None,
                    "data": block.data_json,
                    "previous_hash": block.previous_hash,
                    "hash": block.hash,
                    "nonce": block.nonce
                }
                for block in blocks
            ],
            "total": total,
            "offset": offset,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blocks: {str(e)}"
        )

@router.get("/transactions")
async def get_transactions(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get blockchain blocks as transactions with pagination"""
    
    try:
        blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.index.desc()).offset(offset).limit(limit).all()
        total = db.query(BlockchainBlock).count()
        
        return {
            "transactions": [
                {
                    "id": b.id,
                    "index": b.index,
                    "hash": b.hash,
                    "previous_hash": b.previous_hash,
                    "timestamp": b.timestamp.isoformat() if b.timestamp else None,
                    "data": b.data_json,
                    "nonce": b.nonce
                }
                for b in blocks
            ],
            "total": total,
            "offset": offset,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transactions: {str(e)}"
        )

@router.get("/block/{index}", response_model=BlockResponse)
async def get_block_by_index(
    index: int,
    db: Session = Depends(get_db)
):
    """Get a specific block by index"""
    
    try:
        block = blockchain_manager.get_block(index)
        
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Block {index} not found"
            )
        
        return BlockResponse(
            index=block["index"],
            timestamp=block["timestamp"],
            data=block["data"],
            previous_hash=block["previous_hash"],
            hash=block["hash"],
            nonce=block["nonce"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving block: {str(e)}"
        )

@router.get("/verify", response_model=VerificationResponse)
async def verify_blockchain(
    db: Session = Depends(get_db)
):
    """Verify the integrity of the entire blockchain"""
    
    try:
        verification = blockchain_manager.verify_chain()
        
        return VerificationResponse(
            is_valid=verification["is_valid"],
            chain_length=verification["chain_length"],
            verified_at=verification["verified_at"],
            message=verification["message"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying blockchain: {str(e)}"
        )

@router.get("/stats")
async def get_blockchain_stats(
    db: Session = Depends(get_db)
):
    """Get blockchain statistics"""
    
    try:
        stats = blockchain_manager.get_chain_stats()
        
        # Add additional statistics
        chain = blockchain_manager.get_chain()
        
        # Calculate average block time
        if len(chain) > 1:
            time_diffs = []
            for i in range(1, len(chain)):
                try:
                    prev_time = datetime.fromisoformat(chain[i-1]["timestamp"].replace('Z', '+00:00'))
                    curr_time = datetime.fromisoformat(chain[i]["timestamp"].replace('Z', '+00:00'))
                    time_diffs.append((curr_time - prev_time).total_seconds())
                except:
                    continue
            
            avg_block_time = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        else:
            avg_block_time = 0
        
        # Count event types
        event_types = {}
        for block in chain:
            try:
                event_type = block["data"].get("event_type", "UNKNOWN")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            except:
                continue
        
        return {
            **stats,
            "average_block_time_seconds": avg_block_time,
            "event_distribution": event_types,
            "total_events": len(chain)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting blockchain stats: {str(e)}"
        )

@router.get("/batch/{batch_code}")
async def get_batch_blockchain(
    batch_code: str,
    db: Session = Depends(get_db)
):
    """Get all blockchain records for a specific batch"""
    
    # Find batch
    batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get all supply chain events for this batch
    events = db.query(SupplyChainEvent).filter(
        SupplyChainEvent.batch_id == batch.id,
        SupplyChainEvent.blockchain_block_index.isnot(None)
    ).order_by(SupplyChainEvent.timestamp).all()
    
    # Get corresponding blockchain blocks
    batch_blocks = []
    for event in events:
        try:
            block = blockchain_manager.get_block(event.blockchain_block_index)
            if block:
                batch_blocks.append({
                    **block,
                    "event_type": event.event_type,
                    "event_timestamp": event.timestamp.isoformat(),
                    "actor_name": event.actor_name,
                    "location": event.location
                })
        except:
            continue
    
    return {
        "batch_code": batch_code,
        "total_blocks": len(batch_blocks),
        "blocks": batch_blocks,
        "blockchain_verified": blockchain_manager.verify_chain()["is_valid"]
    }

@router.get("/search")
async def search_blockchain(
    query: str = None,
    event_type: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search blockchain blocks by content"""
    
    try:
        chain = blockchain_manager.get_chain()
        
        filtered_blocks = []
        
        for block in chain:
            include_block = True
            
            # Filter by query
            if query:
                block_data_str = str(block["data"]).lower()
                if query.lower() not in block_data_str:
                    include_block = False
            
            # Filter by event type
            if event_type:
                block_event_type = block["data"].get("event_type", "")
                if event_type != block_event_type:
                    include_block = False
            
            if include_block:
                filtered_blocks.append(block)
        
        # Apply limit
        limited_blocks = filtered_blocks[:limit]
        
        return {
            "query": query,
            "event_type": event_type,
            "total_found": len(filtered_blocks),
            "results": limited_blocks
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching blockchain: {str(e)}"
        )

@router.get("/events")
async def get_blockchain_events(
    event_type: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get blockchain events with optional filtering"""
    
    try:
        chain = blockchain_manager.get_chain()
        
        # Filter by event type
        if event_type:
            filtered_chain = [
                block for block in chain 
                if block["data"].get("event_type") == event_type
            ]
        else:
            filtered_chain = chain
        
        # Apply pagination
        paginated_chain = filtered_chain[offset:offset + limit]
        
        # Enhance with additional information
        enhanced_blocks = []
        for block in paginated_chain:
            enhanced_block = block.copy()
            
            # Add batch information if available
            batch_code = block["data"].get("batch_code")
            if batch_code:
                batch = db.query(Batch).filter(Batch.batch_code == batch_code).first()
                if batch:
                    enhanced_block["batch_info"] = {
                        "product_name": batch.product.name if batch.product else "Unknown",
                        "grade": batch.grade,
                        "quality_score": batch.quality_score
                    }
            
            enhanced_blocks.append(enhanced_block)
        
        return {
            "event_type": event_type,
            "total_events": len(filtered_chain),
            "events": enhanced_blocks
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting blockchain events: {str(e)}"
        )

@router.get("/recent")
async def get_recent_blocks(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most recent blockchain blocks"""
    
    try:
        chain = blockchain_manager.get_chain()
        
        # Get recent blocks (in reverse order)
        recent_blocks = chain[-limit:] if len(chain) > limit else chain
        recent_blocks.reverse()  # Most recent first
        
        return {
            "recent_blocks": recent_blocks,
            "total_shown": len(recent_blocks)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recent blocks: {str(e)}"
        )

@router.get("/health")
async def blockchain_health_check(
    db: Session = Depends(get_db)
):
    """Check blockchain health and status"""
    
    try:
        # Get basic stats
        stats = blockchain_manager.get_chain_stats()
        
        # Verify integrity
        verification = blockchain_manager.verify_chain()
        
        # Check for issues
        issues = []
        
        if not verification["is_valid"]:
            issues.append("Blockchain integrity verification failed")
        
        if stats["chain_length"] == 0:
            issues.append("Blockchain is empty")
        
        # Check for orphaned events (events without blockchain records)
        orphaned_events = db.query(SupplyChainEvent).filter(
            SupplyChainEvent.blockchain_block_index.is_(None)
        ).count()
        
        if orphaned_events > 0:
            issues.append(f"Found {orphaned_events} events without blockchain records")
        
        health_status = "healthy" if not issues else "unhealthy"
        
        return {
            "status": health_status,
            "issues": issues,
            "stats": stats,
            "verification": verification,
            "orphaned_events": orphaned_events,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "issues": [f"Health check failed: {str(e)}"],
            "checked_at": datetime.utcnow().isoformat()
        }

@router.post("/rebuild")
async def rebuild_blockchain(
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """Rebuild blockchain from supply chain events (admin operation)"""
    
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This operation requires confirmation. Set confirm=true to proceed."
        )
    
    try:
        # This would be a complex operation to rebuild the blockchain
        # For now, return a placeholder response
        
        return {
            "message": "Blockchain rebuild operation initiated",
            "status": "processing",
            "note": "This is a placeholder implementation"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rebuilding blockchain: {str(e)}"
        )
