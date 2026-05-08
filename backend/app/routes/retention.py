from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import ChurnPrediction, RetentionResult
from app.graph.pipeline import retention_pipeline
from app.models.schemas import RetentionResponse, OfferDetails

router = APIRouter(prefix="/api/v1", tags=["Retention"])


# ── POST /retention-strategy ──────────────────────────────────────────────────

@router.post("/retention-strategy/{customer_id}", response_model=RetentionResponse)
async def get_retention_strategy(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    # Step 1 – Fetch latest prediction from DB
    result = await db.execute(
        select(ChurnPrediction)
        .where(ChurnPrediction.customer_id == customer_id)
        .order_by(desc(ChurnPrediction.predicted_at))
        .limit(1)
    )
    prediction = result.scalar_one_or_none()

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"No prediction found for {customer_id}. Run /predict-churn first.",
        )

    logger.info(
        f"Running retention pipeline for {customer_id} "
        f"(tier={prediction.risk_tier}, prob={prediction.churn_probability:.3f})"
    )

    # Step 2 – Build initial LangGraph state (no customer_data — not in model)
    initial_state = {
        "customer_id": customer_id,
        "churn_probability": prediction.churn_probability,
        "risk_tier": prediction.risk_tier,
        "top_churn_drivers": prediction.top_churn_drivers or [],
        "retention_signals": prediction.retention_signals or [],
        "retention_strategy": "",
        "offer_details": {},
        "message_draft": "",
        "estimated_save_probability": 0.0,
        "langsmith_trace_url": None,
    }

    # Step 3 – Run LangGraph pipeline
    try:
        final_state = await retention_pipeline.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Retention pipeline failed for {customer_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Retention pipeline failed: {str(e)}",
        )

    # Step 4 – Build LangSmith trace URL
    langsmith_url = (
        final_state["langsmith_trace_url"]
        if final_state.get("langsmith_trace_url")
        else None
    )

    # Step 5 – Save retention record to DB
    try:
        offer = final_state.get("offer_details", {})
        record = RetentionResult(
            customer_id=customer_id,
            risk_tier=final_state["risk_tier"],
            retention_strategy=final_state["retention_strategy"],
            offer_details=offer,
            message_draft=final_state.get("message_draft", ""),
            estimated_save_probability=final_state.get("estimated_save_probability", 0.0),
            langsmith_trace_url=langsmith_url,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.info(f"Retention record saved for {customer_id}")
    except Exception as e:
        await db.rollback()
        logger.error(f"DB save failed for retention record {customer_id}: {e}")

    # Step 6 – Return structured response
    offer_data = final_state.get("offer_details", {})

    return RetentionResponse(
        customer_id=customer_id,
        risk_tier=final_state["risk_tier"],
        retention_strategy=final_state["retention_strategy"],
        offer_details=OfferDetails(
            offer_type=offer_data.get("offer_type", "Standard Offer"),
            discount_pct=offer_data.get("discount_pct", 10),
            validity_days=offer_data.get("validity_days", 30),
            conditions=offer_data.get("conditions", "Terms and conditions apply."),
        ),
        message_draft=final_state.get("message_draft", ""),
        estimated_save_probability=final_state.get("estimated_save_probability", 0.0),
        langsmith_trace_url=langsmith_url,
    )


# ── GET /retention-strategy/{customer_id} ────────────────────────────────────

@router.get("/retention-strategy/{customer_id}", response_model=RetentionResponse)
async def get_saved_retention(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RetentionResult)
        .where(RetentionResult.customer_id == customer_id)
        .order_by(desc(RetentionResult.created_at))
        .limit(1)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No retention strategy found for {customer_id}.",
        )

    offer = record.offer_details or {}

    return RetentionResponse(
        customer_id=record.customer_id,
        risk_tier=record.risk_tier,
        retention_strategy=record.retention_strategy,
        offer_details=OfferDetails(
            offer_type=offer.get("offer_type", "Standard Offer"),
            discount_pct=offer.get("discount_pct", 10),
            validity_days=offer.get("validity_days", 30),
            conditions=offer.get("conditions", "Terms and conditions apply."),
        ),
        message_draft=record.message_draft or "",
        estimated_save_probability=record.estimated_save_probability or 0.0,
        langsmith_trace_url=record.langsmith_trace_url,
        created_at=record.created_at,
    )