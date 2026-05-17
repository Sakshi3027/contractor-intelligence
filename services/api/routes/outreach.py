from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db
from api.schemas import OutreachOut, OutreachStatusUpdate, OutcomeCreate

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("/", response_model=list[OutreachOut])
def get_outreach(
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all outreach records"""

    query = "SELECT * FROM outreach WHERE 1=1"
    params = {}

    if status:
        query += " AND status = :status"
        params["status"] = status

    query += " ORDER BY created_at DESC LIMIT :limit"
    params["limit"] = limit

    result = db.execute(text(query), params).fetchall()
    return [OutreachOut(**dict(row._mapping)) for row in result]


@router.patch("/{outreach_id}/status")
def update_status(
    outreach_id: str,
    update: OutreachStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update outreach status — sent, opened, replied etc"""

    valid = ["pending", "sent", "delivered", "opened",
             "clicked", "replied", "bounced", "failed"]

    if update.status not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid}"
        )

    db.execute(text("""
        UPDATE outreach
        SET status = :status,
            sent_at = CASE WHEN :status = 'sent'
                THEN NOW() ELSE sent_at END,
            opened_at = CASE WHEN :status = 'opened'
                THEN NOW() ELSE opened_at END,
            replied_at = CASE WHEN :status = 'replied'
                THEN NOW() ELSE replied_at END
        WHERE id = :id
    """), {"status": update.status, "id": outreach_id})
    db.commit()

    return {"message": f"Status updated to {update.status}"}


@router.post("/outcomes")
def record_outcome(
    outcome: OutcomeCreate,
    db: Session = Depends(get_db)
):
    """Record outcome for feedback loop"""

    db.execute(text("""
        INSERT INTO outcomes (
            business_id, outreach_id, outcome_type,
            was_good_lead, conversion_value, notes
        ) VALUES (
            :business_id, :outreach_id, :outcome_type,
            :was_good_lead, :conversion_value, :notes
        )
    """), outcome.model_dump())
    db.commit()

    return {"message": "Outcome recorded successfully"}


@router.get("/stats/summary")
def get_outreach_stats(db: Session = Depends(get_db)):
    """Get outreach funnel statistics"""

    result = db.execute(text("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
            COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
            COUNT(CASE WHEN status = 'opened' THEN 1 END) as opened,
            COUNT(CASE WHEN status = 'replied' THEN 1 END) as replied,
            COUNT(CASE WHEN status = 'bounced' THEN 1 END) as bounced
        FROM outreach
    """)).fetchone()

    return dict(result._mapping)