"""
Organic Roots Supply Chain Event Model
Tracks events throughout the supply chain journey
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class SupplyChainEvent(Base):
    __tablename__ = "supply_chain_events"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # CREATED/QUALITY_CHECKED/DISPATCHED/IN_TRANSIT/RECEIVED_DISTRIBUTOR/RECEIVED_RETAILER/SOLD
    actor_name = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)  # farmer/distributor/retailer/consumer
    location = Column(String(200), nullable=False)
    notes = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Blockchain and fraud detection
    blockchain_block_index = Column(Integer, nullable=True)
    fraud_score = Column(Float, nullable=True)  # 0-1, higher = more suspicious
    is_flagged = Column(Boolean, default=False)
    
    # Relationships
    batch = relationship("Batch", back_populates="supply_chain_events")
    
    def __repr__(self):
        return f"<SupplyChainEvent(id={self.id}, type={self.event_type}, batch_id={self.batch_id})>"
    
    def to_dict(self):
        """Convert supply chain event object to dictionary"""
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "event_type": self.event_type,
            "actor_name": self.actor_name,
            "actor_role": self.actor_role,
            "location": self.location,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "blockchain_block_index": self.blockchain_block_index,
            "fraud_score": self.fraud_score,
            "is_flagged": self.is_flagged
        }
