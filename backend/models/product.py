"""
Organic Roots Product Model
Represents agricultural products that farmers can register
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # spice/coffee/tea/millet/organic
    description = Column(String(500), nullable=True)
    origin_state = Column(String(100), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    farmer = relationship("User", back_populates="products")
    batches = relationship("Batch", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, type={self.type})>"
    
    def to_dict(self):
        """Convert product object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "origin_state": self.origin_state,
            "farmer_id": self.farmer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
