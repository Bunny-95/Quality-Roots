"""
Test script to verify all AI modules functionality
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.quality_grader import quality_grader
from ai.fraud_detector import fraud_detector
from ai.demand_forecaster import demand_forecaster

def test_quality_grader():
    """Test the quality grader AI module"""
    print("🧪 Testing Quality Grader AI Module...")
    
    # Test batch data
    test_batch = {
        "batch_code": "AI_TEST001",
        "product_type": "coffee",
        "moisture_level": 11.5,
        "color_score": 8.2,
        "aroma_score": 8.7,
        "defect_percentage": 2.1,
        "weight_per_unit": 205.0
    }
    
    # Grade the batch
    result = quality_grader.grade_batch(test_batch)
    
    print(f"   Batch {test_batch['batch_code']}:")
    print(f"     Grade: {result['grade']}")
    print(f"     Confidence: {result['confidence']}")
    print(f"     Quality Score: {result['quality_score']}")
    print(f"     Recommendations: {', '.join(result['recommendations'])}")
    
    # Test multiple batches
    test_batches = [
        {
            "batch_code": "AI_TEST002",
            "product_type": "spice",
            "moisture_level": 9.8,
            "color_score": 7.5,
            "aroma_score": 8.0,
            "defect_percentage": 3.2,
            "weight_per_unit": 48.0
        },
        {
            "batch_code": "AI_TEST003",
            "product_type": "tea",
            "moisture_level": 14.5,
            "color_score": 6.2,
            "aroma_score": 6.8,
            "defect_percentage": 8.5,
            "weight_per_unit": 95.0
        }
    ]
    
    batch_results = quality_grader.batch_grade_multiple(test_batches)
    print(f"   Batch grading results: {len(batch_results)} batches processed")
    
    # Test feature importance
    importance = quality_grader.get_feature_importance()
    print(f"   Feature importance: {importance}")
    
    print("✅ Quality Grader AI test completed!")

def test_fraud_detector():
    """Test the fraud detector AI module"""
    print("🧪 Testing Fraud Detector AI Module...")
    
    # Test normal transaction
    normal_transaction = {
        "transaction_id": "AI_NORMAL001",
        "price_per_kg": 45.50,
        "quantity_kg": 120.0,
        "transit_days": 3.2,
        "temperature_reported": 24.5,
        "location_jump_km": 45.0,
        "time_since_last_event_hours": 18.5
    }
    
    # Test anomalous transaction
    anomalous_transaction = {
        "transaction_id": "AI_ANOMALY001",
        "price_per_kg": 180.00,
        "quantity_kg": 800.0,
        "transit_days": 0.3,
        "temperature_reported": 55.0,
        "location_jump_km": 1200.0,
        "time_since_last_event_hours": 0.2
    }
    
    # Test both transactions
    print("   Normal Transaction:")
    result1 = fraud_detector.detect_fraud(normal_transaction)
    print(f"     Is Anomaly: {result1['is_anomaly']}")
    print(f"     Risk Level: {result1['risk_level']}")
    print(f"     Flags: {', '.join(result1['flags'])}")
    
    print("   Anomalous Transaction:")
    result2 = fraud_detector.detect_fraud(anomalous_transaction)
    print(f"     Is Anomaly: {result2['is_anomaly']}")
    print(f"     Risk Level: {result2['risk_level']}")
    print(f"     Flags: {', '.join(result2['flags'])}")
    
    # Test batch detection
    batch_results = fraud_detector.batch_detect_fraud([normal_transaction, anomalous_transaction])
    print(f"   Batch detection: {len(batch_results)} transactions processed")
    
    # Test model stats
    stats = fraud_detector.get_model_stats()
    print(f"   Model stats: {stats}")
    
    print("✅ Fraud Detector AI test completed!")

def test_demand_forecaster():
    """Test the demand forecaster AI module"""
    print("🧪 Testing Demand Forecaster AI Module...")
    
    # Test historical data
    historical_prices = [45.2, 46.1, 44.8, 47.3, 48.1, 46.9, 47.5, 48.2, 49.1, 47.8, 
                        48.5, 49.3, 50.1, 48.9, 49.7, 50.5, 51.2, 50.0, 50.8, 51.5,
                        52.3, 51.1, 51.9, 52.7, 53.4, 52.2, 53.0, 53.8, 54.5, 53.3]
    
    historical_demand = [850, 870, 840, 890, 910, 880, 900, 920, 940, 910, 
                         930, 950, 970, 940, 960, 980, 1000, 970, 990, 1010,
                         1030, 1000, 1020, 1040, 1060, 1030, 1050, 1070, 1090, 1060]
    
    # Test forecast for coffee
    result = demand_forecaster.forecast('coffee', historical_prices, historical_demand, 'summer')
    
    print(f"   Coffee Forecast ({result['season']} season):")
    print(f"     Recommended Price: ${result['recommended_price']}")
    print(f"     Price Trend: {result['price_trend']}")
    print(f"     Demand Trend: {result['demand_trend']}")
    print(f"     Confidence: {result['confidence']}")
    print(f"     Avg Forecasted Demand: {result['avg_forecasted_demand']}")
    
    # Test all products
    print("   All Product Forecasts:")
    all_forecasts = demand_forecaster.get_all_product_forecasts('summer')
    for product, forecast in all_forecasts.items():
        print(f"     {product}: ${forecast['recommended_price']} recommended price")
    
    # Test model stats
    stats = demand_forecaster.get_model_stats()
    print(f"   Model stats: {stats}")
    
    print("✅ Demand Forecaster AI test completed!")

def test_ai_integration():
    """Test AI modules working together"""
    print("🧪 Testing AI Module Integration...")
    
    # Simulate a complete supply chain scenario
    batch_data = {
        "batch_code": "INTEGRATION_TEST",
        "product_type": "coffee",
        "moisture_level": 11.5,
        "color_score": 8.2,
        "aroma_score": 8.7,
        "defect_percentage": 2.1,
        "weight_per_unit": 205.0
    }
    
    # Step 1: Quality grading
    grade_result = quality_grader.grade_batch(batch_data)
    print(f"   Step 1 - Quality Grading: Grade {grade_result['grade']}, Score {grade_result['quality_score']}")
    
    # Step 2: Fraud detection (simulate transaction)
    transaction_data = {
        "transaction_id": "INTEGRATION_TXN",
        "price_per_kg": 45.50 if grade_result['grade'] == 'A' else 35.00,
        "quantity_kg": batch_data['weight_per_unit'] / 1000 * 200,  # Convert to kg
        "transit_days": 3.2,
        "temperature_reported": 24.5,
        "location_jump_km": 45.0,
        "time_since_last_event_hours": 18.5
    }
    
    fraud_result = fraud_detector.detect_fraud(transaction_data)
    print(f"   Step 2 - Fraud Detection: {fraud_result['risk_level']} risk, {fraud_result['is_anomaly']} anomaly")
    
    # Step 3: Demand forecasting
    historical_prices = [45.2, 46.1, 44.8, 47.3, 48.1, 46.9, 47.5, 48.2, 49.1, 47.8, 
                        48.5, 49.3, 50.1, 48.9, 49.7, 50.5, 51.2, 50.0, 50.8, 51.5,
                        52.3, 51.1, 51.9, 52.7, 53.4, 52.2, 53.0, 53.8, 54.5, 53.3]
    
    historical_demand = [850, 870, 840, 890, 910, 880, 900, 920, 940, 910, 
                         930, 950, 970, 940, 960, 980, 1000, 970, 990, 1010,
                         1030, 1000, 1020, 1040, 1060, 1030, 1050, 1070, 1090, 1060]
    
    forecast_result = demand_forecaster.forecast(batch_data['product_type'], historical_prices, historical_demand, 'summer')
    print(f"   Step 3 - Demand Forecast: ${forecast_result['recommended_price']} recommended price")
    
    # Integration summary
    print("   Integration Summary:")
    print(f"     Batch Quality: {grade_result['grade']} grade")
    print(f"     Transaction Risk: {fraud_result['risk_level']}")
    print(f"     Market Recommendation: ${forecast_result['recommended_price']}")
    
    print("✅ AI Integration test completed!")

def run_all_ai_tests():
    """Run all AI module tests"""
    print("🚀 Starting AI Modules Test Suite...\n")
    
    try:
        test_quality_grader()
        print()
        
        test_fraud_detector()
        print()
        
        test_demand_forecaster()
        print()
        
        test_ai_integration()
        print()
        
        print("🎉 All AI module tests completed successfully!")
        
    except Exception as e:
        print(f"❌ AI module test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_ai_tests()
