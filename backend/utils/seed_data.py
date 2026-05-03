"""
Organic Roots Seed Data Generator
Generates realistic demo data for testing and development
"""
import sys
import os
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db
from models.user import User
from models.product import Product
from models.batch import Batch
from models.supply_chain import SupplyChainEvent
from utils.security import get_password_hash
from blockchain.chain import blockchain_manager
from ai.quality_grader import quality_grader
from utils.qr_generator import qr_generator

def run_seed():
    """Run seed data generation if database is empty"""
    print("🌱 Checking if seed data is needed...")
    
    db = next(get_db())
    
    try:
        # Check if users exist
        user_count = db.query(User).count()
        
        if user_count > 0:
            print("✅ Database already contains data, skipping seed generation")
            return
        
        print("📋 Database is empty, generating seed data...")
        
        # Create users
        create_users(db)
        
        # Create products
        create_products(db)
        
        # Create batches
        create_batches(db)
        
        # Create supply chain events
        create_supply_chain_events(db)
        
        print("✅ Seed data generation completed!")
        
    except Exception as e:
        print(f"❌ Error generating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_users(db):
    """Create seed users"""
    print("   👥 Creating users...")
    
    users = [
        {
            "name": "Ravi Kumar",
            "email": "ravi.kumar@organicroots.com",
            "password": "farmer123",
            "role": "farmer",
            "phone": "+91-9876543210",
            "location": "Karnataka"
        },
        {
            "name": "Priya Nair",
            "email": "priya.nair@organicroots.com",
            "password": "farmer123",
            "role": "farmer",
            "phone": "+91-9876543211",
            "location": "Kerala"
        },
        {
            "name": "Arjun Patel",
            "email": "arjun.patel@organicroots.com",
            "password": "farmer123",
            "role": "farmer",
            "phone": "+91-9876543212",
            "location": "Gujarat"
        },
        {
            "name": "Admin User",
            "email": "admin@organicroots.com",
            "password": "admin123",
            "role": "admin",
            "phone": "+91-9876543200",
            "location": "Mumbai"
        }
    ]
    
    for user_data in users:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            role=user_data["role"],
            phone=user_data["phone"],
            location=user_data["location"],
            is_active=True
        )
        db.add(user)
    
    db.commit()
    print(f"   ✅ Created {len(users)} users")

def create_products(db):
    """Create seed products"""
    print("   🌾 Creating products...")
    
    # Get farmers
    farmers = db.query(User).filter(User.role == "farmer").all()
    
    products = [
        {
            "name": "Coorg Coffee",
            "type": "coffee",
            "description": "Premium Arabica coffee from Coorg region",
            "origin_state": "Karnataka",
            "farmer": farmers[0]  # Ravi Kumar
        },
        {
            "name": "Kerala Black Pepper",
            "type": "spice",
            "description": "High quality black pepper from Kerala",
            "origin_state": "Kerala",
            "farmer": farmers[1]  # Priya Nair
        },
        {
            "name": "Assam Green Tea",
            "type": "tea",
            "description": "Organic green tea from Assam gardens",
            "origin_state": "Assam",
            "farmer": farmers[2]  # Arjun Patel
        },
        {
            "name": "Rajasthan Bajra",
            "type": "millet",
            "description": "Traditional pearl millet from Rajasthan",
            "origin_state": "Rajasthan",
            "farmer": farmers[2]  # Arjun Patel
        },
        {
            "name": "Organic Turmeric",
            "type": "organic",
            "description": "Certified organic turmeric with high curcumin",
            "origin_state": "Karnataka",
            "farmer": farmers[0]  # Ravi Kumar
        }
    ]
    
    for product_data in products:
        product = Product(
            name=product_data["name"],
            type=product_data["type"],
            description=product_data["description"],
            origin_state=product_data["origin_state"],
            farmer_id=product_data["farmer"].id
        )
        db.add(product)
    
    db.commit()
    print(f"   ✅ Created {len(products)} products")

