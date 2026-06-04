from data.dataset_loader import PRICE_LABELS
from data.spec_mapper import compute_condition_score, map_color, map_imported

FEATURE_COLS = [
    "brand", "model", "year", "carAge", "logMileage", "mileage", "category",
    "engineType", "engineDisplacement", "horsepower", "cylinders",
    "transmission", "driveType", "seatingCapacity",
    "imported", "color", "conditionScore",
    "motorCondition", "electricalCondition", "oilCondition",
    "chassisCondition", "tiresCondition", "engineSmokeLevel",
    "accidentHistoryType", "accidentHistoryLevel",
]

NUMERIC_DEFAULTS = {
    "year": 2018,
    "carAge": 8,
    "logMileage": 11.3,
    "mileage": 80000,
    "engineDisplacement": 1600,
    "horsepower": 120,
    "cylinders": 4,
    "seatingCapacity": 5,
    "conditionScore": 70,
    "motorCondition": 70,
    "electricalCondition": 70,
    "oilCondition": 70,
    "chassisCondition": 70,
    "tiresCondition": 70,
    "engineSmokeLevel": 0,
    "accidentHistoryLevel": 100,
}

CATEGORICAL_DEFAULTS = {
    "category": "sedan",
    "engineType": "gasoline",
    "transmission": "automatic",
    "driveType": "FWD",
    "accidentHistoryType": "none",
    "imported": "unknown",
    "color": "unknown",
}


def normalize_input(data: dict) -> dict:
    import math

    data = dict(data)
    if data.get("year") and not data.get("carAge"):
        data["carAge"] = 2026 - int(data["year"])
    if data.get("mileage") is not None and not data.get("logMileage"):
        data["logMileage"] = round(math.log1p(max(0, float(data["mileage"]))), 4)
    if not data.get("conditionScore"):
        data["conditionScore"] = compute_condition_score(data)
    if data.get("color") and data["color"] not in (
        "white", "black", "silver", "gray", "blue", "red", "beige", "brown", "green", "gold", "navy", "other", "unknown",
    ):
        data["color"] = map_color(str(data["color"]))
    if data.get("imported") and data["imported"] in ("خليجي", "اميركي", "أميركي"):
        data["imported"] = map_imported(str(data["imported"]))
    if data.get("isEngineSmoking") and not data.get("engineSmokeLevel"):
        data["engineSmokeLevel"] = "100" if data["isEngineSmoking"] else "0"

    out = {}
    for key in FEATURE_COLS:
        val = data.get(key, None)
        if val is None or val == "":
            if key in NUMERIC_DEFAULTS:
                val = NUMERIC_DEFAULTS[key]
            elif key in CATEGORICAL_DEFAULTS:
                val = CATEGORICAL_DEFAULTS[key]
            else:
                val = "unknown"
        if key in NUMERIC_DEFAULTS:
            out[key] = float(val)
        else:
            out[key] = str(val)
    return out


def classify_price_ratio(ratio: float) -> dict:
    for key, meta in PRICE_LABELS.items():
        if meta["min_ratio"] <= ratio < meta["max_ratio"]:
            return {
                "label": key,
                "labelAr": meta["ar"],
                "ratio": round(ratio, 4),
            }
    meta = PRICE_LABELS["very_expensive"]
    return {"label": "very_expensive", "labelAr": meta["ar"], "ratio": round(ratio, 4)}


def build_evaluation(listed_price: float, fair_price: float) -> dict:
    if fair_price <= 0:
        fair_price = 1.0
    ratio = listed_price / fair_price
    classification = classify_price_ratio(ratio)
    diff = listed_price - fair_price
    diff_pct = (ratio - 1) * 100

    return {
        "listedPrice": round(listed_price, 2),
        "fairPrice": round(fair_price, 2),
        "difference": round(diff, 2),
        "differencePercent": round(diff_pct, 1),
        "priceRatio": classification["ratio"],
        "label": classification["label"],
        "labelAr": classification["labelAr"],
        "confidence": "high" if abs(diff_pct) < 40 else "medium",
    }
