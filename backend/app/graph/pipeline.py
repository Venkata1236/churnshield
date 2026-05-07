from langgraph.graph import StateGraph, END

from app.graph.state import ChurnState
from app.graph.nodes import (
    risk_router,
    standard_offer_node,
    targeted_offer_node,
    escalate_node,
    message_drafter_node,
)
from loguru import logger


# ── Conditional Edge Router ───────────────────────────────────────────────────

def route_by_tier(state: ChurnState) -> str:
    """
    Called after risk_router node.
    Returns the name of the next node based on retention_strategy.
    This is the conditional routing pattern used in every remaining project.
    """
    strategy = state["retention_strategy"]

    if strategy == "ESCALATE":
        return "escalate_node"
    elif strategy == "TARGETED":
        return "targeted_offer_node"
    else:
        return "standard_offer_node"


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_retention_pipeline() -> StateGraph:
    graph = StateGraph(ChurnState)

    # Register nodes
    graph.add_node("risk_router", risk_router)
    graph.add_node("standard_offer_node", standard_offer_node)
    graph.add_node("targeted_offer_node", targeted_offer_node)
    graph.add_node("escalate_node", escalate_node)
    graph.add_node("message_drafter_node", message_drafter_node)

    # Entry point
    graph.set_entry_point("risk_router")

    # Conditional edges — LOW / MEDIUM / HIGH routing
    graph.add_conditional_edges(
        "risk_router",
        route_by_tier,
        {
            "standard_offer_node": "standard_offer_node",
            "targeted_offer_node": "targeted_offer_node",
            "escalate_node": "escalate_node",
        },
    )

    # All 3 offer nodes flow into message_drafter_node
    graph.add_edge("standard_offer_node", "message_drafter_node")
    graph.add_edge("targeted_offer_node", "message_drafter_node")
    graph.add_edge("escalate_node", "message_drafter_node")

    # message_drafter_node is the final node
    graph.add_edge("message_drafter_node", END)

    logger.info("Retention pipeline compiled successfully")
    return graph.compile()


# ── Singleton ─────────────────────────────────────────────────────────────────

retention_pipeline = build_retention_pipeline()