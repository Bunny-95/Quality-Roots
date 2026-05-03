"""
Test script to verify authentication system functionality
"""
import sys
import os
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import create_tables, reset_database, get_db
from models.user import User
from utils.security import get_password_hash, verify_password, create_access_token, verify_token

def test_password_hashing():
    """Test password hashing and verification"""
    print("🧪 Testing password hashing...")
    
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    print(f"   Original password: {password}")
    print(f"   Hashed password: {hashed[:50]}...")
    
    # Test verification
    is_correct = verify_password(password, hashed)
    is_wrong = verify_password("WrongPassword", hashed)
    
    assert is_correct, "Password verification should pass"
    assert not is_wrong, "Wrong password verification should fail"
    
    print("✅ Password hashing tests passed!")

def test_jwt_tokens():
    """Test JWT token creation and verification"""
    print("🧪 Testing JWT tokens...")
    
    # Create token
    token_data = {"sub": "1", "email": "test@example.com", "role": "farmer"}
    token = create_access_token(token_data)
    
    print(f"   Created token: {token[:50]}...")
    
    # Verify token
    payload = verify_token(token)
    
    assert payload["sub"] == "1", "Token should contain correct user ID"
    assert payload["email"] == "test@example.com", "Token should contain correct email"
    assert payload["role"] == "farmer", "Token should contain correct role"
    
    print("✅ JWT token tests passed!")

def test_user_creation():
    """Test user creation in database"""
    print("🧪 Testing user creation...")
    
    # Reset database
    reset_database()
    
    # Get database session
    db = next(get_db())
    
    # Create test user
    test_user = User(
        name="Test Farmer",
        email="farmer@organicroots.com",
        password_hash=get_password_hash("FarmerPassword123!"),
        role="farmer",
        phone="1234567890",
        location="Test Farm"
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"   Created user: {test_user}")
    
    # Test user retrieval
    retrieved_user = db.query(User).filter(User.email == "farmer@organicroots.com").first()
    
    assert retrieved_user is not None, "User should be found in database"
    assert retrieved_user.name == "Test Farmer", "User name should match"
    assert retrieved_user.role == "farmer", "User role should match"
    
    # Test password verification
    assert verify_password("FarmerPassword123!", retrieved_user.password_hash), "Password should verify"
    assert not verify_password("WrongPassword", retrieved_user.password_hash), "Wrong password should not verify"
    
    db.close()
    print("✅ User creation tests passed!")

def test_auth_endpoints():
    """Test authentication endpoint logic (without HTTP requests)"""
    print("🧪 Testing auth endpoint logic...")
    
    # Test registration logic
    try:
        # Reset database for clean test
        reset_database()
        db = next(get_db())
        
        # Simulate registration data validation
        register_data = {
            "name": "API Test User",
            "email": "apiuser@organicroots.com",
            "password": "ApiUser123!",
            "role": "farmer",
            "phone": "9876543210",
            "location": "API Test Farm"
        }
        
        # Test email uniqueness check
        existing_user = db.query(User).filter(User.email == register_data["email"]).first()
        assert existing_user is None, "Email should be unique"
        
        # Test role validation
        valid_roles = ["farmer", "admin", "consumer"]
        assert register_data["role"] in valid_roles, "Role should be valid"
        
        # Test password validation
        from utils.security import validate_password
        assert validate_password(register_data["password"]), "Password should be valid"
        
        # Simulate user creation
        from utils.security import get_password_hash
        hashed_password = get_password_hash(register_data["password"])
        
        new_user = User(
            name=register_data["name"],
            email=register_data["email"],
            password_hash=hashed_password,
            role=register_data["role"],
            phone=register_data["phone"],
            location=register_data["location"],
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("   ✅ Registration logic working")
        
        # Test login logic
        from utils.security import authenticate_user, create_user_token
        authenticated_user = authenticate_user(db, register_data["email"], register_data["password"])
        assert authenticated_user is not None, "User should authenticate"
        assert authenticated_user.email == register_data["email"], "Email should match"
        
        # Test token creation
        token_data = create_user_token(authenticated_user)
        assert "access_token" in token_data, "Token should be created"
        assert "user" in token_data, "User data should be included"
        
        print("   ✅ Login logic working")
        
        # Test token verification
        from utils.security import verify_token
        payload = verify_token(token_data["access_token"])
        assert payload["sub"] == str(authenticated_user.id), "Token should contain user ID"
        
        print("   ✅ Token verification working")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Auth endpoint logic test failed: {e}")
        raise
    
    print("✅ Auth endpoint logic tests completed!")

def test_password_validation():
    """Test password validation rules"""
    print("🧪 Testing password validation...")
    
    from utils.security import validate_password, get_password_requirements
    
    # Test valid password
    valid_password = "ValidPass123!"
    assert validate_password(valid_password), "Valid password should pass"
    
    # Test invalid passwords
    invalid_passwords = [
        "short",           # Too short
        "nouppercase123!", # No uppercase
        "NOLOWERCASE123!", # No lowercase
        "NoDigits!",       # No digits
    ]
    
    for invalid_pass in invalid_passwords:
        assert not validate_password(invalid_pass), f"Invalid password '{invalid_pass}' should fail"
    
    # Test requirements
    requirements = get_password_requirements()
    assert requirements["min_length"] == 8, "Min length should be 8"
    assert requirements["require_uppercase"], "Should require uppercase"
    assert requirements["require_lowercase"], "Should require lowercase"
    assert requirements["require_digit"], "Should require digit"
    
    print("✅ Password validation tests passed!")

def run_all_tests():
    """Run all authentication tests"""
    print("🚀 Starting authentication system tests...\n")
    
    try:
        test_password_hashing()
        print()
        
        test_jwt_tokens()
        print()
        
        test_user_creation()
        print()
        
        test_password_validation()
        print()
        
        test_auth_endpoints()
        print()
        
        print("🎉 All authentication tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
