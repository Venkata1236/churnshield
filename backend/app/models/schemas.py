from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RetentionStrategy(str, Enum):
    STANDARD = "STANDARD"
    TARGETED = "TARGETED"
    ESCALATE = "ESCALATE"


class ChurnDirection(str, Enum):
    INCREASES_CHURN = "increases_churn"
    REDUCES_CHURN = "reduces_churn"


class OutcomeStatus(str, Enum):
    PENDING = "PENDING"
    SAVED = "SAVED"
    CHURNED = "CHURNED"


# ── Input Schema ─────────────────────────────────────────────────────────────

class CustomerInput(BaseModel):
    customer_id: str = Field(..., example="7590-VHVEG")
    tenure: int = Field(..., ge=0, le=72, example=2)
    monthly_charges: float = Field(..., gt=0, example=85.0)
    total_charges: float = Field(..., ge=0, example=170.0)
    contract: str = Field(..., example="Month-to-month")
    payment_method: str = Field(..., example="Electronic check")
    internet_service: str = Field(..., example="Fiber optic")
    tech_support: str = Field(..., example="No")
    online_security: str = Field(..., example="No")
    online_backup: str = Field(default="No", example="No")
    device_protection: str = Field(default="No", example="No")
    streaming_tv: str = Field(default="No", example="No")
    streaming_movies: str = Field(default="No", example="No")
    phone_service: str = Field(default="Yes", example="Yes")
    multiple_lines: str = Field(default="No", example="No")
    gender: str = Field(default="Male", example="Male")
    senior_citizen: int = Field(default=0, ge=0, le=1, example=0)
    partner: str = Field(default="No", example="No")
    dependents: str = Field(default="No", example="No")
    paperless_billing: str = Field(default="Yes", example="Yes")


# ── SHAP Feature ─────────────────────────────────────────────────────────────

class SHAPFeature(BaseModel):
    feature: str
    shap_value: float
    direction: ChurnDirection
    plain_english: str


# ── Churn Prediction Output ───────────────────────────────────────────────────

class ChurnPredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    churn_prediction: str
    risk_tier: RiskTier
    top_churn_drivers: list[SHAPFeature]
    retention_signals: list[SHAPFeature]
    proceed_to_retention: bool
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


# ── Offer Details ─────────────────────────────────────────────────────────────

class OfferDetails(BaseModel):
    offer_type: str
    discount_pct: int
    validity_days: int
    conditions: str


# ── Retention Strategy Output ─────────────────────────────────────────────────

class RetentionResponse(BaseModel):
    customer_id: str
    risk_tier: RiskTier
    retention_strategy: RetentionStrategy
    offer_details: OfferDetails
    message_draft: str
    estimated_save_probability: float
    langsmith_trace_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── History ───────────────────────────────────────────────────────────────────

class HistoryRecord(BaseModel):
    id: int
    customer_id: str
    churn_probability: float
    risk_tier: RiskTier
    retention_strategy: Optional[RetentionStrategy] = None
    outcome: OutcomeStatus = OutcomeStatus.PENDING
    predicted_at: datetime

    class Config:
        from_attributes = True


class OutcomeUpdate(BaseModel):
    outcome: OutcomeStatus


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    model_loaded: bool