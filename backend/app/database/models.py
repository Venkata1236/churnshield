from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


# ── Churn Predictions Table ───────────────────────────────────────────────────

class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    churn_probability: Mapped[float] = mapped_column(Float, nullable=False)
    churn_prediction: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(10), nullable=False)
    top_churn_drivers: Mapped[dict] = mapped_column(JSON, nullable=True)
    retention_signals: Mapped[dict] = mapped_column(JSON, nullable=True)
    customer_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


# ── Retention Strategies Table ────────────────────────────────────────────────

class RetentionRecord(Base):
    __tablename__ = "retention_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    risk_tier: Mapped[str] = mapped_column(String(10), nullable=False)
    retention_strategy: Mapped[str] = mapped_column(String(20), nullable=False)
    offer_details: Mapped[dict] = mapped_column(JSON, nullable=True)
    message_draft: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_save_probability: Mapped[float] = mapped_column(Float, nullable=True)
    langsmith_trace_url: Mapped[str] = mapped_column(String(500), nullable=True)
    outcome: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )