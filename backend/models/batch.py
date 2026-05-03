"""
Organic Roots Batch Model
Represents individual batches of agricultural products
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String(50), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    harvest_date = Column(DateTime(timezone=True), nullable=False)
    
    # Quality attributes
    moisture_level = Column(Float, nullable=False)  # 0-100
    color_score = Column(Float, nullable=False)  # 0-10
    aroma_score = Column(Float, nullable=False)  # 0-10
    defect_percentage = Column(Float, nullable=False)  # 0-100
    weight_per_unit = Column(Float, nullable=False)  # grams
    
    # AI grading results
    grade = Column(String(1), nullable=False)  # A/B/C
    quality_score = Column(Float, nullable=False)  # 0-100
    
    # Pricing
    price_per_kg = Column(Float, nullable=True)  # Calculated based on grade
    
    # QR and blockchain
    qr_code_path = Column(String(200), nullable=True)
    blockchain_block_index = Column(Integer, nullable=True)
    
    # Status and timestamps
    status = Column(String(20), default="CREATED")  # CREATED/QUALITY_CHECKED/DISPATCHED/IN_TRANSIT/RECEIVED/SOLD
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="batches")
    farmer = relationship("User", back_populates="batches")
    supply_chain_events = relationship("SupplyChainEvent", back_populates="batch")
    
    def __repr__(self):
        return f"<Batch(id={self.id}, batch_code={self.batch_code}, grade={self.grade})>"
    
    def to_dict(self):
        """Convert batch object to dictionary"""
        return {
            "id": self.id,
            "batch_code": self.batch_code,
            "product_id": self.product_id,
            "farmer_id": self.farmer_id,
            "quantity_kg": self.quantity_kg,
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "moisture_level": self.moisture_level,
            "color_score": self.color_score,
            "aroma_score": self.aroma_score,
            "defect_percentage": self.defect_percentage,
            "weight_per_unit": self.weight_per_unit,
            "grade": self.grade,
            "quality_score": self.quality_score,
            "price_per_kg": self.price_per_kg,
            "qr_code_path": self.qr_code_path,
            "blockchain_block_index": self.blockchain_block_index,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
