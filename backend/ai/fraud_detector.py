"""
Organic Roots AI Fraud Detector
Uses Isolation Forest to detect anomalous supply chain transactions
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RANDOM_STATE, MODEL_DIR

class FraudDetector:
    """AI-based fraud detection for supply chain transactions"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = [
            'price_per_kg', 'quantity_kg', 'transit_days', 
            'temperature_reported', 'location_jump_km', 'time_since_last_event_hours'
        ]
        self.model_path = MODEL_DIR / "fraud_detector.joblib"
        self.scaler_path = MODEL_DIR / "fraud_scaler.joblib"
        self.is_trained = False
        
        # Create model directory if it doesn't exist
        MODEL_DIR.mkdir(exist_ok=True)
    
    def generate_synthetic_data(self, n_samples: int = 300) -> pd.DataFrame:
        """Generate synthetic normal transaction data"""
        print(f"🔄 Generating {n_samples} synthetic normal transaction samples...")
        
        data = []
        base_time = datetime.now()
        
        for i in range(n_samples):
            # Generate realistic normal transaction data
            price_per_kg = np.random.normal(50, 15)  # Normal price range
            quantity_kg = np.random.exponential(100)  # Most transactions small
            transit_days = max(1, np.random.normal(3, 1))  # 1-7 days normal
            temperature = np.random.normal(25, 5)  # Room temperature
            location_jump = np.random.exponential(50)  # Most jumps small
            time_since_last = np.random.exponential(24)  # Hours since last event
            
            # Ensure realistic ranges
            price_per_kg = max(5, min(200, price_per_kg))
            quantity_kg = max(1, min(1000, quantity_kg))
            transit_days = max(1, min(14, transit_days))
            temperature = max(10, min(40, temperature))
            location_jump = max(0, min(500, location_jump))
            time_since_last = max(0.1, min(168, time_since_last))  # Max 1 week
            
            data.append({
                'price_per_kg': round(price_per_kg, 2),
                'quantity_kg': round(quantity_kg, 1),
                'transit_days': round(transit_days, 1),
                'temperature_reported': round(temperature, 1),
                'location_jump_km': round(location_jump, 1),
                'time_since_last_event_hours': round(time_since_last, 1),
                'timestamp': base_time + timedelta(hours=i * np.random.uniform(0.5, 4))
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated synthetic normal transaction data")
        return df
    
    def generate_anomalous_data(self, n_samples: int = 50) -> pd.DataFrame:
        """Generate synthetic anomalous transaction data"""
        print(f"🔄 Generating {n_samples} synthetic anomalous transaction samples...")
        
        data = []
        base_time = datetime.now()
        
        for i in range(n_samples):
            anomaly_type = random.choice(['price_spike', 'impossible_transit', 'temperature_anomaly', 'location_jump'])
            
            if anomaly_type == 'price_spike':
                # Unusually high price
                price_per_kg = np.random.normal(150, 30)
                quantity_kg = np.random.exponential(100)
                transit_days = max(1, np.random.normal(3, 1))
                temperature = np.random.normal(25, 5)
                location_jump = np.random.exponential(50)
                time_since_last = np.random.exponential(24)
                
            elif anomaly_type == 'impossible_transit':
                # Impossible fast transit
                price_per_kg = np.random.normal(50, 15)
                quantity_kg = np.random.exponential(100)
                transit_days = max(0.1, np.random.normal(0.5, 0.2))  # Too fast
                temperature = np.random.normal(25, 5)
                location_jump = np.random.exponential(200)  # Long distance
                time_since_last = np.random.exponential(24)
                
            elif anomaly_type == 'temperature_anomaly':
                # Unusual temperature
                price_per_kg = np.random.normal(50, 15)
                quantity_kg = np.random.exponential(100)
                transit_days = max(1, np.random.normal(3, 1))
                temperature = np.random.choice([np.random.normal(-5, 2), np.random.normal(60, 5)])  # Too cold/hot
                location_jump = np.random.exponential(50)
                time_since_last = np.random.exponential(24)
                
            else:  # location_jump
                # Impossible location jump
                price_per_kg = np.random.normal(50, 15)
                quantity_kg = np.random.exponential(100)
                transit_days = max(1, np.random.normal(3, 1))
                temperature = np.random.normal(25, 5)
                location_jump = np.random.exponential(800)  # Very long distance
                time_since_last = np.random.exponential(24)
            
            # Ensure ranges
            price_per_kg = max(5, min(300, price_per_kg))
            quantity_kg = max(1, min(1000, quantity_kg))
            transit_days = max(0.1, min(14, transit_days))
            temperature = max(-10, min(70, temperature))
            location_jump = max(0, min(1500, location_jump))
            time_since_last = max(0.1, min(168, time_since_last))
            
            data.append({
                'price_per_kg': round(price_per_kg, 2),
                'quantity_kg': round(quantity_kg, 1),
                'transit_days': round(transit_days, 1),
                'temperature_reported': round(temperature, 1),
                'location_jump_km': round(location_jump, 1),
                'time_since_last_event_hours': round(time_since_last, 1),
                'timestamp': base_time + timedelta(hours=i * np.random.uniform(0.5, 4)),
                'is_anomaly': True
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated synthetic anomalous transaction data")
        return df
    
    def train_model(self) -> Dict[str, Any]:
        """Train the fraud detection model"""
        print("🧠 Training fraud detection model...")
        
        # Generate training data (only normal data for unsupervised learning)
        normal_data = self.generate_synthetic_data()
        
        # Prepare features
        X = normal_data[self.feature_columns]
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,  # Expect ~10% anomalies
            random_state=RANDOM_STATE,
            max_samples='auto'
        )
        
        self.model.fit(X_scaled)
        
        print("✅ Fraud detection model trained successfully")
        
        # Save model and scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        self.is_trained = True
        
        return {
            "training_samples": len(normal_data),
            "contamination_rate": 0.1,
            "feature_names": self.feature_columns
        }
    
    def load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            if self.model_path.exists() and self.scaler_path.exists():
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                print("✅ Fraud detector model loaded successfully")
                return True
            else:
                print("⚠️ No trained model found, training new model...")
                self.train_model()
                return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def detect_fraud(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect fraud in a single transaction"""
        if not self.is_trained:
            self.load_model()
        
        # Extract features
        features = []
        for col in self.feature_columns:
            value = transaction_data.get(col)
            if value is None:
                raise ValueError(f"Missing required feature: {col}")
            features.append(value)
        
        # Scale features
        features_array = np.array(features).reshape(1, -1)
        features_scaled = self.scaler.transform(features_array)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]  # -1 for anomaly, 1 for normal
        anomaly_score = self.model.decision_function(features_scaled)[0]
        
        # Convert to user-friendly format
        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(anomaly_score, is_anomaly)
        flags = self._generate_flags(transaction_data, is_anomaly, anomaly_score)
        
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(anomaly_score), 3),
            "risk_level": risk_level,
            "flags": flags,
            "confidence": round(abs(anomaly_score), 3)
        }
    
    def _calculate_risk_level(self, anomaly_score: float, is_anomaly: bool) -> str:
        """Calculate risk level based on anomaly score"""
        if not is_anomaly:
            return "LOW"
        
        if anomaly_score < -0.5:
            return "HIGH"
        elif anomaly_score < -0.2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_flags(self, transaction_data: Dict[str, Any], is_anomaly: bool, anomaly_score: float) -> List[str]:
        """Generate specific flags for anomalous transactions"""
        flags = []
        
        if not is_anomaly:
            return ["No suspicious activity detected"]
        
        # Check specific anomalies
        price = transaction_data['price_per_kg']
        quantity = transaction_data['quantity_kg']
        transit_days = transaction_data['transit_days']
        temperature = transaction_data['temperature_reported']
        location_jump = transaction_data['location_jump_km']
        time_since_last = transaction_data['time_since_last_event_hours']
        
        # Price anomalies
        if price > 150:
            flags.append("Unusual price spike detected")
        elif price < 10:
            flags.append("Suspiciously low price")
        
        # Transit anomalies
        if transit_days < 0.5:
            flags.append("Impossible transit speed")
        elif transit_days > 10:
            flags.append("Unusually long transit time")
        
        # Temperature anomalies
        if temperature < 5:
            flags.append("Suspiciously low temperature")
        elif temperature > 45:
            flags.append("Suspiciously high temperature")
        
        # Location anomalies
        if location_jump > 500:
            flags.append("Impossible location jump")
        
        # Time anomalies
        if time_since_last < 0.5:
            flags.append("Suspiciously rapid transaction sequence")
        
        # Quantity anomalies
        if quantity > 500:
            flags.append("Unusually large quantity")
        
        if not flags:
            flags.append("General anomalous pattern detected")
        
        return flags
    
    def batch_detect_fraud(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect fraud in multiple transactions"""
        results = []
        for transaction in transactions:
            try:
                result = self.detect_fraud(transaction)
                result['transaction_id'] = transaction.get('transaction_id', 'unknown')
                results.append(result)
            except Exception as e:
                results.append({
                    'transaction_id': transaction.get('transaction_id', 'unknown'),
                    'error': str(e)
                })
        return results
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        if not self.is_trained:
            self.load_model()
        
        return {
            "model_type": "Isolation Forest",
            "feature_count": len(self.feature_columns),
            "contamination_rate": 0.1,
            "features": self.feature_columns
        }

# Global instance
fraud_detector = FraudDetector()

def test_fraud_detector():
    """Test the fraud detector"""
    print("🧪 Testing Fraud Detector...")
    
    # Test normal transaction
    normal_transaction = {
        "transaction_id": "NORMAL001",
        "price_per_kg": 45.50,
        "quantity_kg": 120.0,
        "transit_days": 3.2,
        "temperature_reported": 24.5,
        "location_jump_km": 45.0,
        "time_since_last_event_hours": 18.5
    }
    
    # Test anomalous transaction
    anomalous_transaction = {
        "transaction_id": "ANOMALY001",
        "price_per_kg": 180.00,
        "quantity_kg": 800.0,
        "transit_days": 0.3,
        "temperature_reported": 55.0,
        "location_jump_km": 1200.0,
        "time_since_last_event_hours": 0.2
    }
    
    # Test both
    print("\nNormal Transaction:")
    result1 = fraud_detector.detect_fraud(normal_transaction)
    print(f"  Is Anomaly: {result1['is_anomaly']}")
    print(f"  Risk Level: {result1['risk_level']}")
    print(f"  Flags: {', '.join(result1['flags'])}")
    
    print("\nAnomalous Transaction:")
    result2 = fraud_detector.detect_fraud(anomalous_transaction)
    print(f"  Is Anomaly: {result2['is_anomaly']}")
    print(f"  Risk Level: {result2['risk_level']}")
    print(f"  Flags: {', '.join(result2['flags'])}")
    
    # Test batch detection
    print("\nBatch Detection:")
    batch_results = fraud_detector.batch_detect_fraud([normal_transaction, anomalous_transaction])
    for result in batch_results:
        print(f"  {result['transaction_id']}: {result['risk_level']} risk")
    
    print("✅ Fraud detector test completed!")

if __name__ == "__main__":
    test_fraud_detector()
