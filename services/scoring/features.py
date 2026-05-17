import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def fetch_businesses_for_scoring() -> pd.DataFrame:
    """Fetch all businesses from PostgreSQL for feature engineering"""

    conn = get_postgres_conn()
    try:
        query = """
            SELECT 
                b.id,
                b.google_place_id,
                b.name,
                b.city,
                b.state,
                b.google_rating,
                b.google_review_count,
                b.price_level,
                b.website,
                b.email,
                b.phone,
                b.is_verified,
                b.latitude,
                b.longitude,
                b.created_at,
                -- Outreach history
                COUNT(DISTINCT o.id) as total_outreach,
                COUNT(DISTINCT CASE WHEN o.status = 'replied' 
                    THEN o.id END) as total_replies,
                -- Outcome history  
                COUNT(DISTINCT oc.id) as total_outcomes,
                COUNT(DISTINCT CASE WHEN oc.was_good_lead = true 
                    THEN oc.id END) as positive_outcomes
            FROM businesses b
            LEFT JOIN outreach o ON b.id = o.business_id
            LEFT JOIN outcomes oc ON b.id = oc.business_id
            GROUP BY b.id
        """
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw business data into ML features"""

    features = pd.DataFrame()

    # =====================
    # RATING FEATURES
    # =====================
    features["rating"] = df["google_rating"].fillna(0)
    features["rating_normalized"] = features["rating"] / 5.0
    features["is_high_rated"] = (features["rating"] >= 4.5).astype(int)
    features["is_perfect_rated"] = (features["rating"] == 5.0).astype(int)

    # =====================
    # REVIEW FEATURES
    # =====================
    features["review_count"] = df["google_review_count"].fillna(0)
    features["log_review_count"] = np.log1p(features["review_count"])
    features["has_reviews"] = (features["review_count"] > 0).astype(int)
    features["is_well_reviewed"] = (features["review_count"] >= 10).astype(int)
    features["is_highly_reviewed"] = (features["review_count"] >= 50).astype(int)

    # Rating × Reviews combined signal
    features["rating_review_score"] = (
        features["rating_normalized"] * features["log_review_count"]
    )

    # =====================
    # CONTACT FEATURES
    # =====================
    features["has_website"] = (
        df["website"].notna() & (df["website"] != "")
    ).astype(int)

    features["has_email"] = (
        df["email"].notna() & (df["email"] != "")
    ).astype(int)

    features["has_phone"] = (
        df["phone"].notna() & (df["phone"] != "")
    ).astype(int)

    # Contact completeness score
    features["contact_completeness"] = (
        features["has_website"] +
        features["has_email"] +
        features["has_phone"]
    ) / 3.0

    # =====================
    # VERIFICATION FEATURES
    # =====================
    features["is_verified"] = df["is_verified"].fillna(False).astype(int)

    # =====================
    # WEBSITE QUALITY
    # =====================
    features["has_https"] = df["website"].apply(
        lambda x: 1 if isinstance(x, str) and x.startswith("https") else 0
    )

    features["has_custom_domain"] = df["website"].apply(
        lambda x: 1 if isinstance(x, str) and
        not any(p in x for p in ["wix", "wordpress", "squarespace",
                                  "weebly", "blogspot"]) else 0
    )

    # =====================
    # PRICE LEVEL FEATURES
    # =====================
    features["price_level"] = df["price_level"].fillna(0)
    features["is_premium"] = (features["price_level"] >= 3).astype(int)

    # =====================
    # ENGAGEMENT FEATURES
    # (from outreach history — starts at 0, grows over time)
    # =====================
    features["total_outreach"] = df["total_outreach"].fillna(0)
    features["total_replies"] = df["total_replies"].fillna(0)
    features["reply_rate"] = np.where(
        features["total_outreach"] > 0,
        features["total_replies"] / features["total_outreach"],
        0
    )
    features["positive_outcomes"] = df["positive_outcomes"].fillna(0)

    # =====================
    # COMPOSITE SCORE
    # Initial heuristic before ML takes over
    # =====================
    features["composite_score"] = (
        features["rating_normalized"] * 0.3 +
        features["log_review_count"] / 10 * 0.2 +
        features["contact_completeness"] * 0.2 +
        features["is_verified"] * 0.1 +
        features["has_https"] * 0.1 +
        features["reply_rate"] * 0.1
    )

    # Keep business identifiers
    features["id"] = df["id"]
    features["name"] = df["name"]
    features["city"] = df["city"]

    return features


def get_feature_columns() -> list[str]:
    """Return list of feature column names used for ML"""

    return [
        "rating",
        "rating_normalized",
        "is_high_rated",
        "is_perfect_rated",
        "review_count",
        "log_review_count",
        "has_reviews",
        "is_well_reviewed",
        "is_highly_reviewed",
        "rating_review_score",
        "has_website",
        "has_email",
        "has_phone",
        "contact_completeness",
        "is_verified",
        "has_https",
        "has_custom_domain",
        "price_level",
        "is_premium",
        "total_outreach",
        "total_replies",
        "reply_rate",
        "positive_outcomes",
        "composite_score"
    ]


if __name__ == "__main__":
    print("🔧 Engineering features...")
    df = fetch_businesses_for_scoring()
    print(f"Fetched {len(df)} businesses")

    features = engineer_features(df)
    print(f"\nFeature columns: {len(get_feature_columns())}")
    print("\nSample features:")
    print(features[get_feature_columns()].head())
    print("\nFeature stats:")
    print(features[get_feature_columns()].describe().round(3))