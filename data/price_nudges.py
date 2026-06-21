"""تعديلات على السعر بعد التنبؤ — المسافة، السلندرات، CC، HP، الحالة، نوع الدفع."""
from __future__ import annotations

CONDITION_TYPE_MULT: dict[str, float] = {
    "new": 1.10,
    "used": 1.0,
    "certified": 1.05,
}

DRIVE_TYPE_MULT: dict[str, float] = {
    "FWD": 1.0,
    "RWD": 1.03,
    "AWD": 1.05,
    "4WD": 1.06,
}


def _float(val) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _catalog_hp_cc(brand: str, model: str) -> tuple[float | None, float | None]:
    try:
        from data.aleppo_catalog import get_car_catalog

        entry = get_car_catalog().get(brand, {}).get(model)
        if not entry:
            return None, None
        return _float(entry.get("hp")), _float(entry.get("cc"))
    except Exception:
        return None, None


def apply_condition_type_nudge(base_price: float, car_data: dict) -> float:
    """تأثير حالة الإعلان: جديد / مستعمل / معتمد."""
    if base_price <= 0:
        return base_price
    raw = str(car_data.get("condition", "")).strip().lower()
    mult = CONDITION_TYPE_MULT.get(raw, 1.0)
    return base_price * mult


def apply_drive_type_nudge(base_price: float, car_data: dict) -> float:
    """تأثير نوع الدفع — AWD/4WD أعلى من FWD في سوق حلب."""
    if base_price <= 0:
        return base_price
    drive = str(car_data.get("driveType", "")).strip().upper()
    mult = DRIVE_TYPE_MULT.get(drive, 1.0)
    return base_price * mult


def apply_cc_hp_nudges(base_price: float, car_data: dict) -> float:
    """
    مقارنة CC و HP مع متوسط الموديل في catalog.json.
    محرك أكبر أو أقوى → سعر عادل أعلى (تأثير معتدل).
    """
    if base_price <= 0:
        return base_price

    brand = str(car_data.get("brand", ""))
    model = str(car_data.get("model", ""))
    ref_hp, ref_cc = _catalog_hp_cc(brand, model)
    cc = _float(car_data.get("engineDisplacement"))
    hp = _float(car_data.get("horsepower"))

    mult = 1.0

    if ref_cc and cc and ref_cc > 0:
        ratio = cc / ref_cc
        adj = max(-0.12, min(0.12, (ratio - 1.0) * 0.15))
        mult *= 1.0 + adj

    if ref_hp and hp and ref_hp > 0:
        ratio = hp / ref_hp
        adj = max(-0.12, min(0.12, (ratio - 1.0) * 0.18))
        mult *= 1.0 + adj

    return base_price * mult


def apply_vehicle_spec_nudges(base_price: float, car_data: dict) -> float:
    """CC + HP + condition (new/used) + drive type."""
    price = apply_condition_type_nudge(base_price, car_data)
    price = apply_drive_type_nudge(price, car_data)
    price = apply_cc_hp_nudges(price, car_data)
    return round(price, 2)


def apply_light_mileage_nudge(base_price: float, mileage: float | None) -> float:
    """تأثير خفيف جداً للمسافة — حدود مطلقة بدون ربط بسنة الصنع."""
    if not mileage or mileage <= 0 or base_price <= 0:
        return base_price
    # مسافة عالية جداً → خصم بسيط (حد أقصى ~6%)
    if mileage >= 200_000:
        penalty = min(0.06, (mileage - 200_000) / 500_000 * 0.06)
        return base_price * (1 - penalty)
    # مسافة منخفضة → مكافأة بسيطة (حد أقصى ~3%)
    if mileage <= 60_000:
        bonus = min(0.03, (60_000 - mileage) / 60_000 * 0.03)
        return base_price * (1 + bonus)
    return base_price


def dampen_cylinders_effect(fair_price: float, car_data: dict) -> float:
    """
    السلندرات: تأثير ضعيف ومعكوس — كلما زاد العدد ينخفض السعر العادل قليلاً.
    """
    raw = car_data.get("cylinders")
    if raw is None or raw == "":
        return fair_price
    try:
        cyl = float(raw)
    except (TypeError, ValueError):
        return fair_price
    if cyl <= 4:
        return fair_price
    # ~1.5% لكل سلندر فوق 4، بحد أقصى 8%
    reduction = min(0.08, (cyl - 4) * 0.015)
    return fair_price * (1 - reduction)
