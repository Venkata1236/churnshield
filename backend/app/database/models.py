from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    churn_probability: Mapped[float] = mapped_column(Float, nullable=False)
    churn_prediction: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(10), nullable=False)
    top_churn_drivers: Mapped[dict] = mapped_column(JSON, nullable=False)
    retention_signals: Mapped[dict] = mapped_column(JSON, nullable=False)
    proceed_to_retention: Mapped[bool] = mapped_column(nullable=False, default=True)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RetentionResult(Base):
    __tablename__ = "retention_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(10), nullable=False)
    retention_strategy: Mapped[str] = mapped_column(String(20), nullable=False)
    offer_details: Mapped[dict] = mapped_column(JSON, nullable=False)
    message_draft: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_save_probability: Mapped[float] = mapped_column(Float, nullable=False)
    langsmith_trace_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CustomerOutcome(Base):
    __tablename__ = "customer_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False, default="Pending")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)