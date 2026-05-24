from pathlib import Path

import joblib
import pandas as pd

from app.features import FEATURE_COLS, build_evaluation, normalize_input

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "price_model.joblib"

_pipeline = None


def load_model():
    global _pipeline
    if _pipeline is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run scripts/train_model.py first."
            )
        bundle = joblib.load(MODEL_PATH)
        _pipeline = bundle["pipeline"]
    return _pipeline


def predict_fair_price(car_data: dict) -> float:
    pipeline = load_model()
    row = normalize_input(car_data)
    df = pd.DataFrame([row])[FEATURE_COLS]
    return float(pipeline.predict(df)[0])


def evaluate_price(car_data: dict) -> dict:
    listed = float(car_data.get("price", 0))
    if listed <= 0:
        raise ValueError("price must be a positive number")
    fair = predict_fair_price(car_data)
    result = build_evaluation(listed, fair)
    result["city"] = "حلب"
    result["currency"] = car_data.get("currency", "USD")
    return result
