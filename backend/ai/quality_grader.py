"""
Organic Roots AI Quality Grader
Uses RandomForest to grade product batches as Grade A/B/C
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from typing import Dict, Any, List, Tuple
from datetime import datetime
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RANDOM_STATE, MODEL_DIR

class QualityGrader:
    """AI-based quality grader for agricultural products"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'moisture_level', 'color_score', 'aroma_score', 
            'defect_percentage', 'weight_per_unit'
        ]
        self.product_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
        self.model_path = MODEL_DIR / "quality_grader.joblib"
        self.is_trained = False
        
        # Create model directory if it doesn't exist
        MODEL_DIR.mkdir(exist_ok=True)
    
    def generate_synthetic_data(self, n_samples: int = 500) -> pd.DataFrame:
        """Generate synthetic training data for quality grading"""
        print(f"🔄 Generating {n_samples} synthetic training samples...")
        
        data = []
        for i in range(n_samples):
            product_type = random.choice(self.product_types)
            
            # Generate realistic quality attributes based on product type
            if product_type == 'spice':
                moisture = np.random.normal(10, 2)  # Lower moisture for spices
                color = np.random.normal(7.5, 1.5)
                aroma = np.random.normal(8.0, 1.2)
                defects = np.random.exponential(3)  # Lower defects for spices
                weight = np.random.normal(50, 10)
            elif product_type == 'coffee':
                moisture = np.random.normal(12, 1.5)
                color = np.random.normal(8.0, 1.0)
                aroma = np.random.normal(8.5, 1.0)
                defects = np.random.exponential(2)
                weight = np.random.normal(200, 20)
            elif product_type == 'tea':
                moisture = np.random.normal(8, 1.5)
                color = np.random.normal(7.0, 1.2)
                aroma = np.random.normal(7.5, 1.5)
                defects = np.random.exponential(4)
                weight = np.random.normal(100, 15)
            elif product_type == 'millet':
                moisture = np.random.normal(13, 2)
                color = np.random.normal(6.5, 1.0)
                aroma = np.random.normal(6.0, 1.0)
                defects = np.random.exponential(5)
                weight = np.random.normal(30, 5)
            else:  # organic
                moisture = np.random.normal(11, 1.8)
                color = np.random.normal(8.2, 1.3)
                aroma = np.random.normal(8.0, 1.2)
                defects = np.random.exponential(2.5)
                weight = np.random.normal(150, 25)
            
            # Ensure values are in realistic ranges
            moisture = max(0, min(100, moisture))
            color = max(0, min(10, color))
            aroma = max(0, min(10, aroma))
            defects = max(0, min(100, defects))
            weight = max(1, weight)
            
            # Determine grade based on quality attributes
            quality_score = (color * 10 + aroma * 10 + (100 - defects) * 5 + (100 - abs(moisture - 12)) * 3) / 28
            
            if quality_score >= 85:
                grade = 'A'
            elif quality_score >= 70:
                grade = 'B'
            else:
                grade = 'C'
            
            data.append({
                'product_type': product_type,
                'moisture_level': round(moisture, 1),
                'color_score': round(color, 1),
                'aroma_score': round(aroma, 1),
                'defect_percentage': round(defects, 1),
                'weight_per_unit': round(weight, 1),
                'grade': grade
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated synthetic data: {len(df[df['grade'] == 'A'])} Grade A, {len(df[df['grade'] == 'B'])} Grade B, {len(df[df['grade'] == 'C'])} Grade C")
        return df
    
    def train_model(self) -> Dict[str, Any]:
        """Train the quality grading model"""
        print("🧠 Training quality grading model...")
        
        # Generate training data
        df = self.generate_synthetic_data()
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['grade']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
        )
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=RANDOM_STATE,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained with accuracy: {accuracy:.3f}")
        print("Classification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        joblib.dump(self.model, self.model_path)
        self.is_trained = True
        
        return {
            "accuracy": accuracy,
            "feature_importance": dict(zip(self.feature_columns, self.model.feature_importances_)),
            "training_samples": len(df),
            "test_samples": len(X_test)
        }
    
    def load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                print("✅ Quality grader model loaded successfully")
                return True
            else:
                print("⚠️ No trained model found, training new model...")
                self.train_model()
                return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def grade_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a product batch"""
        if not self.is_trained:
            self.load_model()
        
        # Extract features
        features = []
        for col in self.feature_columns:
            value = batch_data.get(col)
            if value is None:
                raise ValueError(f"Missing required feature: {col}")
            features.append(value)
        
        # Make prediction
        features_array = np.array(features).reshape(1, -1)
        grade = self.model.predict(features_array)[0]
        probabilities = self.model.predict_proba(features_array)[0]
        confidence = max(probabilities)
        
        # Calculate quality score (0-100)
        quality_score = self._calculate_quality_score(batch_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(batch_data, grade)
        
        return {
            "grade": grade,
            "confidence": round(confidence, 3),
            "quality_score": round(quality_score, 1),
            "recommendations": recommendations,
            "grade_probabilities": {
                "A": round(probabilities[0] if self.model.classes_[0] == 'A' else 0, 3),
                "B": round(probabilities[1] if len(probabilities) > 1 and self.model.classes_[1] == 'B' else 0, 3),
                "C": round(probabilities[2] if len(probabilities) > 2 and self.model.classes_[2] == 'C' else 0, 3)
            }
        }
    
    def _calculate_quality_score(self, batch_data: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)"""
        moisture = batch_data['moisture_level']
        color = batch_data['color_score']
        aroma = batch_data['aroma_score']
        defects = batch_data['defect_percentage']
        
        # Weighted scoring
        moisture_score = max(0, 100 - abs(moisture - 12) * 5)  # Optimal moisture ~12%
        color_score = color * 10  # 0-10 scale to 0-100
        aroma_score = aroma * 10  # 0-10 scale to 0-100
        defect_score = max(0, 100 - defects)  # Lower defects = higher score
        
        # Weighted average
        total_score = (moisture_score * 0.25 + color_score * 0.25 + 
                      aroma_score * 0.3 + defect_score * 0.2)
        
        return min(100, max(0, total_score))
    
    def _generate_recommendations(self, batch_data: Dict[str, Any], grade: str) -> List[str]:
        """Generate improvement recommendations based on grade and attributes"""
        recommendations = []
        
        moisture = batch_data['moisture_level']
        color = batch_data['color_score']
        aroma = batch_data['aroma_score']
        defects = batch_data['defect_percentage']
        
        if moisture > 15:
            recommendations.append("Reduce moisture content to <15% for better preservation")
        elif moisture < 8:
            recommendations.append("Moisture content is low, ensure proper storage conditions")
        
        if color < 6:
            recommendations.append("Improve color quality through better processing methods")
        
        if aroma < 6:
            recommendations.append("Enhance aroma profile through optimized curing/drying")
        
        if defects > 10:
            recommendations.append("Implement better quality control to reduce defects")
        
        if grade == 'A':
            recommendations.append("Excellent quality! Consider premium pricing")
        elif grade == 'B':
            recommendations.append("Good quality with room for improvement")
        else:
            recommendations.append("Quality needs significant improvement")
        
        return recommendations
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if not self.is_trained:
            self.load_model()
        
        return dict(zip(self.feature_columns, self.model.feature_importances_))
    
    def batch_grade_multiple(self, batches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Grade multiple batches at once"""
        results = []
        for batch in batches:
            try:
                result = self.grade_batch(batch)
                result['batch_code'] = batch.get('batch_code', 'unknown')
                results.append(result)
            except Exception as e:
                results.append({
                    'batch_code': batch.get('batch_code', 'unknown'),
                    'error': str(e)
                })
        return results

# Global instance
quality_grader = QualityGrader()

def test_quality_grader():
    """Test the quality grader"""
    print("🧪 Testing Quality Grader...")
    
    # Test data
    test_batch = {
        "batch_code": "TEST001",
        "product_type": "coffee",
        "moisture_level": 11.5,
        "color_score": 8.2,
        "aroma_score": 8.7,
        "defect_percentage": 2.1,
        "weight_per_unit": 205.0
    }
    
    # Grade the batch
    result = quality_grader.grade_batch(test_batch)
    
    print(f"Batch {test_batch['batch_code']}:")
    print(f"  Grade: {result['grade']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Quality Score: {result['quality_score']}")
    print(f"  Recommendations: {', '.join(result['recommendations'])}")
    
    # Test feature importance
    importance = quality_grader.get_feature_importance()
    print(f"Feature Importance: {importance}")
    
    print("✅ Quality grader test completed!")

if __name__ == "__main__":
    test_quality_grader()
