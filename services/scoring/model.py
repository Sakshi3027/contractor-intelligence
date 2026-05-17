import numpy as np
import pandas as pd
import xgboost as xgb
import shap
import mlflow
import mlflow.xgboost
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001"))
MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "models"
MODEL_PATH.mkdir(parents=True, exist_ok=True)


def generate_training_labels(features_df: pd.DataFrame) -> pd.Series:
    """
    Generate initial training labels using heuristics.
    Once real outcome data exists this gets replaced by actual labels.
    """

    score = features_df["composite_score"]

    # Label as good lead if composite score is high
    labels = pd.Series(0, index=features_df.index)
    labels[score >= score.quantile(0.6)] = 1

    return labels


def train_model(features_df: pd.DataFrame, feature_cols: list[str]):
    """Train XGBoost model with MLflow tracking"""

    print("\n🤖 Training XGBoost Lead Scoring Model")
    print("=" * 45)

    # Generate labels
    y = generate_training_labels(features_df)
    X = features_df[feature_cols]

    print(f"Training samples: {len(X)}")
    print(f"Positive labels: {y.sum()} ({y.mean()*100:.1f}%)")
    print(f"Features: {len(feature_cols)}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # MLflow experiment
    mlflow.set_experiment("lead-scoring")

    with mlflow.start_run(run_name="xgboost-v1") as run:

        # Model params
        params = {
            "n_estimators": 100,
            "max_depth": 4,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "eval_metric": "auc",
            "use_label_encoder": False
        }

        # Train model
        model = xgb.XGBClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        # Predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Metrics
        metrics = {
            "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
            "precision": round(precision_score(y_test, y_pred,
                                               zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred,
                                        zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred,
                                  zero_division=0), 4)
        }

        print(f"\n📊 Model Metrics:")
        for k, v in metrics.items():
            print(f"   {k}: {v}")

        # SHAP values
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)

        # Feature importance from SHAP
        shap_importance = pd.DataFrame({
            "feature": feature_cols,
            "importance": np.abs(shap_values).mean(axis=0)
        }).sort_values("importance", ascending=False)

        print(f"\n🔍 Top 5 Features (SHAP):")
        for _, row in shap_importance.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")

        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.log_dict(
            shap_importance.to_dict(orient="records"),
            "shap_importance.json"
        )
        mlflow.xgboost.log_model(model, "model")

        # Save model locally
        model_file = MODEL_PATH / "lead_scorer.json"
        model.save_model(str(model_file))
        print(f"\n💾 Model saved: {model_file}")

        # Save metadata
        metadata = {
            "run_id": run.info.run_id,
            "metrics": metrics,
            "feature_cols": feature_cols,
            "shap_importance": shap_importance.head(10).to_dict(orient="records")
        }
        with open(MODEL_PATH / "model_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"📝 MLflow run ID: {run.info.run_id}")
        print(f"🔗 View at: http://localhost:5001")

        return model, metrics, run.info.run_id