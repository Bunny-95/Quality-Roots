"""
Test script to verify database setup and model creation
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import create_tables, reset_database, get_db
from models.user import User
from models.product import Product
from models.batch import Batch
from models.supply_chain import SupplyChainEvent
from blockchain.models import BlockchainBlock

def test_database_setup():
    """Test database creation and basic operations"""
    print("🧪 Testing database setup...")
    
    try:
        # Reset database (drop and recreate)
        reset_database()
        
        # Get database session
        db = next(get_db())
        
        # Test creating a user
        print("✅ Creating test user...")
        test_user = User(
            name="Test Farmer",
            email="test@organicroots.com",
            password_hash="hashed_password",
            role="farmer",
            phone="1234567890",
            location="Test State"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"   Created user: {test_user}")
        
        # Test creating a product
        print("✅ Creating test product...")
        test_product = Product(
            name="Test Coffee",
            type="coffee",
            description="Premium test coffee beans",
            origin_state="Test State",
            farmer_id=test_user.id
        )
        db.add(test_product)
        db.commit()
        db.refresh(test_product)
        print(f"   Created product: {test_product}")
        
        # Test creating a batch
        print("✅ Creating test batch...")
        from datetime import datetime
        test_batch = Batch(
            batch_code="TEST001",
            product_id=test_product.id,
            farmer_id=test_user.id,
            quantity_kg=100.0,
            harvest_date=datetime(2024, 1, 15),
            moisture_level=12.5,
            color_score=8.5,
            aroma_score=9.0,
            defect_percentage=2.0,
            weight_per_unit=500.0,
            grade="A",
            quality_score=92.0
        )
        db.add(test_batch)
        db.commit()
        db.refresh(test_batch)
        print(f"   Created batch: {test_batch}")
        
        # Test creating a supply chain event
        print("✅ Creating test supply chain event...")
        test_event = SupplyChainEvent(
            batch_id=test_batch.id,
            event_type="CREATED",
            actor_name="Test Farmer",
            actor_role="farmer",
            location="Test Farm",
            notes="Initial batch creation"
        )
        db.add(test_event)
        db.commit()
        db.refresh(test_event)
        print(f"   Created event: {test_event}")
        
        # Test creating a blockchain block
        print("✅ Creating test blockchain block...")
        test_block = BlockchainBlock(
            index=0,
            data_json='{"test": "data"}',
            previous_hash="0",
            hash="test_hash",
            nonce=12345
        )
        db.add(test_block)
        db.commit()
        db.refresh(test_block)
        print(f"   Created block: {test_block}")
        
        print("\n🎉 All database tests passed!")
        print(f"   Users: {db.query(User).count()}")
        print(f"   Products: {db.query(Product).count()}")
        print(f"   Batches: {db.query(Batch).count()}")
        print(f"   Events: {db.query(SupplyChainEvent).count()}")
        print(f"   Blocks: {db.query(BlockchainBlock).count()}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        raise

if __name__ == "__main__":
    test_database_setup()
