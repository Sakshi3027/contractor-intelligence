import sys
import os
sys.path.append(str(__import__('pathlib').Path(__file__).resolve().parents[1]))

from scoring.features import (
    fetch_businesses_for_scoring,
    engineer_features,
    get_feature_columns
)
from scoring.model import train_model


def run_training():
    print("🚀 Lead Scoring Model Training Pipeline")
    print("=" * 45)

    # Step 1 — Fetch and engineer features
    print("\n📦 Step 1: Feature Engineering")
    df = fetch_businesses_for_scoring()
    print(f"Fetched {len(df)} businesses")

    features = engineer_features(df)
    feature_cols = get_feature_columns()

    print(f"Engineered {len(feature_cols)} features")

    # Step 2 — Train model
    print("\n🤖 Step 2: Model Training")
    model, metrics, run_id = train_model(features, feature_cols)

    print("\n✅ Training Complete!")
    print(f"   ROC-AUC:   {metrics['roc_auc']}")
    print(f"   Precision: {metrics['precision']}")
    print(f"   Recall:    {metrics['recall']}")
    print(f"   F1:        {metrics['f1']}")
    print(f"\n🔗 MLflow UI: http://localhost:5001")


if __name__ == "__main__":
    run_training()