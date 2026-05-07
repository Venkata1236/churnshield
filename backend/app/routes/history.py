from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import ChurnPrediction, RetentionResult
from app.models.schemas import HistoryRecord, OutcomeUpdate, OutcomeStatus

router = APIRouter(prefix="/api/v1", tags=["History"])


# ── GET /history ──────────────────────────────────────────────────────────────

@router.get("/history", response_model=list[HistoryRecord])
async def get_history(
    risk_tier: str | None = Query(default=None, description="Filter by LOW, MEDIUM, HIGH"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(ChurnPrediction).order_by(desc(ChurnPrediction.predicted_at))

    if risk_tier:
        query = query.where(ChurnPrediction.risk_tier == risk_tier.upper())

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    records = result.scalars().all()

    logger.info(f"Fetched {len(records)} history records (tier={risk_tier})")

    return [
        HistoryRecord(
            id=r.id,
            customer_id=r.customer_id,
            churn_probability=r.churn_probability,
            risk_tier=r.risk_tier,
            retention_strategy=_get_retention_strategy(r.customer_id),
            outcome=OutcomeStatus.PENDING,
            predicted_at=r.predicted_at,
        )
        for r in records
    ]


# ── GET /history/{customer_id} ────────────────────────────────────────────────

@router.get("/history/{customer_id}", response_model=HistoryRecord)
async def get_customer_history(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChurnPrediction)
        .where(ChurnPrediction.customer_id == customer_id)
        .order_by(desc(ChurnPrediction.predicted_at))
        .limit(1)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No history found for customer {customer_id}",
        )

    return HistoryRecord(
        id=record.id,
        customer_id=record.customer_id,
        churn_probability=record.churn_probability,
        risk_tier=record.risk_tier,
        outcome=OutcomeStatus.PENDING,
        predicted_at=record.predicted_at,
    )


# ── PATCH /history/{customer_id}/outcome ──────────────────────────────────────

@router.patch("/history/{customer_id}/outcome", response_model=HistoryRecord)
async def update_outcome(
    customer_id: str,
    payload: OutcomeUpdate,
    db: AsyncSession = Depends(get_db),
):
    # Get latest retention record for this customer
    result = await db.execute(
        select(RetentionResult)
        .where(RetentionResult.customer_id == customer_id)
        .order_by(desc(RetentionResult.created_at))
        .limit(1)
    )
    retention = result.scalar_one_or_none()

    if not retention:
        raise HTTPException(
            status_code=404,
            detail=f"No retention record found for customer {customer_id}",
        )

    retention.outcome = payload.outcome.value
    await db.flush()
    logger.info(f"Outcome updated for {customer_id}: {payload.outcome.value}")

    # Fetch churn prediction for response
    pred_result = await db.execute(
        select(ChurnPrediction)
        .where(ChurnPrediction.customer_id == customer_id)
        .order_by(desc(ChurnPrediction.predicted_at))
        .limit(1)
    )
    pred = pred_result.scalar_one_or_none()

    return HistoryRecord(
        id=pred.id,
        customer_id=pred.customer_id,
        churn_probability=pred.churn_probability,
        risk_tier=pred.risk_tier,
        retention_strategy=retention.retention_strategy,
        outcome=payload.outcome,
        predicted_at=pred.predicted_at,
    )


# ── DELETE /history/{customer_id} ─────────────────────────────────────────────

@router.delete("/history/{customer_id}")
async def delete_history(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChurnPrediction)
        .where(ChurnPrediction.customer_id == customer_id)
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No records found for customer {customer_id}",
        )

    for record in records:
        await db.delete(record)

    await db.flush()
    logger.info(f"Deleted {len(records)} records for customer {customer_id}")
    return {"message": f"Deleted {len(records)} records for {customer_id}"}


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_retention_strategy(customer_id: str) -> str | None:
    """Placeholder — retention strategy fetched separately via /retention-strategy."""
    return None