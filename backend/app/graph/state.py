from typing import Optional
from typing_extensions import TypedDict


class ChurnState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────────
    customer_id: str
    customer_data: dict          # raw CustomerInput fields
    churn_probability: float
    risk_tier: str               # LOW / MEDIUM / HIGH
    top_churn_drivers: list      # from SHAP
    retention_signals: list      # from SHAP

    # ── Routing ───────────────────────────────────────────────────────────────
    retention_strategy: str      # STANDARD / TARGETED / ESCALATE

    # ── Output ────────────────────────────────────────────────────────────────
    offer_details: dict          # offer_type, discount_pct, validity_days, conditions
    message_draft: str           # AI-drafted talking points or customer message
    estimated_save_probability: float

    # ── Observability ─────────────────────────────────────────────────────────
    langsmith_trace_url: Optional[str]