"""
كتalog سيارات شائعة في سوق حلب (USD).
الأسعار تقريبية لموديلات مستعملة بحالة جيدة (~2024-2025).
"""

ALEPPO_CITY = "حلب"

# brand -> model -> {category, base_price_usd, year_ref, specs}
CAR_CATALOG = {
    "Toyota": {
        "Corolla": {"category": "sedan", "base": 14000, "year_ref": 2018, "hp": 132, "cc": 1800, "trans": "automatic"},
        "Camry": {"category": "sedan", "base": 22000, "year_ref": 2018, "hp": 178, "cc": 2500, "trans": "automatic"},
        "Yaris": {"category": "hatchback", "base": 11000, "year_ref": 2017, "hp": 106, "cc": 1500, "trans": "automatic"},
        "RAV4": {"category": "suv", "base": 28000, "year_ref": 2019, "hp": 203, "cc": 2500, "trans": "automatic"},
        "Hilux": {"category": "pickup", "base": 32000, "year_ref": 2018, "hp": 163, "cc": 2800, "trans": "manual"},
        "Land Cruiser": {"category": "suv", "base": 65000, "year_ref": 2015, "hp": 362, "cc": 4700, "trans": "automatic"},
    },
    "Kia": {
        "Cerato": {"category": "sedan", "base": 15000, "year_ref": 2019, "hp": 130, "cc": 2000, "trans": "automatic"},
        "Sportage": {"category": "suv", "base": 24000, "year_ref": 2019, "hp": 181, "cc": 2400, "trans": "automatic"},
        "Rio": {"category": "hatchback", "base": 10000, "year_ref": 2018, "hp": 120, "cc": 1400, "trans": "automatic"},
        "Optima": {"category": "sedan", "base": 18000, "year_ref": 2017, "hp": 185, "cc": 2400, "trans": "automatic"},
    },
    "Hyundai": {
        "Elantra": {"category": "sedan", "base": 13000, "year_ref": 2018, "hp": 128, "cc": 2000, "trans": "automatic"},
        "Tucson": {"category": "suv", "base": 23000, "year_ref": 2019, "hp": 185, "cc": 2400, "trans": "automatic"},
        "Accent": {"category": "sedan", "base": 9000, "year_ref": 2017, "hp": 123, "cc": 1600, "trans": "automatic"},
        "Sonata": {"category": "sedan", "base": 17000, "year_ref": 2018, "hp": 185, "cc": 2400, "trans": "automatic"},
    },
    "Nissan": {
        "Sunny": {"category": "sedan", "base": 10000, "year_ref": 2017, "hp": 109, "cc": 1500, "trans": "automatic"},
        "Altima": {"category": "sedan", "base": 16000, "year_ref": 2018, "hp": 179, "cc": 2500, "trans": "automatic"},
        "X-Trail": {"category": "suv", "base": 22000, "year_ref": 2018, "hp": 171, "cc": 2500, "trans": "automatic"},
        "Patrol": {"category": "suv", "base": 55000, "year_ref": 2014, "hp": 400, "cc": 5600, "trans": "automatic"},
    },
    "Mercedes-Benz": {
        "C200": {"category": "sedan", "base": 28000, "year_ref": 2016, "hp": 184, "cc": 2000, "trans": "automatic"},
        "E200": {"category": "sedan", "base": 35000, "year_ref": 2016, "hp": 184, "cc": 2000, "trans": "automatic"},
        "GLC": {"category": "suv", "base": 42000, "year_ref": 2017, "hp": 211, "cc": 2000, "trans": "automatic"},
    },
    "BMW": {
        "320i": {"category": "sedan", "base": 26000, "year_ref": 2016, "hp": 184, "cc": 2000, "trans": "automatic"},
        "520i": {"category": "sedan", "base": 38000, "year_ref": 2016, "hp": 184, "cc": 2000, "trans": "automatic"},
        "X3": {"category": "suv", "base": 40000, "year_ref": 2017, "hp": 252, "cc": 3000, "trans": "automatic"},
    },
    "Peugeot": {
        "301": {"category": "sedan", "base": 11000, "year_ref": 2018, "hp": 115, "cc": 1600, "trans": "manual"},
        "308": {"category": "hatchback", "base": 13000, "year_ref": 2017, "hp": 130, "cc": 1600, "trans": "automatic"},
        "2008": {"category": "suv", "base": 16000, "year_ref": 2019, "hp": 130, "cc": 1200, "trans": "automatic"},
    },
    "Renault": {
        "Logan": {"category": "sedan", "base": 7000, "year_ref": 2016, "hp": 102, "cc": 1600, "trans": "manual"},
        "Symbol": {"category": "sedan", "base": 8000, "year_ref": 2017, "hp": 102, "cc": 1600, "trans": "automatic"},
        "Duster": {"category": "suv", "base": 14000, "year_ref": 2018, "hp": 115, "cc": 1600, "trans": "manual"},
    },
    "Chevrolet": {
        "Cruze": {"category": "sedan", "base": 12000, "year_ref": 2016, "hp": 153, "cc": 1800, "trans": "automatic"},
        "Aveo": {"category": "sedan", "base": 7500, "year_ref": 2015, "hp": 115, "cc": 1600, "trans": "manual"},
        "Captiva": {"category": "suv", "base": 15000, "year_ref": 2015, "hp": 184, "cc": 2400, "trans": "automatic"},
    },
    "Volkswagen": {
        "Passat": {"category": "sedan", "base": 15000, "year_ref": 2016, "hp": 150, "cc": 1800, "trans": "automatic"},
        "Golf": {"category": "hatchback", "base": 14000, "year_ref": 2017, "hp": 150, "cc": 1600, "trans": "automatic"},
        "Tiguan": {"category": "suv", "base": 26000, "year_ref": 2018, "hp": 180, "cc": 2000, "trans": "automatic"},
    },
    "Mitsubishi": {
        "Lancer": {"category": "sedan", "base": 11000, "year_ref": 2015, "hp": 148, "cc": 2000, "trans": "automatic"},
        "Pajero": {"category": "suv", "base": 35000, "year_ref": 2014, "hp": 250, "cc": 3800, "trans": "automatic"},
        "Attrage": {"category": "sedan", "base": 8500, "year_ref": 2018, "hp": 78, "cc": 1200, "trans": "automatic"},
    },
    "Suzuki": {
        "Swift": {"category": "hatchback", "base": 9500, "year_ref": 2018, "hp": 94, "cc": 1200, "trans": "automatic"},
        "Vitara": {"category": "suv", "base": 18000, "year_ref": 2018, "hp": 140, "cc": 1600, "trans": "automatic"},
        "Alto": {"category": "hatchback", "base": 5500, "year_ref": 2016, "hp": 68, "cc": 1000, "trans": "manual"},
    },
    "Skoda": {
        "Octavia": {"category": "sedan", "base": 16000, "year_ref": 2018, "hp": 150, "cc": 1600, "trans": "automatic"},
        "Superb": {"category": "sedan", "base": 22000, "year_ref": 2017, "hp": 190, "cc": 2000, "trans": "automatic"},
    },
    "Ford": {
        "Focus": {"category": "hatchback", "base": 12000, "year_ref": 2016, "hp": 125, "cc": 1600, "trans": "automatic"},
        "Fusion": {"category": "sedan", "base": 14000, "year_ref": 2016, "hp": 181, "cc": 2500, "trans": "automatic"},
        "Explorer": {"category": "suv", "base": 32000, "year_ref": 2015, "hp": 290, "cc": 3500, "trans": "automatic"},
    },
    "Opel": {
        "Astra": {"category": "hatchback", "base": 11000, "year_ref": 2016, "hp": 140, "cc": 1600, "trans": "manual"},
        "Insignia": {"category": "sedan", "base": 15000, "year_ref": 2015, "hp": 170, "cc": 2000, "trans": "automatic"},
    },
    "Daewoo": {
        "Matiz": {"category": "hatchback", "base": 4000, "year_ref": 2010, "hp": 52, "cc": 800, "trans": "manual"},
        "Lanos": {"category": "sedan", "base": 3500, "year_ref": 2008, "hp": 86, "cc": 1500, "trans": "manual"},
    },
}

COLORS = ["أبيض", "أسود", "فضي", "رمادي", "أزرق", "أحمر", "بيج"]
ENGINE_TYPES = ["gasoline", "diesel", "hybrid"]
DRIVE_TYPES = ["FWD", "RWD", "AWD", "4WD"]

# تصنيفات تقييم السعر
PRICE_LABELS = {
    "very_cheap": {"ar": "رخيصة جداً", "min_ratio": 0, "max_ratio": 0.75},
    "cheap": {"ar": "رخيصة", "min_ratio": 0.75, "max_ratio": 0.90},
    "fair": {"ar": "مناسبة", "min_ratio": 0.90, "max_ratio": 1.10},
    "expensive": {"ar": "غالية", "min_ratio": 1.10, "max_ratio": 1.30},
    "very_expensive": {"ar": "غالية جداً", "min_ratio": 1.30, "max_ratio": float("inf")},
}
