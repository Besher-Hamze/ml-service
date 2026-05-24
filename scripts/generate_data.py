"""
توليد بيانات تدريب لسوق سيارات حلب.
يُنتج CSV للتدريب + JSON لبذر قاعدة البيانات.
"""
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.aleppo_catalog import (  # noqa: E402
    ALEPPO_CITY,
    CAR_CATALOG,
    COLORS,
    DRIVE_TYPES,
    ENGINE_TYPES,
    PRICE_LABELS,
)


def depreciation_factor(year: int, ref_year: int) -> float:
    """انخفاض السعر ~8% سنوياً بعد سنة المرجع."""
    diff = ref_year - year
    if diff <= 0:
        return 1.0 + abs(diff) * 0.03  # سيارات أحدث أغلى قليلاً
    return max(0.25, 1.0 - diff * 0.08)


def mileage_factor(km: int, year: int) -> float:
    """كل 15,000 كم ≈ -3% من السعر."""
    age = 2025 - year
    expected_km = max(km, age * 12000)
    excess = max(0, expected_km - age * 12000)
    return max(0.5, 1.0 - (excess / 15000) * 0.03)


def condition_factor(scores: dict) -> float:
    avg = sum(scores.values()) / len(scores)
    return 0.5 + (avg / 100) * 0.5


def random_condition_scores() -> dict:
    return {
        "motorCondition": random.choice(range(40, 101, 10)),
        "electricalCondition": random.choice(range(50, 101, 10)),
        "oilCondition": random.choice(range(50, 101, 10)),
        "chassisCondition": random.choice(range(40, 101, 10)),
        "tiresCondition": random.choice(range(30, 101, 10)),
    }


def accident_factor(accident_type: str, level: int) -> float:
    if accident_type == "none":
        return 1.0
    if accident_type == "half_cut":
        return 0.75 - (100 - level) / 100 * 0.15
    return 0.55 - (100 - level) / 100 * 0.20


def compute_fair_price(entry: dict) -> float:
    spec = entry["spec"]
    scores = entry["scores"]
    dep = depreciation_factor(entry["year"], spec["year_ref"])
    mil = mileage_factor(entry["mileage"], entry["year"])
    cond = condition_factor(scores)
    acc = accident_factor(entry["accidentHistoryType"], entry["accidentHistoryLevel"])
    smoke_penalty = 0.85 if entry["engineSmokeLevel"] == 100 else 1.0
    hp_bonus = 1.0 + (spec["hp"] - 100) / 1000
    return round(spec["base"] * dep * mil * cond * acc * smoke_penalty * hp_bonus, 2)


def classify_price_ratio(ratio: float) -> tuple[str, str]:
    for key, meta in PRICE_LABELS.items():
        if meta["min_ratio"] <= ratio < meta["max_ratio"]:
            return key, meta["ar"]
    return "very_expensive", PRICE_LABELS["very_expensive"]["ar"]