def create_batches(db):
    """Create seed batches"""
    print("   📦 Creating batches...")
    
    products = db.query(Product).all()
    
    batches = []
    batch_counter = 1
    
    for product in products:
        # Create 2 batches per product
        for i in range(2):
            # Generate realistic quality attributes based on product type
            if product.type == "coffee":
                moisture = random.uniform(10, 13)
                color = random.uniform(7, 9)
                aroma = random.uniform(7.5, 9.5)
                defects = random.uniform(1, 5)
                weight = random.uniform(180, 220)
            elif product.type == "spice":
                moisture = random.uniform(8, 12)
                color = random.uniform(6, 8)
                aroma = random.uniform(7, 9)
                defects = random.uniform(2, 6)
                weight = random.uniform(45, 55)
            elif product.type == "tea":
                moisture = random.uniform(6, 10)
                color = random.uniform(6, 8)
                aroma = random.uniform(6, 8)
                defects = random.uniform(3, 7)
                weight = random.uniform(90, 110)
            elif product.type == "millet":
                moisture = random.uniform(11, 14)
                color = random.uniform(5, 7)
                aroma = random.uniform(5, 7)
                defects = random.uniform(4, 8)
                weight = random.uniform(25, 35)
            else:  # organic
                moisture = random.uniform(9, 12)
                color = random.uniform(7, 9)
                aroma = random.uniform(7, 8.5)
                defects = random.uniform(1, 4)
                weight = random.uniform(140, 160)
            
            # Generate batch code
            batch_code = f"{product.type.upper()}{datetime.now().strftime('%Y%m%d')}{batch_counter:03d}"
            batch_counter += 1
            
            # AI quality grading
            grading_input = {
                "batch_code": batch_code,
                "product_type": product.type,
                "moisture_level": moisture,
                "color_score": color,
                "aroma_score": aroma,
                "defect_percentage": defects,
                "weight_per_unit": weight
            }
            
            grade_result = quality_grader.grade_batch(grading_input)
            
            # Create batch
            batch = Batch(
                batch_code=batch_code,
                product_id=product.id,
                farmer_id=product.farmer_id,
                quantity_kg=random.uniform(50, 200),
                harvest_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                moisture_level=moisture,
                color_score=color,
                aroma_score=aroma,
                defect_percentage=defects,
                weight_per_unit=weight,
                grade=grade_result['grade'],
                quality_score=grade_result['quality_score'],
                status="CREATED"
            )
            
            db.add(batch)
            batches.append(batch)
    
    db.commit()
    
    # Generate QR codes for all batches
    for batch in batches:
        qr_result = qr_generator.create_qr_code(batch.batch_code)
        batch.qr_code_path = qr_result['relative_path']
        
        # Record blockchain event
        blockchain_data = {
            "event_type": "BATCH_CREATED",
            "batch_code": batch.batch_code,
            "product_id": batch.product_id,
            "farmer_id": batch.farmer_id,
            "quantity_kg": batch.quantity_kg,
            "grade": batch.grade,
            "quality_score": batch.quality_score,
            "ai_confidence": grade_result['confidence'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        block = blockchain_manager.add_supply_chain_event(blockchain_data)
        batch.blockchain_block_index = block.index
    
    db.commit()
    print(f"   ✅ Created {len(batches)} batches with QR codes")

def create_supply_chain_events(db):
    """Create seed supply chain events"""
    print("   🔗 Creating supply chain events...")
    
    batches = db.query(Batch).all()
    
    event_types = [
        "QUALITY_CHECKED",
        "DISPATCHED", 
        "IN_TRANSIT",
        "RECEIVED_DISTRIBUTOR",
        "RECEIVED_RETAILER",
        "SOLD"
    ]
    
    actors = [
        {"name": "Quality Inspector", "role": "admin"},
        {"name": "Logistics Coordinator", "role": "distributor"},
        {"name": "Transport Manager", "role": "distributor"},
        {"name": "Warehouse Manager", "role": "distributor"},
        {"name": "Retail Store Manager", "role": "retailer"},
        {"name": "End Consumer", "role": "consumer"}
    ]
    
    locations = [
        "Quality Lab, Bangalore",
        "Distribution Center, Mumbai",
        "Transit Hub, Pune",
        "Warehouse, Delhi",
        "Retail Store, Chennai",
        "Customer Address, Kolkata"
    ]
    
    total_events = 0
    
    for batch in batches:
        # Create events for each batch
        for i, event_type in enumerate(event_types):
            # Add some randomness - not all batches have complete journey
            if random.random() < 0.8:  # 80% chance to have this event
                event = SupplyChainEvent(
                    batch_id=batch.id,
                    event_type=event_type,
                    actor_name=actors[i]["name"],
                    actor_role=actors[i]["role"],
                    location=locations[i],
                    notes=f"Standard {event_type.lower()} processing",
                    timestamp=datetime.now() - timedelta(days=random.randint(1, 20), hours=random.randint(1, 23))
                )
                
                db.add(event)
                total_events += 1
    
    db.commit()
    print(f"   ✅ Created {total_events} supply chain events")

if __name__ == "__main__":
    run_seed()
