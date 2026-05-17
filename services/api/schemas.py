from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class BusinessOut(BaseModel):
    id: UUID
    name: str
    city: str
    state: Optional[str]
    google_rating: Optional[float]
    google_review_count: Optional[int]
    website: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_verified: Optional[bool]
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True


class LeadScoreOut(BaseModel):
    id: UUID
    business_id: UUID
    score: float
    tier: str
    confidence: Optional[float]
    shap_rating_impact: Optional[float]
    shap_review_count_impact: Optional[float]
    shap_website_impact: Optional[float]
    shap_email_impact: Optional[float]
    scored_at: datetime

    class Config:
        from_attributes = True


class LeadOut(BaseModel):
    id: UUID
    name: str
    city: str
    state: Optional[str]
    google_rating: Optional[float]
    google_review_count: Optional[int]
    website: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    score: Optional[float]
    tier: Optional[str]
    confidence: Optional[float]

    class Config:
        from_attributes = True


class OutreachOut(BaseModel):
    id: UUID
    business_id: UUID
    to_email: str
    subject: Optional[str]
    body: Optional[str]
    status: str
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class OutreachStatusUpdate(BaseModel):
    status: str


class OutcomeCreate(BaseModel):
    business_id: str
    outreach_id: Optional[str]
    outcome_type: str
    was_good_lead: bool
    conversion_value: Optional[float]
    notes: Optional[str]


class ModelMetricsOut(BaseModel):
    version: str
    roc_auc: Optional[float]
    precision_score: Optional[float]
    recall_score: Optional[float]
    f1_score: Optional[float]
    training_sample_size: Optional[int]
    is_active: bool
    trained_at: datetime

    class Config:
        from_attributes = True


class PipelineRunOut(BaseModel):
    id: UUID
    workflow_type: Optional[str]
    status: str
    leads_discovered: int
    leads_scored: int
    emails_generated: int
    emails_sent: int
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_businesses: int
    total_scored: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    total_outreach: int
    pending_outreach: int
    sent_outreach: int
    replied_outreach: int
    avg_score: float