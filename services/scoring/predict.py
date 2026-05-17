import os
import json
import numpy as np
import xgboost as xgb
import shap
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "models"


def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def load_model():
    """Load trained XGBoost model"""
    model = xgb.XGBClassifier()
    model.load_model(str(MODEL_PATH / "lead_scorer.json"))

    with open(MODEL_PATH / "model_metadata.json") as f:
        metadata = json.load(f)

    return model, metadata


def assign_tier(score: float) -> str:
    """Assign lead tier based on score"""
    if score >= 0.7:
        return "hot"
    elif score >= 0.4:
        return "warm"
    else:
        return "cold"


def save_scores(scores: list[dict]):
    """Save lead scores to PostgreSQL"""

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            for score in scores:
                cur.execute("""
                    INSERT INTO lead_scores (
                        business_id, score, score_version,
                        model_version, confidence, tier,
                        shap_rating_impact, shap_review_count_impact,
                        shap_website_impact, shap_email_impact,
                        feature_vector
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT DO NOTHING
                """, (
                    score["business_id"],
                    score["score"],
                    score["score_version"],
                    score["model_version"],
                    score["confidence"],
                    score["tier"],
                    score.get("shap_rating_impact", 0),
                    score.get("shap_review_count_impact", 0),
                    score.get("shap_website_impact", 0),
                    score.get("shap_email_impact", 0),
                    json.dumps(score.get("feature_vector", {}))
                ))
            conn.commit()
    finally:
        conn.close()


def run_scoring():
    """Score all businesses and save results"""

    from scoring.features import (
        fetch_businesses_for_scoring,
        engineer_features,
        get_feature_columns
    )

    print("\n🎯 Running Lead Scoring")
    print("=" * 40)

    # Load model
    model, metadata = load_model()
    feature_cols = metadata["feature_cols"]
    model_version = metadata["run_id"][:8]
    print(f"Model version: {model_version}")

    # Get features
    df = fetch_businesses_for_scoring()
    features = engineer_features(df)
    X = features[feature_cols]

    # Predict scores
    scores_prob = model.predict_proba(X)[:, 1]

    # SHAP explanations
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Build score records
    score_records = []
    results = []

    for i, (_, row) in enumerate(features.iterrows()):
        score = float(scores_prob[i])
        tier = assign_tier(score)

        record = {
            "business_id": str(row["id"]),
            "score": score,
            "score_version": "v1",
            "model_version": model_version,
            "confidence": score,
            "tier": tier,
            "shap_rating_impact": float(shap_values[i][feature_cols.index("rating")]),
            "shap_review_count_impact": float(shap_values[i][feature_cols.index("review_count")]),
            "shap_website_impact": float(shap_values[i][feature_cols.index("has_website")]),
            "shap_email_impact": float(shap_values[i][feature_cols.index("has_email")]),
            "feature_vector": {col: float(X.iloc[i][col]) for col in feature_cols[:5]}
        }

        score_records.append(record)
        results.append({
            "name": row["name"],
            "city": row["city"],
            "score": round(score, 3),
            "tier": tier
        })

    # Save to database
    save_scores(score_records)

    # Print results sorted by score
    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n{'Rank':<5} {'Score':<8} {'Tier':<8} {'City':<12} Name")
    print("-" * 70)
    for i, r in enumerate(results, 1):
        tier_emoji = {"hot": "🔥", "warm": "🌤", "cold": "❄️"}.get(r["tier"], "")
        print(f"{i:<5} {r['score']:<8} {tier_emoji}{r['tier']:<8} "
              f"{r['city']:<12} {r['name'][:35]}")

    hot = sum(1 for r in results if r["tier"] == "hot")
    warm = sum(1 for r in results if r["tier"] == "warm")
    cold = sum(1 for r in results if r["tier"] == "cold")

    print(f"\n📊 Summary:")
    print(f"   🔥 Hot leads:  {hot}")
    print(f"   🌤 Warm leads: {warm}")
    print(f"   ❄️  Cold leads: {cold}")


if __name__ == "__main__":
    run_scoring()