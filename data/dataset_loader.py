"""
تحميل ودمج البيانات الحقيقية: car.json + market.json + model.json
"""
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

ALEPPO_CITY = "حلب"

PRICE_LABELS = {
    "very_cheap": {"ar": "رخيصة جداً", "min_ratio": 0, "max_ratio": 0.75},
    "cheap": {"ar": "رخيصة", "min_ratio": 0.75, "max_ratio": 0.90},
    "fair": {"ar": "مناسبة", "min_ratio": 0.90, "max_ratio": 1.10},
    "expensive": {"ar": "غالية", "min_ratio": 1.10, "max_ratio": 1.30},
    "very_expensive": {"ar": "غالية جداً", "min_ratio": 1.30, "max_ratio": float("inf")},
}

# حالة السيارة العربية → درجة 0-100
STATUS_SCORES = {
    "ممتازة": 90,
    "ممتاز": 90,
    "جيدة": 70,
    "جيد": 70,
    "متوسطة": 50,
    "مقبولة": 40,
    "سيئة": 20,
}

# بخ / دهان → نوع حادث
SPRAY_NONE = {"لا يوجد", "لايوجد", "خالية", "خالي", "بدون", "لا يوجد"}
SPRAY_LIGHT = {"قطعة واحدة", "قطعتين", "زنار", "زنار نضافة", "زنار نظافة", "بخ زنار"}
SPRAY_HEAVY = {"3قطع", "4 قطع", "4قطع", "قطع", "على الفحص"}


def _load_json(name: str) -> dict:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def parse_mileage(distance: str) -> int | None:
    if not distance:
        return None
    s = str(distance).strip().lower()
    s = s.replace("كيلومتر", "").replace("كم", "").replace("m", "").strip()
    nums = re.findall(r"\d+", s)
    if not nums:
        return None
    val = int(nums[0])
    if val > 500_000:
        return None
    return val


def parse_year(year_val) -> int | None:
    try:
        y = int(str(year_val).strip())
        if 1980 <= y <= 2026:
            return y
    except (ValueError, TypeError):
        pass
    return None


def map_engine_type(gasoline: str) -> str:
    g = (gasoline or "").strip()
    if "ديزل" in g or "ديزيل" in g:
        return "diesel"
    if "هايبرد" in g or "هجين" in g:
        return "hybrid"
    if "كهرب" in g:
        return "electric"
    return "gasoline"


def map_transmission(trans: str) -> str:
    t = (trans or "").strip().lower()
    if "يدوي" in t or "مانيوال" in t:
        return "manual"
    return "automatic"


def map_spray(spray: str) -> tuple[str, int]:
    """نوع الحادث + مستوى (0-100)."""
    s = (spray or "").strip()
    if not s or any(k in s for k in SPRAY_NONE) or s in SPRAY_NONE:
        return "none", 100
    if any(k in s for k in SPRAY_HEAVY) or "3قط" in s or "4 قط" in s or "4قط" in s:
        return "full_cut", 40
    if any(k in s for k in SPRAY_LIGHT) or "قطع" in s or "زنار" in s:
        return "half_cut", 60
    if "فحص" in s:
        return "half_cut", 50
    return "none", 80


def map_status_score(status: str) -> int:
    s = (status or "").strip()
    for key, score in STATUS_SCORES.items():
        if key in s:
            return score
    return 70


def infer_category(model_name: str, brand: str) -> str:
    n = (model_name + " " + brand).lower()
    if any(x in n for x in ("land cruiser", "patrol", "prado", "rav", "sportage", "tucson",
                            "x-trail", "x5", "x3", "q5", "q7", "glc", "pajero", "vitara",
                            "suv", "4x4", "jeep", "renegade", "compass", "tahoe", "yukon")):
        return "suv"
    if any(x in n for x in ("hilux", "f150", "silverado", "pickup", "sierra", "ram")):
        return "pickup"
    if any(x in n for x in ("golf", "swift", "rio", "yaris", "i10", "matiz", "alto")):
        return "hatchback"
    return "sedan"


def classify_price_ratio(ratio: float) -> tuple[str, str]:
    for key, meta in PRICE_LABELS.items():
        if meta["min_ratio"] <= ratio < meta["max_ratio"]:
            return key, meta["ar"]
    return "very_expensive", PRICE_LABELS["very_expensive"]["ar"]


