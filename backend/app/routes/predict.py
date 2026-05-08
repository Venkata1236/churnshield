from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import ChurnPrediction
from app.ml.predict import model_manager
from app.models.schemas import CustomerInput, ChurnPredictionResponse

router = APIRouter(prefix="/api/v1", tags=["Prediction"])


# ── POST /predict-churn ───────────────────────────────────────────────────────

@router.post("/predict-churn", response_model=ChurnPredictionResponse)
async def predict_churn(
    payload: CustomerInput,
    db: AsyncSession = Depends(get_db),
):
    if not model_manager.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Train the model first.",
        )

    try:
        result = model_manager.predict(payload.model_dump())
    except Exception as e:
        logger.error(f"Prediction error for {payload.customer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    try:
        record = ChurnPrediction(
            customer_id=result["customer_id"],
            churn_probability=result["churn_probability"],
            churn_prediction=result["churn_prediction"],
            risk_tier=result["risk_tier"].value,
            top_churn_drivers=result["top_churn_drivers"],
            retention_signals=result["retention_signals"],
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.info(f"Prediction saved to DB for customer: {payload.customer_id}")
    except Exception as e:
        await db.rollback()
        logger.error(f"DB save failed for {payload.customer_id}: {e}")

    return ChurnPredictionResponse(**result)


# ── GET /predict-churn/{customer_id} ─────────────────────────────────────────

@router.get("/predict-churn/{customer_id}", response_model=ChurnPredictionResponse)
async def get_prediction(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, desc

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
            detail=f"No prediction found for customer {customer_id}",
        )

    return ChurnPredictionResponse(
        customer_id=record.customer_id,
        churn_probability=record.churn_probability,
        churn_prediction=record.churn_prediction,
        risk_tier=record.risk_tier,
        top_churn_drivers=record.top_churn_drivers or [],
        retention_signals=record.retention_signals or [],
        proceed_to_retention=record.churn_probability >= 0.4,
        predicted_at=record.predicted_at,
    )