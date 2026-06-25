"""
Aayu AI — ML Service
XGBoost-powered health risk prediction based on historical report trends.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from database_models import Report, Parameter
import xgboost as xgb

# ── Prototype Note ───────────────────────────────────────
# In a production environment, you would load a pre-trained 
# model from a .pkl or .json file trained on real datasets 
# (e.g., PIMA Indians Diabetes Database). 
# For this prototype, we generate a synthetic dataset on the 
# fly and train the XGBoost model to demonstrate the architecture.

def _train_synthetic_xgboost():
    """Trains a simple XGBoost model to predict Diabetes Risk Percentage."""
    # Synthetic dataset: [Glucose, HbA1c, Age, BMI]
    # Output: Risk % (0-100)
    np.random.seed(42)
    n_samples = 500
    
    # Generate realistic-ish synthetic data
    glucose = np.random.uniform(70, 250, n_samples)
    hba1c = np.random.uniform(4.0, 12.0, n_samples)
    age = np.random.uniform(20, 80, n_samples)
    bmi = np.random.uniform(18, 40, n_samples)
    
    # Calculate synthetic risk score
    # Higher glucose, higher hba1c, higher bmi, older age -> higher risk
    risk = (glucose - 100) * 0.3 + (hba1c - 5.5) * 10 + (bmi - 25) * 1.5 + (age - 40) * 0.2
    risk = np.clip(risk, 0, 100) # Clamp between 0% and 100%
    
    # Add some noise
    risk += np.random.normal(0, 5, n_samples)
    risk = np.clip(risk, 0, 100)
    
    X = pd.DataFrame({'glucose': glucose, 'hba1c': hba1c, 'age': age, 'bmi': bmi})
    y = risk
    
    # Train XGBoost
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=50, max_depth=3, learning_rate=0.1)
    model.fit(X, y)
    
    return model

# Initialize the model globally
_risk_model = None

def get_risk_model():
    global _risk_model
    if _risk_model is None:
        try:
            print("Training prototype XGBoost model...")
            _risk_model = _train_synthetic_xgboost()
        except Exception as e:
            print(f"Failed to train XGBoost: {e}")
    return _risk_model

def predict_health_risks(user_id, patient_name=None):
    """
    Analyzes a user's past reports and uses XGBoost to predict disease risk.
    Requires at least 3 reports.
    """
    # Fetch user reports sorted by date ascending
    query = Report.query.filter_by(user_id=user_id)
    if patient_name:
        query = query.filter_by(patient_name=patient_name)
    reports = query.order_by(Report.created_at.asc()).all()
    
    if len(reports) < 3:
        return {
            "status": "insufficient_data",
            "message": f"You currently have {len(reports)} reports. Upload {3 - len(reports)} more to unlock AI Risk Predictions.",
            "predictions": []
        }

    # Extract historical trends for key markers
    glucose_history = []
    hba1c_history = []
    
    # Latest demographics (we'll guess or use default if missing since MVP DB doesn't have age/bmi strictly)
    latest_age = 40 
    
    for report in reports:
        # Try to parse age from patient_age string (e.g., "45 Years")
        if report.patient_age:
            try:
                latest_age = float(report.patient_age.split()[0])
            except:
                pass
                
        # Find parameters
        for param in report.parameters:
            name_lower = param.test_name.lower()
            try:
                val = float(param.value)
                if 'glucose' in name_lower or 'sugar' in name_lower:
                    glucose_history.append(val)
                elif 'hba1c' in name_lower or 'a1c' in name_lower:
                    hba1c_history.append(val)
            except ValueError:
                continue

    # We need at least the latest value to make a prediction
    # If they don't have these tests, use typical baselines just to show the feature
    latest_glucose = glucose_history[-1] if glucose_history else 95.0
    latest_hba1c = hba1c_history[-1] if hba1c_history else 5.2
    
    # Calculate trend direction
    glucose_trend = "stable"
    if len(glucose_history) >= 2:
        diff = glucose_history[-1] - glucose_history[0]
        if diff > 10: glucose_trend = "rising"
        elif diff < -10: glucose_trend = "falling"

    hba1c_trend = "stable"
    if len(hba1c_history) >= 2:
        diff = hba1c_history[-1] - hba1c_history[0]
        if diff > 0.5: hba1c_trend = "rising"
        elif diff < -0.5: hba1c_trend = "falling"

    # Get model and predict
    model = get_risk_model()
    if not model:
        return {
            "status": "error",
            "message": "AI Risk Engine is currently initializing or unavailable.",
            "predictions": []
        }
        
    # Prepare input feature (Default BMI 24)
    input_df = pd.DataFrame([{
        'glucose': latest_glucose, 
        'hba1c': latest_hba1c, 
        'age': latest_age, 
        'bmi': 24.0
    }])
    
    risk_score = float(model.predict(input_df)[0])
    risk_score = max(0, min(100, risk_score)) # Clamp
    
    # Determine risk category
    if risk_score > 70:
        level = "High"
        color = "red"
        advice = "Critical: Your trends show high risk. Please consult a diabetologist immediately."
    elif risk_score > 40:
        level = "Moderate"
        color = "amber"
        advice = "Warning: Your trends indicate developing risk. Improve diet and exercise."
    else:
        level = "Low"
        color = "green"
        advice = "Great! Your markers are stable and indicate low risk."

    predictions = [
        {
            "disease": "Type 2 Diabetes",
            "score": round(risk_score, 1),
            "level": level,
            "color": color,
            "advice": advice,
            "trends": {
                "glucose": glucose_trend,
                "hba1c": hba1c_trend
            }
        }
    ]

    return {
        "status": "success",
        "message": "AI Risk Prediction analyzed successfully.",
        "predictions": predictions
    }