def generate_car(rng: random.Random, force_ratio: float | None = None) -> dict:
    brand = rng.choice(list(CAR_CATALOG.keys()))
    model = rng.choice(list(CAR_CATALOG[brand].keys()))
    spec = CAR_CATALOG[brand][model]

    year = rng.randint(max(2005, spec["year_ref"] - 12), min(2024, spec["year_ref"] + 3))
    age = 2025 - year
    mileage = rng.randint(max(5000, age * 8000), max(15000, age * 22000))

    scores = random_condition_scores()
    accident_type = rng.choices(
        ["none", "half_cut", "full_cut"],
        weights=[0.72, 0.20, 0.08],
    )[0]
    accident_level = rng.choice(range(30, 101, 10)) if accident_type != "none" else 100
    engine_smoke = rng.choices([0, 100], weights=[0.92, 0.08])[0]

    entry = {
        "brand": brand,
        "model": model,
        "year": year,
        "mileage": mileage,
        "category": spec["category"],
        "engineType": rng.choice(ENGINE_TYPES if spec["cc"] > 1500 else ["gasoline"]),
        "engineDisplacement": spec["cc"],
        "horsepower": spec["hp"] + rng.randint(-5, 5),
        "transmission": spec["trans"],
        "driveType": rng.choice(DRIVE_TYPES),
        "seatingCapacity": rng.choice([4, 5, 7]),
        "color": rng.choice(COLORS),
        "condition": "used",
        "currency": "USD",
        "city": ALEPPO_CITY,
        "scores": scores,
        "motorCondition": scores["motorCondition"],
        "electricalCondition": scores["electricalCondition"],
        "oilCondition": scores["oilCondition"],
        "chassisCondition": scores["chassisCondition"],
        "tiresCondition": scores["tiresCondition"],
        "engineSmokeLevel": engine_smoke,
        "accidentHistoryType": accident_type,
        "accidentHistoryLevel": accident_level,
        "spec": spec,
    }

    fair_price = compute_fair_price(entry)

    if force_ratio is not None:
        ratio = force_ratio
    else:
        ratio = rng.choices(
            [0.65, 0.82, 0.98, 1.18, 1.45],
            weights=[0.12, 0.18, 0.40, 0.22, 0.08],
        )[0]
        ratio *= rng.uniform(0.97, 1.03)

    listed_price = round(fair_price * ratio, 2)
    label_key, label_ar = classify_price_ratio(ratio)

    car = {
        "brand": brand,
        "model": model,
        "year": year,
        "price": listed_price,
        "fairPrice": fair_price,
        "priceRatio": round(ratio, 4),
        "priceLabel": label_key,
        "priceLabelAr": label_ar,
        "mileage": mileage,
        "category": spec["category"],
        "engineType": entry["engineType"],
        "engineDisplacement": spec["cc"],
        "horsepower": entry["horsepower"],
        "transmission": spec["trans"],
        "driveType": entry["driveType"],
        "seatingCapacity": entry["seatingCapacity"],
        "color": entry["color"],
        "condition": "used",
        "currency": "USD",
        "motorCondition": str(entry["motorCondition"]),
        "electricalCondition": str(entry["electricalCondition"]),
        "oilCondition": str(entry["oilCondition"]),
        "chassisCondition": str(entry["chassisCondition"]),
        "tiresCondition": str(entry["tiresCondition"]),
        "engineSmokeLevel": str(entry["engineSmokeLevel"]),
        "accidentHistoryType": accident_type,
        "accidentHistoryLevel": str(accident_level),
        "description": f"سيارة {brand} {model} {year} معروضة في {ALEPPO_CITY}",
        "isAvailable": True,
        "status": "published",
    }
    return car


def main():
    rng = random.Random(42)
    n_train = 3000
    n_seed = 150

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)

    cars: list[dict] = []
    for i in range(n_train):
        if i % 600 == 0:
            forced = [0.68, 0.85, 1.0, 1.2, 1.5][(i // 600) % 5]
            cars.append(generate_car(rng, force_ratio=forced * rng.uniform(0.95, 1.05)))
        else:
            cars.append(generate_car(rng))

    csv_path = data_dir / "aleppo_training.csv"
    fieldnames = [
        "brand", "model", "year", "price", "fairPrice", "priceRatio",
        "priceLabel", "priceLabelAr", "mileage", "category", "engineType",
        "engineDisplacement", "horsepower", "transmission", "driveType",
        "seatingCapacity", "color", "condition", "currency",
        "motorCondition", "electricalCondition", "oilCondition",
        "chassisCondition", "tiresCondition", "engineSmokeLevel",
        "accidentHistoryType", "accidentHistoryLevel",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({k: c[k] for k in fieldnames} for c in cars)

    seed_cars = cars[:n_seed]
    seed_path = ROOT.parent / "backend" / "src" / "cars" / "data" / "aleppo-seed.json"
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    with seed_path.open("w", encoding="utf-8") as f:
        json.dump(seed_cars, f, ensure_ascii=False, indent=2)

    labels = {}
    for c in cars:
        labels[c["priceLabel"]] = labels.get(c["priceLabel"], 0) + 1

    print(f"Generated {len(cars)} training records -> {csv_path}")
    print(f"Seed subset ({n_seed}) -> {seed_path}")
    print("Label distribution:", labels)
    print(f"Price range: ${min(c['price'] for c in cars):,.0f} - ${max(c['price'] for c in cars):,.0f}")


if __name__ == "__main__":
    main()
