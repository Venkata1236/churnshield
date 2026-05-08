from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
import json

from app.core.config import settings
from app.graph.state import ChurnState


# ── LLM Setup ─────────────────────────────────────────────────────────────────

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
    model_kwargs={"response_format": {"type": "json_object"}},
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _format_drivers(drivers: list) -> str:
    return "\n".join(
        f"- {d['plain_english']} (SHAP: {d['shap_value']:.3f})"
        for d in drivers[:3]
    )


# ── Node 1: RiskRouter ────────────────────────────────────────────────────────

def risk_router(state: ChurnState) -> ChurnState:
    tier = state["risk_tier"]
    if tier == "HIGH":
        strategy = "ESCALATE"
    elif tier == "MEDIUM":
        strategy = "TARGETED"
    else:
        strategy = "STANDARD"
    logger.info(f"RiskRouter: {state['customer_id']} → {strategy}")
    return {"retention_strategy": strategy}


# ── Node 2: StandardOfferNode ─────────────────────────────────────────────────

def standard_offer_node(state: ChurnState) -> ChurnState:
    offer = {
        "offer_type": "Loyalty Reward",
        "discount_pct": 10,
        "validity_days": 30,
        "conditions": "Applicable on next billing cycle. Cannot be combined with other offers.",
    }
    logger.info(f"StandardOfferNode: loyalty offer for {state['customer_id']}")
    return {
        "offer_details": offer,
        "estimated_save_probability": 0.85,
    }


# ── Node 3: TargetedOfferNode ─────────────────────────────────────────────────

def targeted_offer_node(state: ChurnState) -> ChurnState:
    drivers_text = _format_drivers(state["top_churn_drivers"])
    prob = state["churn_probability"]

    system_prompt = """You are a telecom retention specialist at Airtel India.
Create personalized retention offers that directly address why a customer might leave.
Always return valid JSON only."""

    user_prompt = f"""Top churn drivers:
{drivers_text}

Churn probability: {prob:.1%}

Create a targeted retention offer. Return JSON with exactly these keys:
{{
  "offer_type": "string – specific offer name",
  "discount_pct": integer – 15 to 30,
  "validity_days": integer – 30 to 90,
  "conditions": "string – offer conditions",
  "reasoning": "string – why this offer addresses the churn driver"
}}"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    offer = json.loads(response.content)
    reasoning = offer.pop("reasoning", "")
    logger.info(f"TargetedOfferNode: {state['customer_id']} – {offer['offer_type']} | {reasoning}")

    return {
        "offer_details": offer,
        "estimated_save_probability": 0.65,
    }


# ── Node 4: EscalateNode ──────────────────────────────────────────────────────

def escalate_node(state: ChurnState) -> ChurnState:
    drivers_text = _format_drivers(state["top_churn_drivers"])
    prob = state["churn_probability"]

    system_prompt = """You are a senior retention manager at Airtel India.
Prepare escalation briefs for retention specialists before high-risk customer calls.
Always return valid JSON only."""

    user_prompt = f"""High-Risk Customer – Escalation Brief

Top churn drivers:
{drivers_text}

Churn probability: {prob:.1%} – CRITICAL

Generate an escalation package. Return JSON with exactly these keys:
{{
  "offer_type": "string – premium retention offer name",
  "discount_pct": integer – 25 to 40,
  "validity_days": integer – 60 to 90,
  "conditions": "string – offer conditions",
  "escalation_brief": "string – 2-3 sentence brief for the specialist",
  "urgency": "CRITICAL"
}}"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    offer = json.loads(response.content)
    logger.info(f"EscalateNode: {state['customer_id']} – CRITICAL escalation prepared")

    return {
        "offer_details": offer,
        "estimated_save_probability": 0.45,
    }


# ── Node 5: MessageDrafter ────────────────────────────────────────────────────

def message_drafter_node(state: ChurnState) -> ChurnState:
    strategy = state["retention_strategy"]
    offer = state["offer_details"]
    drivers_text = _format_drivers(state["top_churn_drivers"])

    if strategy == "STANDARD":
        system_prompt = """You are a friendly customer success agent at Airtel India.
Write warm, brief customer messages. Return valid JSON only."""

        user_prompt = f"""Write a friendly SMS/WhatsApp message for a loyal customer.

Offer: {offer['offer_type']} – {offer['discount_pct']}% off for {offer['validity_days']} days

Return JSON:
{{
  "message_draft": "string – friendly 2-3 sentence customer message"
}}"""

    elif strategy == "TARGETED":
        system_prompt = """You are a retention agent at Airtel India.
Write persuasive but honest retention messages. Return valid JSON only."""

        user_prompt = f"""Write a personalized retention message addressing the customer's concerns.

Why they might leave:
{drivers_text}

Offer prepared: {offer['offer_type']} – {offer['discount_pct']}% off
Validity: {offer['validity_days']} days

Return JSON:
{{
  "message_draft": "string – personalized 3-4 sentence message addressing their specific concern"
}}"""

    else:  # ESCALATE
        system_prompt = """You are a senior retention specialist at Airtel India.
Write professional call scripts for high-risk customer calls. Return valid JSON only."""

        user_prompt = f"""Write a call opening script for a senior specialist calling a high-risk customer.

Escalation brief: {offer.get('escalation_brief', 'High risk customer requiring immediate attention')}
Premium offer prepared: {offer['offer_type']} – {offer['discount_pct']}% off

Return JSON:
{{
  "message_draft": "string – professional 3-4 sentence call opening"
}}"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    result = json.loads(response.content)
    logger.info(f"MessageDrafter: message drafted for {state['customer_id']} ({strategy})")
    return {"message_draft": result["message_draft"]}