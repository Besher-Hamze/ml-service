from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.model_loader import evaluate_price, load_model

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Car Price Evaluation - Aleppo",
    description="تقييم أسعار السيارات في سوق حلب",
    version="1.1.0",
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
    """مطابق لحقول Car في الباك إند."""
    brand: str
    model: str
    year: int
    price: float = Field(gt=0)
    mileage: Optional[float] = None
    category: Optional[str] = None
    engineType: Optional[str] = None
    engineDisplacement: Optional[float] = None
    horsepower: Optional[float] = None
    cylinders: Optional[float] = None
    torque: Optional[float] = None
    transmission: Optional[str] = None
    driveType: Optional[str] = None
    seatingCapacity: Optional[float] = None
    color: Optional[str] = None
    interiorColor: Optional[str] = None
    imported: Optional[str] = None
    condition: Optional[str] = None
    motorCondition: Optional[str] = None
    electricalCondition: Optional[str] = None
    oilCondition: Optional[str] = None
    chassisCondition: Optional[str] = None
    tiresCondition: Optional[str] = None
    engineSmokeLevel: Optional[str] = None
    isEngineSmoking: Optional[bool] = None
    accidentHistoryType: Optional[str] = None
    accidentHistoryLevel: Optional[str] = None
    currency: str = "USD"


@app.on_event("startup")
def startup():
    try:
        load_model()
    except FileNotFoundError:
        pass


@app.get("/")
def gui():
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="الواجهة غير موجودة")
    return FileResponse(index, media_type="text/html; charset=utf-8")


@app.get("/catalog")
def catalog():
    from data.aleppo_catalog import get_car_catalog
    return get_car_catalog()


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
        return evaluate_price(req.model_dump(exclude_none=True))
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="النموذج غير مدرب بعد")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
