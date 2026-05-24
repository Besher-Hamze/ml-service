from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.model_loader import evaluate_price, load_model

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Car Price Evaluation - Aleppo",
    description="تقييم أسعار السيارات في سوق حلب باستخدام Random Forest",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class CarEvaluateRequest(BaseModel):
    brand: str
    model: str
    year: int
    price: float = Field(gt=0)
    mileage: float | None = None
    category: str | None = None
    engineType: str | None = None
    engineDisplacement: float | None = None
    horsepower: float | None = None
    transmission: str | None = None
    driveType: str | None = None
    seatingCapacity: float | None = None
    motorCondition: str | None = None
    electricalCondition: str | None = None
    oilCondition: str | None = None
    chassisCondition: str | None = None
    tiresCondition: str | None = None
    engineSmokeLevel: str | None = None
    accidentHistoryType: str | None = None
    accidentHistoryLevel: str | None = None
    currency: str = "USD"


@app.on_event("startup")
def startup():
    try:
        load_model()
    except FileNotFoundError:
        pass


@app.get("/")
def gui():
    """واجهة عربية لاختبار النموذج."""
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="الواجهة غير موجودة")
    return FileResponse(index, media_type="text/html; charset=utf-8")


@app.get("/catalog")
def catalog():
    """كتalog الماركات والموديلات لسوق حلب."""
    from data.aleppo_catalog import CAR_CATALOG

    out = {}
    for brand, models in CAR_CATALOG.items():
        out[brand] = {}
        for model, spec in models.items():
            out[brand][model] = {
                "category": spec["category"],
                "year_ref": spec["year_ref"],
                "hp": spec["hp"],
                "cc": spec["cc"],
                "trans": spec["trans"],
                "base": spec["base"],
            }
    return out


@app.get("/health")
def health():
    try:
        load_model()
        return {"status": "ok", "modelLoaded": True, "city": "حلب"}
    except FileNotFoundError:
        return {"status": "ok", "modelLoaded": False, "city": "حلب"}


@app.post("/evaluate")
def evaluate(req: CarEvaluateRequest):
    try:
        return evaluate_price(req.model_dump())
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="النموذج غير مدرب بعد")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
