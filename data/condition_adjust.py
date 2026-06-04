"""
تعديل السعر العادل حسب مواصفات وحالة السيارة (مطابق لحقول الباك إند).

حالة المحرك لها التأثير الأقوى: محرك غاطل → سعر عادل منخفض → السعر المطلوب يبدو غالياً.
"""


def _score(val) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def motor_multiplier(motor: float) -> float:
    """
    تأثير المحرك على السعر العادل (الأهم):
    - 0–10  (غاطل/ميت)     → 25–35% من سعر السوق
    - 20–30 (سيء جداً)     → ~45%
    - 40–50 (يحتاج شغل)    → ~60%
    - 70+   (جيد)          → ~90–108%
    """
    if motor <= 10:
        return 0.28
    if motor <= 20:
        return 0.38
    if motor <= 30:
        return 0.48
    if motor <= 40:
        return 0.58
    if motor <= 50:
        return 0.68
    if motor <= 60:
        return 0.78
    if motor <= 70:
        return 0.88
    if motor <= 80:
        return 0.96
    if motor <= 90:
        return 1.04
    return 1.1


def other_conditions_multiplier(car_data: dict) -> float:
    """باقي الحالات — تأثير أخف من المحرك."""
    mult = 1.0
    keys = [
        ("electricalCondition", 0.12),
        ("oilCondition", 0.08),
        ("chassisCondition", 0.1),
        ("tiresCondition", 0.06),
    ]
    for key, weight in keys:
        s = _score(car_data.get(key))
        if s is not None:
            factor = 0.7 + (s / 100) * 0.35
            mult *= 1.0 + (factor - 1.0) * weight

    smoke = str(car_data.get("engineSmokeLevel", "0"))
    if smoke == "100" or car_data.get("isEngineSmoking") is True:
        mult *= 0.88

    accident = str(car_data.get("accidentHistoryType", "none"))
    acc_level = _score(car_data.get("accidentHistoryLevel")) or 100

    if accident == "full_cut":
        mult *= 0.72 + (acc_level / 100) * 0.1
    elif accident == "half_cut":
        mult *= 0.86 + (acc_level / 100) * 0.08

    return mult


def condition_multiplier(car_data: dict) -> float:
    motor = _score(car_data.get("motorCondition"))

    if motor is not None:
        mult = motor_multiplier(motor)
    else:
        mult = 0.88

    mult *= other_conditions_multiplier(car_data)

    return max(0.22, min(1.15, mult))


def adjust_fair_price_for_specs(base_price: float, car_data: dict) -> float:
    if base_price <= 0:
        return base_price
    return round(base_price * condition_multiplier(car_data), 2)
