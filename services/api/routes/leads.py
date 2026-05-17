from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from api.database import get_db
from api.schemas import LeadOut

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", response_model=list[LeadOut])
def get_leads(
    tier: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get all leads with optional filtering"""

    query = """
        SELECT
            b.id, b.name, b.city, b.state,
            b.google_rating, b.google_review_count,
            b.website, b.email, b.phone,
            b.latitude, b.longitude,
            ls.score, ls.tier, ls.confidence
        FROM businesses b
        LEFT JOIN lead_scores ls ON b.id = ls.business_id
        WHERE 1=1
    """
    params = {}

    if tier:
        query += " AND ls.tier = :tier"
        params["tier"] = tier

    if city:
        query += " AND b.city ILIKE :city"
        params["city"] = f"%{city}%"

    if min_score:
        query += " AND ls.score >= :min_score"
        params["min_score"] = min_score

    query += " ORDER BY ls.score DESC NULLS LAST"
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    result = db.execute(text(query), params).fetchall()
    return [LeadOut(**dict(row._mapping)) for row in result]


@router.get("/hot", response_model=list[LeadOut])
def get_hot_leads(
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get hot leads only"""
    query = """
        SELECT
            b.id, b.name, b.city, b.state,
            b.google_rating, b.google_review_count,
            b.website, b.email, b.phone,
            b.latitude, b.longitude,
            ls.score, ls.tier, ls.confidence
        FROM businesses b
        LEFT JOIN lead_scores ls ON b.id = ls.business_id
        WHERE ls.tier = 'hot'
        ORDER BY ls.score DESC NULLS LAST
        LIMIT :limit
    """
    result = db.execute(text(query), {"limit": limit}).fetchall()
    return [LeadOut(**dict(row._mapping)) for row in result]

@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    """Get single lead by ID"""

    result = db.execute(text("""
        SELECT
            b.id, b.name, b.city, b.state,
            b.google_rating, b.google_review_count,
            b.website, b.email, b.phone,
            b.latitude, b.longitude,
            ls.score, ls.tier, ls.confidence
        FROM businesses b
        LEFT JOIN lead_scores ls ON b.id = ls.business_id
        WHERE b.id = :id
    """), {"id": lead_id}).fetchone()

    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Lead not found")

    return LeadOut(**dict(result._mapping))


@router.get("/cities/list")
def get_cities(db: Session = Depends(get_db)):
    """Get all cities with lead counts"""

    result = db.execute(text("""
        SELECT
            b.city,
            COUNT(*) as total,
            COUNT(CASE WHEN ls.tier = 'hot' THEN 1 END) as hot,
            ROUND(AVG(ls.score)::numeric, 3) as avg_score
        FROM businesses b
        LEFT JOIN lead_scores ls ON b.id = ls.business_id
        GROUP BY b.city
        ORDER BY hot DESC
    """)).fetchall()

    return [dict(row._mapping) for row in result]