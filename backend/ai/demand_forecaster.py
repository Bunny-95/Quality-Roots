"""
Organic Roots AI Demand Forecaster
Uses polynomial regression to forecast demand and prices
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RANDOM_STATE, MODEL_DIR

class DemandForecaster:
    """AI-based demand and price forecaster for agricultural products"""
    
    def __init__(self):
        self.models = {}  # One model per product type
        self.scalers = {}  # One scaler per product type
        self.product_types = ['spice', 'coffee', 'tea', 'millet', 'organic']
        self.seasons = ['summer', 'monsoon', 'winter', 'spring']
        self.model_dir = MODEL_DIR / "demand_models"
        self.is_trained = False
        
        # Create model directory if it doesn't exist
        self.model_dir.mkdir(exist_ok=True)
    
    def generate_synthetic_data(self, product_type: str, days: int = 365) -> pd.DataFrame:
        """Generate synthetic historical data for a product type"""
        print(f"🔄 Generating {days} days of synthetic data for {product_type}...")
        
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        # Set base parameters based on product type
        if product_type == 'spice':
            base_price = 80
            base_demand = 1000
            price_volatility = 15
            demand_volatility = 200
            seasonal_factor = 0.3
        elif product_type == 'coffee':
            base_price = 120
            base_demand = 800
            price_volatility = 20
            demand_volatility = 150
            seasonal_factor = 0.4
        elif product_type == 'tea':
            base_price = 60
            base_demand = 1200
            price_volatility = 10
            demand_volatility = 250
            seasonal_factor = 0.5
        elif product_type == 'millet':
            base_price = 40
            base_demand = 600
            price_volatility = 8
            demand_volatility = 100
            seasonal_factor = 0.6
        else:  # organic
            base_price = 150
            base_demand = 400
            price_volatility = 25
            demand_volatility = 80
            seasonal_factor = 0.3
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            
            # Calculate seasonal effect
            day_of_year = current_date.timetuple().tm_yday
            seasonal_effect = np.sin(2 * np.pi * day_of_year / 365.25) * seasonal_factor
            
            # Add some trend
            trend = i * 0.001  # Slight upward trend
            
            # Generate price and demand with seasonal effects
            price = base_price * (1 + seasonal_effect + trend) + np.random.normal(0, price_volatility)
            demand = base_demand * (1 + seasonal_effect * 0.5 + trend) + np.random.normal(0, demand_volatility)
            
            # Ensure positive values
            price = max(10, price)
            demand = max(10, demand)
            
            # Determine season
            month = current_date.month
            if month in [12, 1, 2]:
                season = 'winter'
            elif month in [3, 4, 5]:
                season = 'spring'
            elif month in [6, 7, 8]:
                season = 'summer'
            else:
                season = 'monsoon'
            
            data.append({
                'date': current_date,
                'price': round(price, 2),
                'demand': round(demand, 1),
                'season': season,
                'day_of_year': day_of_year,
                'product_type': product_type
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated synthetic data for {product_type}: price range {df['price'].min():.2f}-{df['price'].max():.2f}")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for training"""
        # Create lag features
        df['price_lag_1'] = df['price'].shift(1)
        df['price_lag_7'] = df['price'].shift(7)
        df['demand_lag_1'] = df['demand'].shift(1)
        df['demand_lag_7'] = df['demand'].shift(7)
        
        # Create moving averages
        df['price_ma_7'] = df['price'].rolling(window=7).mean()
        df['demand_ma_7'] = df['demand'].rolling(window=7).mean()
        
        # Create seasonal features
        df['season_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
        df['season_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
        
        # One-hot encode seasons
        season_dummies = pd.get_dummies(df['season'], prefix='season')
        df = pd.concat([df, season_dummies], axis=1)
        
        # Drop rows with NaN values (due to lag features)
        df = df.dropna()
        
        # Feature columns
        feature_cols = [
            'price_lag_1', 'price_lag_7', 'demand_lag_1', 'demand_lag_7',
            'price_ma_7', 'demand_ma_7', 'season_sin', 'season_cos',
            'season_summer', 'season_monsoon', 'season_winter', 'season_spring'
        ]
        
        X = df[feature_cols].values
        y_price = df['price'].values
        y_demand = df['demand'].values
        
        return X, y_price, y_demand
    
    def train_models(self) -> Dict[str, Any]:
        """Train forecasting models for all product types"""
        print("🧠 Training demand forecasting models...")
        
        results = {}
        
        for product_type in self.product_types:
            print(f"\nTraining model for {product_type}...")
            
            # Generate training data
            df = self.generate_synthetic_data(product_type)
            
            # Prepare features
            X, y_price, y_demand = self.prepare_features(df)
            
            # Split data (80% train, 20% test)
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_price_train, y_price_test = y_price[:split_idx], y_price[split_idx:]
            y_demand_train, y_demand_test = y_demand[:split_idx], y_demand[split_idx:]
            
            # Create polynomial features
            poly = PolynomialFeatures(degree=2, include_bias=False)
            X_train_poly = poly.fit_transform(X_train)
            X_test_poly = poly.transform(X_test)
            
            # Train price model
            price_model = LinearRegression()
            price_model.fit(X_train_poly, y_price_train)
            
            # Train demand model
            demand_model = LinearRegression()
            demand_model.fit(X_train_poly, y_demand_train)
            
            # Evaluate models
            price_pred = price_model.predict(X_test_poly)
            demand_pred = demand_model.predict(X_test_poly)
            
            price_mae = mean_absolute_error(y_price_test, price_pred)
            price_r2 = r2_score(y_price_test, price_pred)
            demand_mae = mean_absolute_error(y_demand_test, demand_pred)
            demand_r2 = r2_score(y_demand_test, demand_pred)
            
            print(f"  Price model - MAE: {price_mae:.2f}, R²: {price_r2:.3f}")
            print(f"  Demand model - MAE: {demand_mae:.1f}, R²: {demand_r2:.3f}")
            
            # Save models
            model_path = self.model_dir / f"{product_type}_price.joblib"
            demand_model_path = self.model_dir / f"{product_type}_demand.joblib"
            poly_path = self.model_dir / f"{product_type}_poly.joblib"
            
            joblib.dump(price_model, model_path)
            joblib.dump(demand_model, demand_model_path)
            joblib.dump(poly, poly_path)
            
            self.models[product_type] = {
                'price': price_model,
                'demand': demand_model,
                'poly': poly
            }
            
            results[product_type] = {
                'price_mae': price_mae,
                'price_r2': price_r2,
                'demand_mae': demand_mae,
                'demand_r2': demand_r2,
                'training_samples': len(X_train)
            }
        
        self.is_trained = True
        print("\n✅ All demand forecasting models trained successfully")
        
        return results
    
    def load_models(self) -> bool:
        """Load trained models from disk"""
        try:
            for product_type in self.product_types:
                price_model_path = self.model_dir / f"{product_type}_price.joblib"
                demand_model_path = self.model_dir / f"{product_type}_demand.joblib"
                poly_path = self.model_dir / f"{product_type}_poly.joblib"
                
                if all(path.exists() for path in [price_model_path, demand_model_path, poly_path]):
                    self.models[product_type] = {
                        'price': joblib.load(price_model_path),
                        'demand': joblib.load(demand_model_path),
                        'poly': joblib.load(poly_path)
                    }
                else:
                    print(f"⚠️ Missing models for {product_type}, training new models...")
                    self.train_models()
                    break
            
            self.is_trained = True
            print("✅ Demand forecaster models loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
    
    def forecast(self, product_type: str, historical_prices: List[float], 
                 historical_demand: List[float], season: str) -> Dict[str, Any]:
        """Forecast demand and price for next 7 days"""
        if not self.is_trained:
            self.load_models()
        
        if product_type not in self.product_types:
            raise ValueError(f"Invalid product type: {product_type}")
        
        if len(historical_prices) < 7 or len(historical_demand) < 7:
            raise ValueError("Need at least 7 days of historical data")
        
        # Get models
        models = self.models[product_type]
        price_model = models['price']
        demand_model = models['demand']
        poly = models['poly']
        
        # Prepare features for forecasting
        forecasts = []
        current_prices = historical_prices.copy()
        current_demand = historical_demand.copy()
        
        # Get current day of year
        current_day = datetime.now().timetuple().tm_yday
        
        for day_ahead in range(1, 8):
            # Calculate features
            price_lag_1 = current_prices[-1]
            price_lag_7 = current_prices[-7] if len(current_prices) >= 7 else current_prices[0]
            demand_lag_1 = current_demand[-1]
            demand_lag_7 = current_demand[-7] if len(current_demand) >= 7 else current_demand[0]
            
            price_ma_7 = np.mean(current_prices[-7:])
            demand_ma_7 = np.mean(current_demand[-7:])
            
            day_of_year = current_day + day_ahead
            season_sin = np.sin(2 * np.pi * day_of_year / 365.25)
            season_cos = np.cos(2 * np.pi * day_of_year / 365.25)
            
            # Season one-hot encoding
            season_features = [0, 0, 0, 0]
            season_idx = ['summer', 'monsoon', 'winter', 'spring'].index(season)
            season_features[season_idx] = 1
            
            # Create feature array
            features = np.array([[
                price_lag_1, price_lag_7, demand_lag_1, demand_lag_7,
                price_ma_7, demand_ma_7, season_sin, season_cos,
                *season_features
            ]])
            
            # Transform features and predict
            features_poly = poly.transform(features)
            price_pred = price_model.predict(features_poly)[0]
            demand_pred = demand_model.predict(features_poly)[0]
            
            # Ensure positive values
            price_pred = max(10, price_pred)
            demand_pred = max(10, demand_pred)
            
            forecasts.append({
                'day': day_ahead,
                'predicted_price': round(price_pred, 2),
                'predicted_demand': round(demand_pred, 1)
            })
            
            # Add predictions to history for next day's forecast
            current_prices.append(price_pred)
            current_demand.append(demand_pred)
        
        # Calculate trend and confidence
        predicted_prices = [f['predicted_price'] for f in forecasts]
        predicted_demand = [f['predicted_demand'] for f in forecasts]
        
        price_trend = "RISING" if predicted_prices[-1] > predicted_prices[0] else "FALLING"
        demand_trend = "RISING" if predicted_demand[-1] > predicted_demand[0] else "FALLING"
        
        # Simple confidence based on historical volatility
        price_volatility = np.std(historical_prices) / np.mean(historical_prices)
        demand_volatility = np.std(historical_demand) / np.mean(historical_demand)
        confidence = max(0.5, 1.0 - (price_volatility + demand_volatility) / 2)
        
        return {
            'product_type': product_type,
            'season': season,
            'forecast_7_days': forecasts,
            'recommended_price': round(np.mean(predicted_prices), 2),
            'price_trend': price_trend,
            'demand_trend': demand_trend,
            'confidence': round(confidence, 2),
            'avg_forecasted_demand': round(np.mean(predicted_demand), 1)
        }
    
    def get_all_product_forecasts(self, season: str) -> Dict[str, Any]:
        """Get forecasts for all product types"""
        all_forecasts = {}
        
        for product_type in self.product_types:
            # Generate sample historical data
            df = self.generate_synthetic_data(product_type, days=30)
            historical_prices = df['price'].tolist()[-30:]
            historical_demand = df['demand'].tolist()[-30:]
            
            try:
                forecast = self.forecast(product_type, historical_prices, historical_demand, season)
                all_forecasts[product_type] = forecast
            except Exception as e:
                print(f"Error forecasting for {product_type}: {e}")
        
        return all_forecasts
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        if not self.is_trained:
            self.load_models()
        
        return {
            "product_types": self.product_types,
            "model_type": "Polynomial Regression (degree 2)",
            "forecast_horizon": 7,
            "features_used": 12
        }

# Global instance
demand_forecaster = DemandForecaster()

def test_demand_forecaster():
    """Test the demand forecaster"""
    print("🧪 Testing Demand Forecaster...")
    
    # Test data
    historical_prices = [45.2, 46.1, 44.8, 47.3, 48.1, 46.9, 47.5, 48.2, 49.1, 47.8, 
                        48.5, 49.3, 50.1, 48.9, 49.7, 50.5, 51.2, 50.0, 50.8, 51.5,
                        52.3, 51.1, 51.9, 52.7, 53.4, 52.2, 53.0, 53.8, 54.5, 53.3]
    
    historical_demand = [850, 870, 840, 890, 910, 880, 900, 920, 940, 910, 
                         930, 950, 970, 940, 960, 980, 1000, 970, 990, 1010,
                         1030, 1000, 1020, 1040, 1060, 1030, 1050, 1070, 1090, 1060]
    
    # Test forecast
    result = demand_forecaster.forecast('coffee', historical_prices, historical_demand, 'summer')
    
    print(f"\nForecast for {result['product_type']} ({result['season']} season):")
    print(f"  Recommended Price: ${result['recommended_price']}")
    print(f"  Price Trend: {result['price_trend']}")
    print(f"  Demand Trend: {result['demand_trend']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Avg Forecasted Demand: {result['avg_forecasted_demand']}")
    
    print("\n7-Day Forecast:")
    for day in result['forecast_7_days']:
        print(f"  Day {day['day']}: ${day['predicted_price']} price, {day['predicted_demand']} demand")
    
    # Test all products
    print("\nAll Product Forecasts:")
    all_forecasts = demand_forecaster.get_all_product_forecasts('summer')
    for product, forecast in all_forecasts.items():
        print(f"  {product}: ${forecast['recommended_price']} recommended price")
    
    print("✅ Demand forecaster test completed!")

if __name__ == "__main__":
    test_demand_forecaster()
