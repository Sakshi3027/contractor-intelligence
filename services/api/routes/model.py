from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db
import json
from pathlib import Path

router = APIRouter(prefix="/model", tags=["model"])

MODEL_PATH = Path(__file__).resolve().parents[3] / "data" / "models"


@router.get("/metadata")
def get_model_metadata():
    """Get current model metadata"""

    metadata_file = MODEL_PATH / "model_metadata.json"
    if not metadata_file.exists():
        return {"error": "No model trained yet"}

    with open(metadata_file) as f:
        return json.load(f)


@router.get("/performance")
def get_model_performance(db: Session = Depends(get_db)):
    """Get model performance history"""

    result = db.execute(text("""
        SELECT * FROM model_versions
        ORDER BY trained_at DESC
        LIMIT 10
    """)).fetchall()

    return [dict(row._mapping) for row in result]


@router.get("/shap/top-features")
def get_top_features():
    """Get top SHAP features from latest model"""

    metadata_file = MODEL_PATH / "model_metadata.json"
    if not metadata_file.exists():
        return {"error": "No model trained yet"}

    with open(metadata_file) as f:
        metadata = json.load(f)

    return {
        "run_id": metadata.get("run_id"),
        "metrics": metadata.get("metrics"),
        "top_features": metadata.get("shap_importance", [])[:10]
    }