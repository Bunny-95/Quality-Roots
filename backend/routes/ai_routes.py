"""
Organic Roots AI Routes
API endpoints for AI services and predictions
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from ai.quality_grader import quality_grader
from ai.fraud_detector import fraud_detector
from ai.demand_forecaster import demand_forecaster

router = APIRouter(prefix="/ai", tags=["ai"])

# Pydantic models
class QualityGradingRequest(BaseModel):
    batch_code: str
    product_type: str
    moisture_level: float
    color_score: float
    aroma_score: float
    defect_percentage: float
    weight_per_unit: float

class QualityGradingResponse(BaseModel):
    grade: str
    confidence: float
    quality_score: float
    recommendations: List[str]
    grade_probabilities: Dict[str, float]

class FraudDetectionRequest(BaseModel):
    transaction_id: str = None
    price_per_kg: float
    quantity_kg: float
    transit_days: float
    temperature_reported: float
    location_jump_km: float
    time_since_last_event_hours: float

class FraudDetectionResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    risk_level: str
    flags: List[str]
    confidence: float

class DemandForecastRequest(BaseModel):
    product_type: str
    historical_prices: List[float]
    historical_demand: List[float]
    season: str

class DemandForecastResponse(BaseModel):
    product_type: str
    season: str
    forecast_7_days: List[Dict[str, Any]]
    recommended_price: float
    price_trend: str
    demand_trend: str
    confidence: float
    avg_forecasted_demand: float

@router.post("/grade-quality", response_model=QualityGradingResponse)
async def grade_batch_quality(
    grading_request: QualityGradingRequest,
    db: Session = Depends(get_db)
):
    """Grade the quality of a batch using AI"""
    
    try:
        # Validate product type
        valid_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
        if grading_request.product_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate input ranges
        if not (0 <= grading_request.moisture_level <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Moisture level must be between 0 and 100"
            )
        
        if not (0 <= grading_request.color_score <= 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Color score must be between 0 and 10"
            )
        
        if not (0 <= grading_request.aroma_score <= 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aroma score must be between 0 and 10"
            )
        
        if not (0 <= grading_request.defect_percentage <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Defect percentage must be between 0 and 100"
            )
        
        # Prepare data for AI model
        batch_data = {
            "batch_code": grading_request.batch_code,
            "product_type": grading_request.product_type,
            "moisture_level": grading_request.moisture_level,
            "color_score": grading_request.color_score,
            "aroma_score": grading_request.aroma_score,
            "defect_percentage": grading_request.defect_percentage,
            "weight_per_unit": grading_request.weight_per_unit
        }
        
        # Get AI grading result
        result = quality_grader.grade_batch(batch_data)
        
        return QualityGradingResponse(
            grade=result["grade"],
            confidence=result["confidence"],
            quality_score=result["quality_score"],
            recommendations=result["recommendations"],
            grade_probabilities=result["grade_probabilities"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error grading quality: {str(e)}"
        )

@router.post("/detect-fraud", response_model=FraudDetectionResponse)
async def detect_transaction_fraud(
    fraud_request: FraudDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect fraud in a transaction using AI"""
    
    try:
        # Validate input ranges
        if fraud_request.price_per_kg <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price per kg must be positive"
            )
        
        if fraud_request.quantity_kg <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be positive"
            )
        
        if fraud_request.transit_days < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transit days cannot be negative"
            )
        
        # Prepare data for AI model
        transaction_data = {
            "transaction_id": fraud_request.transaction_id or f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "price_per_kg": fraud_request.price_per_kg,
            "quantity_kg": fraud_request.quantity_kg,
            "transit_days": fraud_request.transit_days,
            "temperature_reported": fraud_request.temperature_reported,
            "location_jump_km": fraud_request.location_jump_km,
            "time_since_last_event_hours": fraud_request.time_since_last_event_hours
        }
        
        # Get AI fraud detection result
        result = fraud_detector.detect_fraud(transaction_data)
        
        return FraudDetectionResponse(
            is_anomaly=result["is_anomaly"],
            anomaly_score=result["anomaly_score"],
            risk_level=result["risk_level"],
            flags=result["flags"],
            confidence=result["confidence"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting fraud: {str(e)}"
        )

@router.post("/forecast", response_model=DemandForecastResponse)
async def forecast_demand(
    forecast_request: DemandForecastRequest,
    db: Session = Depends(get_db)
):
    """Forecast demand and prices using AI"""
    
    try:
        # Validate product type
        valid_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
        if forecast_request.product_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate season
        valid_seasons = ['summer', 'monsoon', 'winter', 'spring']
        if forecast_request.season not in valid_seasons:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid season. Must be one of: {', '.join(valid_seasons)}"
            )
        
        # Validate historical data length
        if len(forecast_request.historical_prices) < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need at least 7 days of historical price data"
            )
        
        if len(forecast_request.historical_demand) < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need at least 7 days of historical demand data"
            )
        
        if len(forecast_request.historical_prices) != len(forecast_request.historical_demand):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Historical prices and demand must have same length"
            )
        
        # Validate price ranges
        for price in forecast_request.historical_prices:
            if price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All historical prices must be positive"
                )
        
        # Validate demand ranges
        for demand in forecast_request.historical_demand:
            if demand <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All historical demand values must be positive"
                )
        
        # Get AI forecast result
        result = demand_forecaster.forecast(
            forecast_request.product_type,
            forecast_request.historical_prices,
            forecast_request.historical_demand,
            forecast_request.season
        )
        
        return DemandForecastResponse(
            product_type=result["product_type"],
            season=result["season"],
            forecast_7_days=result["forecast_7_days"],
            recommended_price=result["recommended_price"],
            price_trend=result["price_trend"],
            demand_trend=result["demand_trend"],
            confidence=result["confidence"],
            avg_forecasted_demand=result["avg_forecasted_demand"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error forecasting demand: {str(e)}"
        )

@router.get("/insights/{product_type}")
async def get_product_insights(
    product_type: str,
    db: Session = Depends(get_db)
):
    """Get pre-computed AI insights for a product type"""
    
    try:
        # Validate product type
        valid_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
        if product_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Get quality grader insights
        quality_importance = quality_grader.get_feature_importance()
        
        # Get fraud detector insights
        fraud_stats = fraud_detector.get_model_stats()
        
        # Get demand forecaster insights
        demand_stats = demand_forecaster.get_model_stats()
        
        # Generate sample historical data for forecast
        sample_prices = [45.2, 46.1, 44.8, 47.3, 48.1, 46.9, 47.5, 48.2, 49.1, 47.8, 
                         48.5, 49.3, 50.1, 48.9, 49.7, 50.5, 51.2, 50.0, 50.8, 51.5,
                         52.3, 51.1, 51.9, 52.7, 53.4, 52.2, 53.0, 53.8, 54.5, 53.3]
        
        sample_demand = [850, 870, 840, 890, 910, 880, 900, 920, 940, 910, 
                        930, 950, 970, 940, 960, 980, 1000, 970, 990, 1010,
                        1030, 1000, 1020, 1040, 1060, 1030, 1050, 1070, 1090, 1060]
        
        sample_forecast = demand_forecaster.forecast(
            product_type, sample_prices, sample_demand, 'summer'
        )
        
        return {
            "product_type": product_type,
            "quality_insights": {
                "feature_importance": quality_importance,
                "model_type": "Random Forest Classifier",
                "target_grades": ["A", "B", "C"]
            },
            "fraud_insights": {
                "model_type": fraud_stats["model_type"],
                "features_monitored": fraud_stats["features"],
                "contamination_rate": fraud_stats["contamination_rate"]
            },
            "demand_insights": {
                "model_type": demand_stats["model_type"],
                "forecast_horizon": demand_stats["forecast_horizon"],
                "sample_forecast": {
                    "recommended_price": sample_forecast["recommended_price"],
                    "price_trend": sample_forecast["price_trend"],
                    "confidence": sample_forecast["confidence"]
                }
            },
            "recommendations": [
                f"Focus on {max(quality_importance, key=quality_importance.get)} for quality improvement",
                "Monitor transaction patterns for fraud detection",
                "Use demand forecasts for production planning"
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting insights: {str(e)}"
        )

@router.get("/models/status")
async def get_ai_models_status(
    db: Session = Depends(get_db)
):
    """Get status of all AI models"""
    
    try:
        return {
            "quality_grader": {
                "model_type": "Random Forest Classifier",
                "is_trained": quality_grader.is_trained,
                "features": quality_grader.feature_columns,
                "target_classes": ["A", "B", "C"]
            },
            "fraud_detector": {
                "model_type": "Isolation Forest",
                "is_trained": fraud_detector.is_trained,
                "features": fraud_detector.feature_columns,
                "contamination_rate": 0.1
            },
            "demand_forecaster": {
                "model_type": "Polynomial Regression",
                "is_trained": demand_forecaster.is_trained,
                "product_types": demand_forecaster.product_types,
                "forecast_horizon": 7
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting model status: {str(e)}"
        )

@router.post("/batch-grade-multiple")
async def grade_multiple_batches(
    batch_requests: List[QualityGradingRequest],
    db: Session = Depends(get_db)
):
    """Grade multiple batches at once"""
    
    try:
        if len(batch_requests) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot process more than 50 batches at once"
            )
        
        results = []
        
        for request in batch_requests:
            try:
                # Convert to dict for grading
                batch_data = {
                    "batch_code": request.batch_code,
                    "product_type": request.product_type,
                    "moisture_level": request.moisture_level,
                    "color_score": request.color_score,
                    "aroma_score": request.aroma_score,
                    "defect_percentage": request.defect_percentage,
                    "weight_per_unit": request.weight_per_unit
                }
                
                result = quality_grader.grade_batch(batch_data)
                result["batch_code"] = request.batch_code
                results.append(result)
            
            except Exception as e:
                results.append({
                    "batch_code": request.batch_code,
                    "error": str(e)
                })
        
        return {
            "total_batches": len(batch_requests),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error grading multiple batches: {str(e)}"
        )

@router.post("/batch-detect-fraud-multiple")
async def detect_fraud_multiple_transactions(
    transaction_requests: List[FraudDetectionRequest],
    db: Session = Depends(get_db)
):
    """Detect fraud in multiple transactions at once"""
    
    try:
        if len(transaction_requests) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot process more than 50 transactions at once"
            )
        
        results = []
        
        for request in transaction_requests:
            try:
                # Convert to dict for fraud detection
                transaction_data = {
                    "transaction_id": request.transaction_id or f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "price_per_kg": request.price_per_kg,
                    "quantity_kg": request.quantity_kg,
                    "transit_days": request.transit_days,
                    "temperature_reported": request.temperature_reported,
                    "location_jump_km": request.location_jump_km,
                    "time_since_last_event_hours": request.time_since_last_event_hours
                }
                
                result = fraud_detector.detect_fraud(transaction_data)
                result["transaction_id"] = transaction_data["transaction_id"]
                results.append(result)
            
            except Exception as e:
                results.append({
                    "transaction_id": request.transaction_id,
                    "error": str(e)
                })
        
        return {
            "total_transactions": len(transaction_requests),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting fraud in multiple transactions: {str(e)}"
        )

@router.get("/quality/feature-importance")
async def get_quality_feature_importance(
    db: Session = Depends(get_db)
):
    """Get feature importance for quality grading model"""
    
    try:
        importance = quality_grader.get_feature_importance()
        
        return {
            "feature_importance": importance,
            "model_type": "Random Forest Classifier",
            "total_features": len(importance),
            "most_important": max(importance, key=importance.get),
            "least_important": min(importance, key=importance.get)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting feature importance: {str(e)}"
        )
