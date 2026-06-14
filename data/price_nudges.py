"""تعديلات خفيفة على السعر بعد التنبؤ — المسافة والسلندرات."""
from __future__ import annotations


def apply_light_mileage_nudge(base_price: float, year: int, mileage: float | None) -> float:
    """تأثير خفيف جداً للمسافة المقطوعة على السعر العادل."""
    if not mileage or mileage <= 0 or base_price <= 0:
        return base_price
    age = max(1, 2026 - int(year))
    expected = age * 12_000
    ratio = mileage / expected
    if ratio > 1.5:
        penalty = min(0.06, (ratio - 1.5) * 0.04)
        return base_price * (1 - penalty)
    if ratio < 0.5:
        bonus = min(0.03, (0.5 - ratio) * 0.04)
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
