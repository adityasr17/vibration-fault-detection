import joblib
import os
import sys

try:
    model_path = os.path.join("models", "scaler.pkl")
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}")
        sys.exit(1)
        
    scaler = joblib.load(model_path)
    print(f"Scaler expects {scaler.n_features_in_} features.")
    print(f"Feature names (if available): {getattr(scaler, 'feature_names_in_', 'Not available')}")
except Exception as e:
    print(f"Error inspecting model: {e}")
