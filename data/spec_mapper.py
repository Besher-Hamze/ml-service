"""
تحويل حقول car.json / الباك إند إلى ميزات موحّدة للتدريب والتقييم.
"""

import re

IMPORTED_MAP = {
    "خليجي": "gulf",
    "خليجية": "gulf",
    "اميركي": "american",
    "أميركي": "american",
    "امريكي": "american",
    "أوروبي": "european",
    "اوروبي": "european",
    "محلي": "local",
    "تركي": "turkish",
    "كوري": "korean",
    "صيني": "chinese",
    "ياباني": "japanese",
}


def map_imported(raw: str) -> str:
    s = (raw or "").strip()
    for key, val in IMPORTED_MAP.items():
        if key in s:
            return val
    return "other" if s else "unknown"


def map_color(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return "unknown"
    mapping = {
        "ابيض": "white",
        "أبيض": "white",
        "اسود": "black",
        "أسود": "black",
        "فضي": "silver",
        "رمادي": "gray",
        "كحلي": "navy",
        "ازرق": "blue",
        "أزرق": "blue",
        "احمر": "red",
        "أحمر": "red",
        "بيج": "beige",
        "بني": "brown",
        "ذهبي": "gold",
        "دهبي": "gold",
        "اخضر": "green",
        "أخضر": "green",
    }
    for ar, en in mapping.items():
        if ar in s:
            return en
    return "other"


def parse_cylinders(engine: str) -> int:
    e = (engine or "").strip()
    m = re.search(r"(\d+)\s*سلندر", e)
    if m:
        return int(m.group(1))
    if "8" in e:
        return 8
    if "6" in e:
        return 6
    return 4


def compute_condition_score(car_data: dict) -> float:
    """متوسط مرجّح: المحرك 50%، الباقي 50%."""
    from data.condition_adjust import _score

    motor = _score(car_data.get("motorCondition"))
    others = [
        _score(car_data.get("electricalCondition")),
        _score(car_data.get("oilCondition")),
        _score(car_data.get("chassisCondition")),
        _score(car_data.get("tiresCondition")),
    ]
    others = [s for s in others if s is not None]

    if motor is None and not others:
        return 70.0

    motor_part = motor if motor is not None else 70.0
    other_part = sum(others) / len(others) if others else motor_part
    return round(motor_part * 0.55 + other_part * 0.45, 1)
