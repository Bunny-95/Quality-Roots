#!/usr/bin/env python3
"""
Organic Roots - Final Integration Test
Tests all components working together
"""

import asyncio
import sys
import os
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import get_db, engine
from backend.models import User, Product, Batch, SupplyChainEvent, BlockchainBlock
from backend.blockchain.chain import Blockchain
from backend.ai.quality_grader import QualityGrader
from backend.ai.fraud_detector import FraudDetector
from backend.ai.demand_forecaster import DemandForecaster
from backend.utils.qr_generator import QRGenerator
from backend.utils.seed_data import SeedDataGenerator

class IntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
    
    def test_backend_startup(self) -> bool:
        """Test if backend is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            db = next(get_db())
            # Test a simple query
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            return False
    
    def test_auth_endpoints(self) -> bool:
        """Test authentication endpoints"""
        try:
            # Test registration
            register_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "testpass123",
                "role": "consumer",
                "location": "Test Location"
            }
            response = requests.post(f"{self.base_url}/api/auth/register", json=register_data)
            if response.status_code != 200:
                return False
            
            # Test login
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code != 200:
                return False
            
            token = response.json().get("access_token")
            if not token:
                return False
            
            # Store token for later tests
            self.auth_token = token
            return True
        except Exception as e:
            return False
    
    def test_blockchain_functionality(self) -> bool:
        """Test blockchain operations"""
        try:
            # Test blockchain stats
            response = requests.get(f"{self.base_url}/api/blockchain/stats")
            if response.status_code != 200:
                return False
            
            # Test blockchain verification
            response = requests.post(f"{self.base_url}/api/blockchain/verify")
            if response.status_code != 200:
                return False
            
            return True
        except Exception as e:
            return False
    
    def test_ai_modules(self) -> bool:
        """Test AI module endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test quality grading
            grade_data = {
                "batch_code": "TEST001",
                "product_type": "tomatoes",
                "moisture_level": 85.0,
                "color_score": 8.5,
                "aroma_score": 7.8,
                "defect_percentage": 2.1,
                "weight_per_unit": 150.0
            }
            response = requests.post(f"{self.base_url}/api/ai/grade-quality", json=grade_data, headers=headers)
            if response.status_code != 200:
                return False
            
            # Test fraud detection
            fraud_data = {
                "batch_code": "TEST001",
                "anomaly_score": 0.15,
                "location_variance": 0.05,
                "time_variance": 0.02,
                "quality_variance": 0.08
            }
            response = requests.post(f"{self.base_url}/api/ai/detect-fraud", json=fraud_data, headers=headers)
            if response.status_code != 200:
                return False
            
            # Test demand forecasting
            forecast_data = {
                "product_type": "tomatoes",
                "region": "north",
                "season": "summer"
            }
            response = requests.post(f"{self.base_url}/api/ai/forecast-demand", json=forecast_data, headers=headers)
            if response.status_code != 200:
                return False
            
            return True
        except Exception as e:
            return False
    
    def test_qr_generation(self) -> bool:
        """Test QR code generation"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            qr_data = {
                "batch_code": "TEST001",
                "product_name": "Test Tomatoes",
                "farmer_name": "Test Farmer"
            }
            response = requests.post(f"{self.base_url}/api/qr/generate", json=qr_data, headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def test_farmer_operations(self) -> bool:
        """Test farmer-specific operations"""
        try:
            # Create farmer user
            farmer_data = {
                "name": "Test Farmer",
                "email": "farmer@example.com",
                "password": "farmerpass123",
                "role": "farmer",
                "location": "Farm Location"
            }
            response = requests.post(f"{self.base_url}/api/auth/register", json=farmer_data)
            if response.status_code != 200:
                return False
            
            # Login as farmer
            login_data = {
                "email": "farmer@example.com",
                "password": "farmerpass123"
            }
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code != 200:
                return False
            
            farmer_token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {farmer_token}"}
            
            # Test batch creation
            batch_data = {
                "product_id": 1,
                "quantity_kg": 100.0,
                "planting_date": "2024-01-01",
                "harvest_date": "2024-03-01",
                "organic_certified": True
            }
            response = requests.post(f"{self.base_url}/api/farmer/batches", json=batch_data, headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def test_consumer_operations(self) -> bool:
        """Test consumer-specific operations"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test product verification
            response = requests.get(f"{self.base_url}/api/consumer/verify/TEST001", headers=headers)
            if response.status_code != 200:
                return False
            
            # Test product search
            response = requests.get(f"{self.base_url}/api/consumer/products", headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def test_admin_operations(self) -> bool:
        """Test admin-specific operations"""
        try:
            # Create admin user
            admin_data = {
                "name": "Test Admin",
                "email": "admin@example.com",
                "password": "adminpass123",
                "role": "admin",
                "location": "Admin Location"
            }
            response = requests.post(f"{self.base_url}/api/auth/register", json=admin_data)
            if response.status_code != 200:
                return False
            
            # Login as admin
            login_data = {
                "email": "admin@example.com",
                "password": "adminpass123"
            }
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code != 200:
                return False
            
            admin_token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Test admin dashboard
            response = requests.get(f"{self.base_url}/api/admin/dashboard", headers=headers)
            if response.status_code != 200:
                return False
            
            # Test user management
            response = requests.get(f"{self.base_url}/api/admin/users", headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def test_seed_data(self) -> bool:
        """Test seed data generation"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.post(f"{self.base_url}/api/admin/seed-data", headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def test_frontend_build(self) -> bool:
        """Test if frontend can be built"""
        try:
            frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
            if not os.path.exists(frontend_dir):
                return False
            
            # Check if package.json exists
            package_json = os.path.join(frontend_dir, 'package.json')
            if not os.path.exists(package_json):
                return False
            
            return True
        except Exception as e:
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting Organic Roots Integration Tests")
        print("=" * 50)
        
        # Test backend startup
        self.log_result("Backend Startup", self.test_backend_startup())
        
        # Test database
        self.log_result("Database Connection", self.test_database_connection())
        
        # Test authentication
        self.log_result("Authentication System", self.test_auth_endpoints())
        
        # Test blockchain
        self.log_result("Blockchain Operations", self.test_blockchain_functionality())
        
        # Test AI modules
        self.log_result("AI Modules", self.test_ai_modules())
        
        # Test QR generation
        self.log_result("QR Code Generation", self.test_qr_generation())
        
        # Test farmer operations
        self.log_result("Farmer Operations", self.test_farmer_operations())
        
        # Test consumer operations
        self.log_result("Consumer Operations", self.test_consumer_operations())
        
        # Test admin operations
        self.log_result("Admin Operations", self.test_admin_operations())
        
        # Test seed data
        self.log_result("Seed Data Generation", self.test_seed_data())
        
        # Test frontend
        self.log_result("Frontend Build Setup", self.test_frontend_build())
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print("=" * 50)
        print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
        
        if failed_tests > 0:
            print(f"❌ {failed_tests} tests failed:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        print(f"⏱️  Total time: {datetime.now() - self.start_time}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "test_results": self.test_results,
            "duration": str(datetime.now() - self.start_time)
        }

def main():
    """Main function to run integration tests"""
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: integration_test_results.json")
    
    # Exit with appropriate code
    if results["failed_tests"] > 0:
        print("\n❌ Integration tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All integration tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
