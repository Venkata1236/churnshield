from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import ChurnPrediction, RetentionResult, CustomerOutcome
from app.models.schemas import HistoryRecord, OutcomeUpdate, OutcomeStatus

router = APIRouter(prefix="/api/v1", tags=["History"])


async def _get_latest_retention(db: AsyncSession, customer_id: str):
    result = await db.execute(
        select(RetentionResult)
        .where(RetentionResult.customer_id == customer_id)
        .order_by(desc(RetentionResult.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_latest_outcome(db: AsyncSession, customer_id: str):
    result = await db.execute(
        select(CustomerOutcome)
        .where(CustomerOutcome.customer_id == customer_id)
        .order_by(desc(CustomerOutcome.updated_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


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

    history = []
    for r in records:
        retention = await _get_latest_retention(db, r.customer_id)
        outcome_row = await _get_latest_outcome(db, r.customer_id)

        outcome_value = outcome_row.outcome.upper() if outcome_row else OutcomeStatus.PENDING.value
        try:
            outcome = OutcomeStatus(outcome_value)
        except ValueError:
            outcome = OutcomeStatus.PENDING

        history.append(
            HistoryRecord(
                id=r.id,
                customer_id=r.customer_id,
                churn_probability=r.churn_probability,
                risk_tier=r.risk_tier,
                retention_strategy=retention.retention_strategy if retention else None,
                outcome=outcome,
                predicted_at=r.predicted_at,
            )
        )

    logger.info(f"Fetched {len(history)} history records (tier={risk_tier})")
    return history


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

    retention = await _get_latest_retention(db, customer_id)
    outcome_row = await _get_latest_outcome(db, customer_id)

    outcome_value = outcome_row.outcome.upper() if outcome_row else OutcomeStatus.PENDING.value
    try:
        outcome = OutcomeStatus(outcome_value)
    except ValueError:
        outcome = OutcomeStatus.PENDING

    return HistoryRecord(
        id=record.id,
        customer_id=record.customer_id,
        churn_probability=record.churn_probability,
        risk_tier=record.risk_tier,
        retention_strategy=retention.retention_strategy if retention else None,
        outcome=outcome,
        predicted_at=record.predicted_at,
    )


@router.patch("/history/{customer_id}/outcome", response_model=HistoryRecord)
async def update_outcome(
    customer_id: str,
    payload: OutcomeUpdate,
    db: AsyncSession = Depends(get_db),
):
    pred_result = await db.execute(
        select(ChurnPrediction)
        .where(ChurnPrediction.customer_id == customer_id)
        .order_by(desc(ChurnPrediction.predicted_at))
        .limit(1)
    )
    pred = pred_result.scalar_one_or_none()

    if not pred:
        raise HTTPException(
            status_code=404,
            detail=f"No churn prediction found for customer {customer_id}",
        )

    retention = await _get_latest_retention(db, customer_id)

    outcome_result = await db.execute(
        select(CustomerOutcome)
        .where(CustomerOutcome.customer_id == customer_id)
        .order_by(desc(CustomerOutcome.updated_at))
        .limit(1)
    )
    outcome_row = outcome_result.scalar_one_or_none()

    if outcome_row:
        outcome_row.outcome = payload.outcome.value
    else:
        outcome_row = CustomerOutcome(
            customer_id=customer_id,
            outcome=payload.outcome.value,
        )
        db.add(outcome_row)

    await db.flush()

    logger.info(f"Outcome updated for {customer_id}: {payload.outcome.value}")

    return HistoryRecord(
        id=pred.id,
        customer_id=pred.customer_id,
        churn_probability=pred.churn_probability,
        risk_tier=pred.risk_tier,
        retention_strategy=retention.retention_strategy if retention else None,
        outcome=payload.outcome,
        predicted_at=pred.predicted_at,
    )


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

    logger.info(f"Deleted {len(records)} records for customer {customer_id}")
    return {"message": f"Deleted {len(records)} records for {customer_id}"}