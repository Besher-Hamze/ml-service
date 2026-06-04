"""
توليد بيانات التدريب من car.json + market.json + model.json (بيانات حقيقية — حلب).
"""
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.dataset_loader import (  # noqa: E402
    ALEPPO_CITY,
    build_catalog,
    compute_fair_prices,
    load_joined_cars,
)
from data.market_stats import save_market_stats  # noqa: E402

FIELDNAMES = [
    "brand", "model", "year", "carAge", "logMileage",
    "price", "fairPrice", "priceRatio",
    "priceLabel", "priceLabelAr", "mileage", "category", "engineType",
    "engineDisplacement", "horsepower", "cylinders", "transmission", "driveType",
    "seatingCapacity", "imported", "color", "conditionScore", "condition", "currency",
    "motorCondition", "electricalCondition", "oilCondition",
    "chassisCondition", "tiresCondition", "engineSmokeLevel",
    "accidentHistoryType", "accidentHistoryLevel",
]


def to_training_row(r: dict) -> dict:
    return {k: r[k] for k in FIELDNAMES if k in r}


def to_seed_row(r: dict) -> dict:
    skip = {"fairPrice", "priceRatio", "priceLabel", "priceLabelAr", "sourceId", "imported", "city"}
    row = {k: v for k, v in r.items() if k not in skip}
    row["description"] = r.get("description") or f"سيارة {r['brand']} {r['model']} {r['year']} — {ALEPPO_CITY}"
    row["isAvailable"] = True
    row["status"] = "published"
    return row


def main():
    print("Loading real datasets...")
    raw = load_joined_cars()
    print(f"  Valid cars: {len(raw)}")

    records = compute_fair_prices(raw)
    save_market_stats(records)

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)

    csv_path = data_dir / "aleppo_training.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(to_training_row(r) for r in records)

    catalog = build_catalog(records)
    catalog_path = data_dir / "catalog.json"
    with catalog_path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    rng = random.Random(42)
    n_seed = min(150, len(records))
    seed_cars = [to_seed_row(r) for r in rng.sample(records, n_seed)]

    data_out = ROOT.parent / "backend" / "src" / "cars" / "data"
    data_out.mkdir(parents=True, exist_ok=True)

    backend_catalog_path = data_out / "catalog.json"
    with backend_catalog_path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    seed_path = data_out / "aleppo-seed.json"
    with seed_path.open("w", encoding="utf-8") as f:
        json.dump(seed_cars, f, ensure_ascii=False, indent=2)

    labels: dict[str, int] = {}
    for c in records:
        labels[c["priceLabel"]] = labels.get(c["priceLabel"], 0) + 1

    prices = [c["price"] for c in records]
    brands = len(catalog)
    models = sum(len(m) for m in catalog.values())

    print(f"\nDone (real market data):")
    print(f"  Training CSV ({len(records)} rows) -> {csv_path}")
    print(f"  Catalog ({brands} brands, {models} models) -> {catalog_path}")
    print(f"  Backend catalog -> {backend_catalog_path}")
    print(f"  MongoDB seed ({n_seed}) -> {seed_path}")
    print(f"  Label distribution: {labels}")
    print(f"  Price range: ${min(prices):,.0f} - ${max(prices):,.0f}")


if __name__ == "__main__":
    main()
