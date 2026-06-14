"""تعديلات خفيفة على السعر بعد التنبؤ — المسافة والسلندرات."""
from __future__ import annotations


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
