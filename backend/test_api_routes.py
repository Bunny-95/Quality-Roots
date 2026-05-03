"""
Test script to verify API routes functionality
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all route modules can be imported"""
    print("🧪 Testing API route imports...")
    
    try:
        from routes.auth import router as auth_router
        print("   ✅ Auth routes imported")
        
        from routes.farmer import router as farmer_router
        print("   ✅ Farmer routes imported")
        
        from routes.admin import router as admin_router
        print("   ✅ Admin routes imported")
        
        from routes.consumer import router as consumer_router
        print("   ✅ Consumer routes imported")
        
        from routes.blockchain_routes import router as blockchain_router
        print("   ✅ Blockchain routes imported")
        
        from routes.ai_routes import router as ai_router
        print("   ✅ AI routes imported")
        
        from routes.supply_chain import router as supply_chain_router
        print("   ✅ Supply chain routes imported")
        
        print("✅ All route modules imported successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def test_main_app():
    """Test that the main FastAPI app can be created"""
    print("🧪 Testing FastAPI app creation...")
    
    try:
        from main import app
        
        # Check app configuration
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        print(f"   Debug mode: {app.debug}")
        
        # Check routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api'):
                routes.append(f"{route.methods} {route.path}")
        
        print(f"   Total API routes: {len(routes)}")
        
        # Show some example routes
        example_routes = routes[:5]
        print("   Example routes:")
        for route in example_routes:
            print(f"     {route}")
        
        print("✅ FastAPI app created successfully!")
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False
    
    return True

def test_route_endpoints():
    """Test that all expected endpoints are available"""
    print("🧪 Testing route endpoints...")
    
    try:
        from main import app
        
        expected_prefixes = [
            "/api/auth",
            "/api/farmer", 
            "/api/admin",
            "/api/consumer",
            "/api/blockchain",
            "/api/ai",
            "/api/supply"
        ]
        
        found_prefixes = set()
        for route in app.routes:
            if hasattr(route, 'path'):
                for prefix in expected_prefixes:
                    if route.path.startswith(prefix):
                        found_prefixes.add(prefix)
                        break
        
        print(f"   Found route prefixes: {len(found_prefixes)}/{len(expected_prefixes)}")
        
        missing_prefixes = set(expected_prefixes) - found_prefixes
        if missing_prefixes:
            print(f"   ❌ Missing prefixes: {missing_prefixes}")
            return False
        else:
            print("   ✅ All expected route prefixes found")
        
        # Check specific endpoints
        key_endpoints = [
            "/api/auth/register",
            "/api/auth/login",
            "/api/farmer/dashboard",
            "/api/admin/dashboard",
            "/api/consumer/verify/{batch_code}",
            "/api/blockchain/chain",
            "/api/ai/grade-quality",
            "/api/supply/event"
        ]
        
        found_endpoints = []
        for route in app.routes:
            if hasattr(route, 'path'):
                for endpoint in key_endpoints:
                    if route.path == endpoint or "{" in endpoint and endpoint.split("{")[0] in route.path:
                        found_endpoints.append(endpoint)
                        break
        
        print(f"   Found key endpoints: {len(found_endpoints)}/{len(key_endpoints)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint testing error: {e}")
        return False

def test_dependencies():
    """Test that all dependencies can be imported"""
    print("🧪 Testing dependencies...")
    
    dependencies = [
        "fastapi",
        "sqlalchemy", 
        "pydantic",
        "python_jose",
        "passlib",
        "qrcode",
        "sklearn",
        "numpy",
        "pandas",
        "joblib"
    ]
    
    failed_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep}")
            failed_deps.append(dep)
    
    if failed_deps:
        print(f"❌ Missing dependencies: {failed_deps}")
        return False
    else:
        print("✅ All dependencies available!")
        return True

def run_api_tests():
    """Run all API tests"""
    print("🚀 Starting API Routes Test Suite...\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Route Imports", test_imports),
        ("Main App", test_main_app),
        ("Route Endpoints", test_route_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API route tests completed successfully!")
        return True
    else:
        print("❌ Some API route tests failed")
        return False

if __name__ == "__main__":
    run_api_tests()
