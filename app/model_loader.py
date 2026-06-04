from pathlib import Path

import joblib
import pandas as pd

from app.features import FEATURE_COLS, build_evaluation, normalize_input
from data.condition_adjust import adjust_fair_price_for_specs
from data.market_stats import lookup_market_price

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


def predict_ml_price(car_data: dict) -> float:
    pipeline = load_model()
    row = normalize_input(car_data)
    df = pd.DataFrame([row])[FEATURE_COLS]
    return float(pipeline.predict(df)[0])


def predict_fair_price(car_data: dict) -> tuple[float, str]:
    """
    السعر العادل: أولوية لإعلانات السوق الحقيقية (نفس الموديل والسنة)،
    ثم النموذج كاحتياطي.
    """
    brand = str(car_data.get("brand", ""))
    model = str(car_data.get("model", ""))
    year = int(car_data.get("year", 2018))
    mileage = car_data.get("mileage")
    mileage_f = float(mileage) if mileage is not None else None

    market_price, source, count = lookup_market_price(brand, model, year, mileage_f)

    ml_price = predict_ml_price(car_data)

    if market_price > 0:
        if source in ("market_exact", "market_exact_neighbors", "market_interpolated"):
            base, src = market_price, source
        elif source in ("market_extrapolated_older", "market_extrapolated_newer"):
            base, src = market_price * 0.75 + ml_price * 0.25, f"blend_{source}"
        else:
            base, src = market_price * 0.6 + ml_price * 0.4, f"blend_{source}"
        return adjust_fair_price_for_specs(base, car_data), f"{src}_adjusted"

    return adjust_fair_price_for_specs(ml_price, car_data), "ml_adjusted"


def evaluate_price(car_data: dict) -> dict:
    listed = float(car_data.get("price", 0))
    if listed <= 0:
        raise ValueError("price must be a positive number")

    fair, source = predict_fair_price(car_data)
    result = build_evaluation(listed, fair)
    result["city"] = "حلب"
    result["currency"] = car_data.get("currency", "USD")
    result["priceSource"] = source
    if source.startswith("market_") or source.startswith("blend_market"):
        result["confidence"] = "high"
    elif source.startswith("blend_"):
        result["confidence"] = "medium"
    else:
        result["confidence"] = "medium"
    return result