def load_joined_cars() -> list[dict]:
    """دمج السيارات مع الماركة والموديل."""
    raw_cars = _load_json("car.json")["data"]
    markets = {m["id"]: m["name"] for m in _load_json("market.json")["data"]}
    models = {m["id"]: {"name": m["name"], "market_id": m["market_id"]}
              for m in _load_json("model.json")["data"]}

    records = []
    for c in raw_cars:
        price = c.get("price")
        if not price or price < 300 or price > 250_000:
            continue

        model_info = models.get(c.get("model_id"))
        if not model_info:
            continue

        brand = markets.get(c.get("market_id")) or markets.get(model_info["market_id"])
        if not brand:
            continue

        year = parse_year(c.get("year"))
        if not year:
            continue

        mileage = parse_mileage(c.get("distance", ""))
        if mileage is None:
            age = max(1, 2025 - year)
            mileage = age * 15_000

        status_score = map_status_score(c.get("status", ""))
        accident_type, accident_level = map_spray(c.get("spray", ""))

        from data.spec_mapper import map_color, map_imported, parse_cylinders

        brand_clean = brand.strip()
        model_clean = model_info["name"].strip()
        cylinders = parse_cylinders(c.get("engine", ""))

        cond_row = {
            "motorCondition": str(status_score),
            "electricalCondition": str(status_score),
            "oilCondition": str(max(50, status_score - 10)),
            "chassisCondition": str(accident_level if accident_type != "none" else status_score),
            "tiresCondition": str(max(40, status_score - 15)),
            "engineSmokeLevel": "0",
            "accidentHistoryType": accident_type,
            "accidentHistoryLevel": str(accident_level),
        }
        from data.spec_mapper import compute_condition_score

        age = 2026 - year
        record = {
            "sourceId": c.get("id"),
            "brand": brand_clean,
            "model": model_clean,
            "year": year,
            "carAge": age,
            "logMileage": round(__import__("math").log1p(max(0, mileage)), 4),
            "price": float(price),
            "mileage": mileage,
            "category": infer_category(model_clean, brand_clean),
            "engineType": map_engine_type(c.get("gasoline", "")),
            "engineDisplacement": cylinders * 400,
            "horsepower": 100 + cylinders * 25,
            "cylinders": cylinders,
            "transmission": map_transmission(c.get("transmission", "")),
            "driveType": "FWD",
            "seatingCapacity": 5,
            "color": map_color(c.get("color", "")),
            "imported": map_imported(c.get("imported", "")),
            "conditionScore": compute_condition_score(cond_row),
            "condition": "used",
            "currency": "USD",
            **cond_row,
            "importedRaw": (c.get("imported") or "").strip(),
            "description": (c.get("description") or f"{brand_clean} {model_clean} {year}").strip(),
            "city": ALEPPO_CITY,
        }
        records.append(record)

    return records


def compute_fair_prices(records: list[dict]) -> list[dict]:
    """
    السعر العادل = وسيط أسعار نفس (ماركة + موديل + سنة).
    يُستخدم لتصنيف السعر (رخيص/مناسب/غالي).
    """
    from collections import defaultdict

    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in records:
        key = (r["brand"], r["model"], r["year"])
        groups[key].append(r["price"])

    medians = {k: sorted(v)[len(v) // 2] for k, v in groups.items()}

    out = []
    for r in records:
        key = (r["brand"], r["model"], r["year"])
        fair = medians.get(key, r["price"])
        ratio = r["price"] / fair if fair > 0 else 1.0
        label_key, label_ar = classify_price_ratio(ratio)
        row = {**r}
        row["fairPrice"] = round(fair, 2)
        row["priceRatio"] = round(ratio, 4)
        row["priceLabel"] = label_key
        row["priceLabelAr"] = label_ar
        out.append(row)
    return out


def build_catalog(records: list[dict]) -> dict:
    """كتalog للواجهة من البيانات الحقيقية."""
    from collections import defaultdict

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in records:
        groups[(r["brand"], r["model"])].append(r)

    catalog = {}
    for (brand, model), items in sorted(groups.items()):
        prices = [x["price"] for x in items]
        years = [x["year"] for x in items]
        sample = items[0]

        by_year: dict[str, list[float]] = defaultdict(list)
        for x in items:
            by_year[str(x["year"])].append(x["price"])
        year_prices = {
            y: int(statistics.median(p))
            for y, p in by_year.items()
        }

        if brand not in catalog:
            catalog[brand] = {}
        catalog[brand][model] = {
            "category": sample["category"],
            "year_ref": int(sorted(years)[len(years) // 2]),
            "hp": int(sample["horsepower"]),
            "cc": int(sample["engineDisplacement"]),
            "trans": sample["transmission"],
            "base": int(sorted(prices)[len(prices) // 2]),
            "count": len(items),
            "min_year": min(years),
            "max_year": max(years),
            "by_year": year_prices,
        }
    return catalog
