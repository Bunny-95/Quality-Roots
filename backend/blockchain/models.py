"""
Organic Roots Blockchain Block Model
Represents blocks in simulated blockchain
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class BlockchainBlock(Base):
    __tablename__ = "blockchain_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    index = Column(Integer, unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    data_json = Column(Text, nullable=False)  # JSON string of block data
    previous_hash = Column(String(64), nullable=False)
    hash = Column(String(64), unique=True, nullable=False, index=True)
    nonce = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<BlockchainBlock(index={self.index}, hash={self.hash[:8]}...)"
    
    def to_dict(self):
        """Convert blockchain block object to dictionary"""
        return {
            "id": self.id,
            "index": self.index,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "data_json": self.data_json,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }
    
    def to_simple_dict(self):
        """Convert to simplified dictionary for API responses"""
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "data": self.data_json,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }
