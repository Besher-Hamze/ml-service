"""
تدريب Random Forest لتقدير السعر العادل + حفظ النموذج.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.dataset_loader import PRICE_LABELS  # noqa: E402

FEATURE_COLS = [
    "brand", "model", "year", "carAge", "logMileage", "mileage", "category",
    "engineType", "engineDisplacement", "horsepower", "cylinders",
    "transmission", "driveType", "seatingCapacity",
    "imported", "color", "conditionScore",
    "motorCondition", "electricalCondition", "oilCondition",
    "chassisCondition", "tiresCondition", "engineSmokeLevel",
    "accidentHistoryType", "accidentHistoryLevel",
]

NUMERIC_COLS = [
    "year", "carAge", "logMileage", "mileage", "engineDisplacement", "horsepower",
    "cylinders", "seatingCapacity", "conditionScore",
    "motorCondition", "electricalCondition", "oilCondition",
    "chassisCondition", "tiresCondition", "engineSmokeLevel", "accidentHistoryLevel",
]

CATEGORICAL_COLS = [
    "brand", "model", "category", "engineType", "transmission",
    "driveType", "accidentHistoryType", "imported", "color",
]


def classify_ratio(ratio: float) -> tuple[str, str]:
    for key, meta in PRICE_LABELS.items():
        if meta["min_ratio"] <= ratio < meta["max_ratio"]:
            return key, meta["ar"]
    return "very_expensive", PRICE_LABELS["very_expensive"]["ar"]


def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in NUMERIC_COLS:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    for col in CATEGORICAL_COLS:
        out[col] = out[col].fillna("unknown").astype(str)
    return out


def main():
    csv_path = ROOT / "data" / "aleppo_training.csv"
    if not csv_path.exists():
        print("Training CSV not found. Run generate_data.py first.")
        sys.exit(1)

    df = prepare_df(pd.read_csv(csv_path))
    X = df[FEATURE_COLS]
    # التدريب على السعر الفعلي من السوق الحقيقي
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS),
            ("num", "passthrough", NUMERIC_COLS),
        ],
    )

    model = Pipeline([
        ("prep", preprocessor),
        ("reg", RandomForestRegressor(
            n_estimators=300,
            max_depth=22,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"MAE: ${mae:,.0f}  |  R²: {r2:.3f}")

    models_dir = ROOT / "models"
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / "price_model.joblib"
    joblib.dump({"pipeline": model, "feature_cols": FEATURE_COLS}, model_path)

    meta = {
        "mae": round(mae, 2),
        "r2": round(r2, 4),
        "samples": len(df),
        "price_labels": PRICE_LABELS,
        "city": "حلب",
    }
    with (models_dir / "model_meta.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Model saved -> {model_path}")


if __name__ == "__main__":
    main()
