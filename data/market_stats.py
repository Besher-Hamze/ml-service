"""
إحصائيات السوق الحقيقي — السعر العادل حسب ماركة + موديل + سنة.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
STATS_PATH = DATA_DIR / "market_stats.json"

CURRENT_YEAR = 2026
KM_PER_YEAR = 12_000


def _median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    return float(statistics.median(vals))


def build_market_stats(records: list[dict]) -> dict:
    """بناء جداول وسيط الأسعار من الإعلانات الحقيقية."""
    by_bmy: dict[str, dict] = defaultdict(list)
    by_bm: dict[str, dict] = defaultdict(list)

    for r in records:
        price = r["price"]
        key_bmy = f"{r['brand']}|{r['model']}|{r['year']}"
        key_bm = f"{r['brand']}|{r['model']}"
        by_bmy[key_bmy].append(price)
        by_bm[key_bm].append({"year": r["year"], "price": price, "mileage": r.get("mileage", 0)})

    bmy_stats = {}
    for key, prices in by_bmy.items():
        bmy_stats[key] = {
            "median": round(_median(prices), 2),
            "mean": round(statistics.mean(prices), 2),
            "min": round(min(prices), 2),
            "max": round(max(prices), 2),
            "count": len(prices),
        }

    bm_stats = {}
    for key, items in by_bm.items():
        prices = [x["price"] for x in items]
        years = [x["year"] for x in items]
        by_year: dict[str, dict] = defaultdict(list)
        for x in items:
            by_year[str(x["year"])].append(x["price"])

        year_medians = {
            int(y): round(_median(p), 2)
            for y, p in by_year.items()
        }

        bm_stats[key] = {
            "median": round(_median(prices), 2),
            "count": len(items),
            "min_year": min(years),
            "max_year": max(years),
            "by_year": year_medians,
        }

    return {"by_bmy": bmy_stats, "by_bm": bm_stats}


def save_market_stats(records: list[dict]) -> dict:
    stats = build_market_stats(records)
    with STATS_PATH.open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    return stats


def load_market_stats() -> dict:
    if not STATS_PATH.exists():
        return {"by_bmy": {}, "by_bm": {}}
    with STATS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _interp_year_price(by_year: dict[int, float], target_year: int) -> tuple[float, str]:
    """استيفاء السعر بين أقرب سنوات موجودة في السوق."""
    if not by_year:
        return 0.0, "none"

    if target_year in by_year:
        return by_year[target_year], "exact_year"

    years = sorted(by_year.keys())
    lower = [y for y in years if y < target_year]
    upper = [y for y in years if y > target_year]

    if lower and upper:
        y1, y2 = max(lower), min(upper)
        p1, p2 = by_year[y1], by_year[y2]
        if y2 == y1:
            return p1, "exact_year"
        t = (target_year - y1) / (y2 - y1)
        return p1 + t * (p2 - p1), "interpolated"

    if lower:
        y1 = max(lower)
        p1 = by_year[y1]
        years_gap = y1 - target_year
        dep_per_year = max(80, min(250, p1 * 0.04))
        return max(500, p1 - years_gap * dep_per_year), "extrapolated_older"

    y2 = min(upper)
    p2 = by_year[y2]
    years_gap = target_year - y2
    dep_per_year = max(80, min(250, p2 * 0.03))
    return p2 + years_gap * dep_per_year, "extrapolated_newer"


def _mileage_adjustment(year: int, mileage: float | None, base_price: float) -> float:
    if not mileage or mileage <= 0 or base_price <= 0:
        return base_price
    age = max(1, CURRENT_YEAR - year)
    expected = age * KM_PER_YEAR
    ratio = mileage / expected
    if ratio > 1.35:
        penalty = min(0.25, (ratio - 1.35) * 0.15)
        return base_price * (1 - penalty)
    if ratio < 0.65:
        bonus = min(0.08, (0.65 - ratio) * 0.1)
        return base_price * (1 + bonus)
    return base_price


def lookup_market_price(
    brand: str,
    model: str,
    year: int,
    mileage: float | None = None,
) -> tuple[float, str, int]:
    """
    السعر العادل من الإعلانات الحقيقية.
    Returns: (price, source, sample_count)
    """
    stats = load_market_stats()
    key_bmy = f"{brand}|{model}|{year}"
    key_bm = f"{brand}|{model}"

    bm = stats["by_bm"].get(key_bm)
    by_year = {}
    if bm and bm.get("by_year"):
        by_year = {int(y): float(p) for y, p in bm["by_year"].items()}

    if key_bmy in stats["by_bmy"]:
        s = stats["by_bmy"][key_bmy]
        if s["count"] >= 3:
            price = _mileage_adjustment(year, mileage, s["median"])
            return price, "market_exact", s["count"]
        if by_year:
            max_gap = 5
            close = [p for y, p in by_year.items() if abs(y - year) <= max_gap]
            if close:
                price = _mileage_adjustment(year, mileage, _median(close))
                return price, "market_exact_neighbors", s["count"]

    if by_year:
        price, src = _interp_year_price(by_year, year)
        if price > 0:
            price = _mileage_adjustment(year, mileage, price)
            return price, f"market_{src}", bm["count"] if bm else 0

    if bm:
        price = _mileage_adjustment(year, mileage, bm["median"])
        return price, "market_model_avg", bm["count"]

    return 0.0, "none", 0


def enrich_record_features(record: dict) -> dict:
    """ميزات إضافية تساعد النموذج على تمييز السيارات القديمة."""
    year = int(record.get("year", 2018))
    mileage = float(record.get("mileage", 0))
    record["carAge"] = CURRENT_YEAR - year
    record["logMileage"] = round(__import__("math").log1p(max(0, mileage)), 4)
    return record
