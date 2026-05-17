from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db
from api.schemas import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    """Get overall system summary"""

    result = db.execute(text("""
        SELECT
            COUNT(DISTINCT b.id) as total_businesses,
            COUNT(DISTINCT ls.id) as total_scored,
            COUNT(DISTINCT CASE WHEN ls.tier = 'hot'
                THEN b.id END) as hot_leads,
            COUNT(DISTINCT CASE WHEN ls.tier = 'warm'
                THEN b.id END) as warm_leads,
            COUNT(DISTINCT CASE WHEN ls.tier = 'cold'
                THEN b.id END) as cold_leads,
            COUNT(DISTINCT o.id) as total_outreach,
            COUNT(DISTINCT CASE WHEN o.status = 'pending'
                THEN o.id END) as pending_outreach,
            COUNT(DISTINCT CASE WHEN o.status = 'sent'
                THEN o.id END) as sent_outreach,
            COUNT(DISTINCT CASE WHEN o.status = 'replied'
                THEN o.id END) as replied_outreach,
            ROUND(AVG(ls.score)::numeric, 3) as avg_score
        FROM businesses b
        LEFT JOIN lead_scores ls ON b.id = ls.business_id
        LEFT JOIN outreach o ON b.id = o.business_id
    """)).fetchone()

    return AnalyticsSummary(**dict(result._mapping))


@router.get("/scores/distribution")
def get_score_distribution(db: Session = Depends(get_db)):
    """Get score distribution by tier and city"""

    result = db.execute(text("""
        SELECT
            ls.tier,
            b.city,
            COUNT(*) as count,
            ROUND(AVG(ls.score)::numeric, 3) as avg_score,
            ROUND(MIN(ls.score)::numeric, 3) as min_score,
            ROUND(MAX(ls.score)::numeric, 3) as max_score
        FROM lead_scores ls
        JOIN businesses b ON ls.business_id = b.id
        GROUP BY ls.tier, b.city
        ORDER BY avg_score DESC
    """)).fetchall()

    return [dict(row._mapping) for row in result]


@router.get("/shap/features")
def get_shap_importance(db: Session = Depends(get_db)):
    """Get average SHAP feature importance across all leads"""

    result = db.execute(text("""
        SELECT
            ROUND(AVG(shap_rating_impact)::numeric, 4)
                as avg_rating_impact,
            ROUND(AVG(shap_review_count_impact)::numeric, 4)
                as avg_review_impact,
            ROUND(AVG(shap_website_impact)::numeric, 4)
                as avg_website_impact,
            ROUND(AVG(shap_email_impact)::numeric, 4)
                as avg_email_impact
        FROM lead_scores
    """)).fetchone()

    return dict(result._mapping)