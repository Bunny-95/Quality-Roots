#!/usr/bin/env python3
"""
Organic Roots - System Health Check
Monitors all system components and reports health status
"""

import asyncio
import sys
import os
import requests
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import get_db, engine
from backend.models import User, Product, Batch, SupplyChainEvent, BlockchainBlock
from backend.blockchain.chain import Blockchain
from backend.ai.quality_grader import QualityGrader
from backend.ai.fraud_detector import FraudDetector
from backend.ai.demand_forecaster import DemandForecaster

class HealthChecker:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.health_status = {}
        self.start_time = datetime.now()
        
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "disk_usage": disk_percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
                "status": "healthy" if cpu_percent < 80 and memory_percent < 80 and disk_percent < 90 else "warning"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and stats"""
        try:
            db = next(get_db())
            
            # Test basic connectivity
            db.execute("SELECT 1")
            
            # Get table counts
            user_count = db.execute("SELECT COUNT(*) FROM users").scalar()
            product_count = db.execute("SELECT COUNT(*) FROM products").scalar()
            batch_count = db.execute("SELECT COUNT(*) FROM batches").scalar()
            event_count = db.execute("SELECT COUNT(*) FROM supply_chain_events").scalar()
            block_count = db.execute("SELECT COUNT(*) FROM blockchain_blocks").scalar()
            
            db.close()
            
            # Check database file size
            db_path = "backend/organic_roots.db"
            db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            
            return {
                "status": "healthy",
                "users": user_count,
                "products": product_count,
                "batches": batch_count,
                "events": event_count,
                "blocks": block_count,
                "database_size_mb": db_size / (1024**2),
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_backend_health(self) -> Dict[str, Any]:
        """Check backend API health"""
        try:
            # Basic health check
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code != 200:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
            
            # API health endpoints
            health_endpoints = [
                "/api/health/database",
                "/api/blockchain/stats",
                "/api/ai/models-status"
            ]
            
            endpoint_status = {}
            for endpoint in health_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    endpoint_status[endpoint] = {
                        "status": "healthy" if response.status_code == 200 else "error",
                        "response_time": response.elapsed.total_seconds()
                    }
                except Exception as e:
                    endpoint_status[endpoint] = {"status": "error", "error": str(e)}
            
            return {
                "status": "healthy",
                "base_url": self.base_url,
                "endpoints": endpoint_status,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_ai_models_health(self) -> Dict[str, Any]:
        """Check AI model status"""
        try:
            models_status = {}
            
            # Test Quality Grader
            try:
                grader = QualityGrader()
                # Test with sample data
                sample_data = {
                    "moisture_level": 85.0,
                    "color_score": 8.5,
                    "aroma_score": 7.8,
                    "defect_percentage": 2.1,
                    "weight_per_unit": 150.0
                }
                grade = grader.predict_grade(sample_data)
                models_status["quality_grader"] = {
                    "status": "healthy",
                    "prediction": grade,
                    "model_type": "RandomForest"
                }
            except Exception as e:
                models_status["quality_grader"] = {"status": "error", "error": str(e)}
            
            # Test Fraud Detector
            try:
                detector = FraudDetector()
                sample_data = {
                    "anomaly_score": 0.15,
                    "location_variance": 0.05,
                    "time_variance": 0.02,
                    "quality_variance": 0.08
                }
                fraud_score = detector.predict_fraud(sample_data)
                models_status["fraud_detector"] = {
                    "status": "healthy",
                    "fraud_score": fraud_score,
                    "model_type": "IsolationForest"
                }
            except Exception as e:
                models_status["fraud_detector"] = {"status": "error", "error": str(e)}
            
            # Test Demand Forecaster
            try:
                forecaster = DemandForecaster()
                sample_data = {
                    "product_type": "tomatoes",
                    "region": "north",
                    "season": "summer"
                }
                forecast = forecaster.predict_demand(sample_data)
                models_status["demand_forecaster"] = {
                    "status": "healthy",
                    "forecast": forecast,
                    "model_type": "LinearRegression"
                }
            except Exception as e:
                models_status["demand_forecaster"] = {"status": "error", "error": str(e)}
            
            # Overall status
            healthy_count = sum(1 for model in models_status.values() if model["status"] == "healthy")
            total_count = len(models_status)
            
            return {
                "status": "healthy" if healthy_count == total_count else "degraded",
                "models": models_status,
                "healthy_models": healthy_count,
                "total_models": total_count
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_blockchain_health(self) -> Dict[str, Any]:
        """Check blockchain integrity"""
        try:
            blockchain = Blockchain()
            
            # Get blockchain stats
            chain = blockchain.get_chain()
            latest_block = blockchain.get_latest_block()
            
            # Verify chain integrity
            is_valid = blockchain.is_chain_valid()
            
            # Get mining difficulty
            difficulty = blockchain.difficulty
            
            return {
                "status": "healthy" if is_valid else "error",
                "total_blocks": len(chain),
                "latest_block_index": latest_block.index if latest_block else 0,
                "difficulty": difficulty,
                "is_valid": is_valid,
                "last_block_timestamp": latest_block.timestamp if latest_block else None
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_recent_activity(self) -> Dict[str, Any]:
        """Check recent system activity"""
        try:
            db = next(get_db())
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            
            recent_users = db.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= ?
            """, (yesterday,)).scalar()
            
            recent_batches = db.execute("""
                SELECT COUNT(*) FROM batches 
                WHERE created_at >= ?
            """, (yesterday,)).scalar()
            
            recent_events = db.execute("""
                SELECT COUNT(*) FROM supply_chain_events 
                WHERE timestamp >= ?
            """, (yesterday,)).scalar()
            
            recent_blocks = db.execute("""
                SELECT COUNT(*) FROM blockchain_blocks 
                WHERE timestamp >= ?
            """, (yesterday,)).scalar()
            
            db.close()
            
            return {
                "status": "healthy",
                "recent_users_24h": recent_users,
                "recent_batches_24h": recent_batches,
                "recent_events_24h": recent_events,
                "recent_blocks_24h": recent_blocks,
                "period_hours": 24
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_service_dependencies(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        dependencies = {}
        
        # Check if required services are running
        try:
            # Backend API
            response = requests.get(f"{self.base_url}/", timeout=5)
            dependencies["backend_api"] = {
                "status": "healthy" if response.status_code == 200 else "error",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            dependencies["backend_api"] = {"status": "error", "error": str(e)}
        
        # Check file system access
        try:
            test_file = "health_check_test.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            dependencies["file_system"] = {"status": "healthy"}
        except Exception as e:
            dependencies["file_system"] = {"status": "error", "error": str(e)}
        
        # Check QR codes directory
        qr_dir = "backend/qr_codes"
        if os.path.exists(qr_dir) and os.access(qr_dir, os.W_OK):
            dependencies["qr_codes_directory"] = {"status": "healthy"}
        else:
            dependencies["qr_codes_directory"] = {"status": "error", "error": "Directory not accessible"}
        
        return dependencies
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        print("🔍 Running Organic Roots System Health Check...")
        print("=" * 60)
        
        # Run all health checks
        checks = {
            "system_resources": self.check_system_resources(),
            "database": self.check_database_health(),
            "backend": self.check_backend_health(),
            "ai_models": self.check_ai_models_health(),
            "blockchain": self.check_blockchain_health(),
            "recent_activity": self.check_recent_activity(),
            "dependencies": self.check_service_dependencies()
        }
        
        # Calculate overall health
        healthy_checks = sum(1 for check in checks.values() if check.get("status") == "healthy")
        total_checks = len(checks)
        overall_health = "healthy" if healthy_checks == total_checks else "degraded"
        
        # Prepare report
        report = {
            "overall_health": overall_health,
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "duration": str(datetime.now() - self.start_time)
        }
        
        # Display results
        self.display_health_report(report)
        
        return report
    
    def display_health_report(self, report: Dict[str, Any]):
        """Display health report in a readable format"""
        overall_health = report["overall_health"]
        healthy_checks = report["healthy_checks"]
        total_checks = report["total_checks"]
        
        # Overall status
        if overall_health == "healthy":
            print("✅ Overall System Health: HEALTHY")
        else:
            print("⚠️  Overall System Health: DEGRADED")
        
        print(f"📊 Healthy Checks: {healthy_checks}/{total_checks}")
        print(f"⏱️  Check Duration: {report['duration']}")
        print(f"🕐 Timestamp: {report['timestamp']}")
        print("")
        
        # Individual checks
        checks = report["checks"]
        
        # System Resources
        resources = checks["system_resources"]
        if resources["status"] == "healthy":
            print("✅ System Resources:")
        else:
            print("⚠️  System Resources:")
        print(f"   CPU Usage: {resources.get('cpu_usage', 'N/A')}%")
        print(f"   Memory Usage: {resources.get('memory_usage', 'N/A')}%")
        print(f"   Disk Usage: {resources.get('disk_usage', 'N/A')}%")
        print("")
        
        # Database
        db = checks["database"]
        if db["status"] == "healthy":
            print("✅ Database:")
        else:
            print("❌ Database:")
        print(f"   Users: {db.get('users', 'N/A')}")
        print(f"   Products: {db.get('products', 'N/A')}")
        print(f"   Batches: {db.get('batches', 'N/A')}")
        print(f"   Events: {db.get('events', 'N/A')}")
        print(f"   Database Size: {db.get('database_size_mb', 'N/A'):.2f} MB")
        print("")
        
        # Backend
        backend = checks["backend"]
        if backend["status"] == "healthy":
            print("✅ Backend API:")
        else:
            print("❌ Backend API:")
        print(f"   Base URL: {backend.get('base_url', 'N/A')}")
        for endpoint, status in backend.get("endpoints", {}).items():
            endpoint_status = "✅" if status["status"] == "healthy" else "❌"
            print(f"   {endpoint_status} {endpoint}")
        print("")
        
        # AI Models
        ai = checks["ai_models"]
        if ai["status"] == "healthy":
            print("✅ AI Models:")
        else:
            print("⚠️  AI Models:")
        print(f"   Healthy Models: {ai.get('healthy_models', 'N/A')}/{ai.get('total_models', 'N/A')}")
        for model_name, model_status in ai.get("models", {}).items():
            model_icon = "✅" if model_status["status"] == "healthy" else "❌"
            print(f"   {model_icon} {model_name.replace('_', ' ').title()}")
        print("")
        
        # Blockchain
        blockchain = checks["blockchain"]
        if blockchain["status"] == "healthy":
            print("✅ Blockchain:")
        else:
            print("❌ Blockchain:")
        print(f"   Total Blocks: {blockchain.get('total_blocks', 'N/A')}")
        print(f"   Latest Block: {blockchain.get('latest_block_index', 'N/A')}")
        print(f"   Chain Valid: {blockchain.get('is_valid', 'N/A')}")
        print(f"   Difficulty: {blockchain.get('difficulty', 'N/A')}")
        print("")
        
        # Recent Activity
        activity = checks["recent_activity"]
        if activity["status"] == "healthy":
            print("✅ Recent Activity (24h):")
        else:
            print("❌ Recent Activity:")
        print(f"   New Users: {activity.get('recent_users_24h', 'N/A')}")
        print(f"   New Batches: {activity.get('recent_batches_24h', 'N/A')}")
        print(f"   New Events: {activity.get('recent_events_24h', 'N/A')}")
        print(f"   New Blocks: {activity.get('recent_blocks_24h', 'N/A')}")
        print("")
        
        # Dependencies
        deps = checks["dependencies"]
        print("📦 Dependencies:")
        for dep_name, dep_status in deps.items():
            dep_icon = "✅" if dep_status["status"] == "healthy" else "❌"
            print(f"   {dep_icon} {dep_name.replace('_', ' ').title()}")
        print("")
        
        # Recommendations
        if overall_health != "healthy":
            print("🔧 Recommendations:")
            for check_name, check_data in checks.items():
                if check_data.get("status") != "healthy":
                    print(f"   - Fix {check_name.replace('_', ' ').title()}")
            print("")

def main():
    """Main function to run health check"""
    checker = HealthChecker()
    report = checker.generate_health_report()
    
    # Save report to file
    with open("health_check_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Detailed report saved to: health_check_report.json")
    
    # Exit with appropriate code
    if report["overall_health"] == "healthy":
        print("\n🎉 System is healthy!")
        sys.exit(0)
    else:
        print("\n⚠️  System health issues detected!")
        sys.exit(1)

if __name__ == "__main__":
    main()
