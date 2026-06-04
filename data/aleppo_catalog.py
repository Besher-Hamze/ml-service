"""
كتalog سوق حلب — يُحمّل من البيانات الحقيقية (car.json + market.json + model.json).

شغّل أولاً: python scripts/generate_data.py
لإنشاء/تحديث catalog.json ثم استيراد CAR_CATALOG من هنا.
"""
from __future__ import annotations

import json
from pathlib import Path

from data.dataset_loader import (
    ALEPPO_CITY,
    PRICE_LABELS,
    build_catalog,
    compute_fair_prices,
    load_joined_cars,
)

DATA_DIR = Path(__file__).resolve().parent
CATALOG_JSON = DATA_DIR / "catalog.json"

COLORS = ["أبيض", "أسود", "فضي", "رمادي", "أزرق", "أحمر", "بيج", "كحلي", "بني"]
ENGINE_TYPES = ["gasoline", "diesel", "hybrid", "electric"]
DRIVE_TYPES = ["FWD", "RWD", "AWD", "4WD"]


def _load_catalog_from_disk() -> dict:
    if CATALOG_JSON.exists():
        with CATALOG_JSON.open(encoding="utf-8") as f:
            return json.load(f)
    records = compute_fair_prices(load_joined_cars())
    catalog = build_catalog(records)
    with CATALOG_JSON.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    return catalog


def get_car_catalog() -> dict:
    """brand -> model -> {category, base, year_ref, hp, cc, trans, count?}."""
    return _load_catalog_from_disk()


class _CatalogProxy(dict):
    """يسمح بـ CAR_CATALOG['Toyota'] دون تحميل مكرر عند الاستيراد."""

    _cache: dict | None = None

    def _data(self) -> dict:
        if _CatalogProxy._cache is None:
            _CatalogProxy._cache = get_car_catalog()
        return _CatalogProxy._cache

    def __getitem__(self, key):
        return self._data()[key]

    def __iter__(self):
        return iter(self._data())

    def keys(self):
        return self._data().keys()

    def values(self):
        return self._data().values()

    def items(self):
        return self._data().items()

    def get(self, key, default=None):
        return self._data().get(key, default)

    def __len__(self):
        return len(self._data())

    def __contains__(self, key):
        return key in self._data()


CAR_CATALOG = _CatalogProxy()
