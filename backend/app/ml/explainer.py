import numpy as np
import shap
from loguru import logger


# ── Plain English Mapping ─────────────────────────────────────────────────────

PLAIN_ENGLISH_MAP = {
    "contract_score": "Contract type (lower = month-to-month, higher = long-term)",
    "charge_ratio": "Monthly cost relative to total spend (high = new + expensive)",
    "tenure_bucket": "How long the customer has been with us",
    "tenure": "Months as a customer",
    "MonthlyCharges": "Monthly bill amount",
    "TotalCharges": "Total amount paid so far",
    "service_count": "Number of add-on services subscribed",
    "SeniorCitizen": "Customer is a senior citizen",
    "Partner": "Has a partner",
    "Dependents": "Has dependents",
    "PhoneService": "Has phone service",
    "PaperlessBilling": "Uses paperless billing",
    "Contract_Month-to-month": "No contract commitment — easiest to leave",
    "Contract_One year": "One year contract lock-in",
    "Contract_Two year": "Two year contract lock-in",
    "PaymentMethod_Electronic check": "Pays by electronic check (highest churn group)",
    "PaymentMethod_Mailed check": "Pays by mailed check",
    "PaymentMethod_Bank transfer (automatic)": "Automatic bank transfer payment",
    "PaymentMethod_Credit card (automatic)": "Automatic credit card payment",
    "InternetService_Fiber optic": "Uses fiber optic internet (premium, high churn)",
    "InternetService_DSL": "Uses DSL internet",
    "InternetService_No": "No internet service",
    "OnlineSecurity_No": "No online security add-on",
    "OnlineSecurity_Yes": "Has online security add-on",
    "TechSupport_No": "No tech support subscription",
    "TechSupport_Yes": "Has tech support subscription",
    "OnlineBackup_No": "No online backup service",
    "OnlineBackup_Yes": "Has online backup service",
    "DeviceProtection_No": "No device protection plan",
    "DeviceProtection_Yes": "Has device protection plan",
    "StreamingTV_No": "No streaming TV",
    "StreamingTV_Yes": "Subscribes to streaming TV",
    "StreamingMovies_No": "No streaming movies",
    "StreamingMovies_Yes": "Subscribes to streaming movies",
    "MultipleLines_No": "Single phone line",
    "MultipleLines_Yes": "Multiple phone lines",
}


def _get_plain_english(feature_name: str) -> str:
    """Match feature name to plain English — fallback to formatted name."""
    if feature_name in PLAIN_ENGLISH_MAP:
        return PLAIN_ENGLISH_MAP[feature_name]
    # Fallback: clean up underscores
    return feature_name.replace("_", " ").title()


# ── SHAP Explainer ────────────────────────────────────────────────────────────

class ChurnExplainer:
    def __init__(self, model, feature_names: list[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)
        logger.info("SHAP TreeExplainer initialized")

    def explain(
        self,
        X_row: np.ndarray,
        top_drivers: int = 5,
        top_signals: int = 3,
    ) -> tuple[list[dict], list[dict]]:
        """
        Returns:
            churn_drivers  — features pushing toward churn (positive SHAP)
            retention_signals — features pushing away from churn (negative SHAP)
        """
        shap_values = self.explainer.shap_values(X_row)

        # shap_values shape: (1, n_features)
        if shap_values.ndim == 2:
            sv = shap_values[0]
        else:
            sv = shap_values

        # Build feature-shap pairs
        pairs = list(zip(self.feature_names, sv))

        # Sort by absolute value descending
        pairs_sorted = sorted(pairs, key=lambda x: abs(x[1]), reverse=True)

        churn_drivers = []
        retention_signals = []

        for feature, value in pairs_sorted:
            entry = {
                "feature": feature,
                "shap_value": round(float(value), 4),
                "direction": "increases_churn" if value > 0 else "reduces_churn",
                "plain_english": _get_plain_english(feature),
            }
            if value > 0 and len(churn_drivers) < top_drivers:
                churn_drivers.append(entry)
            elif value < 0 and len(retention_signals) < top_signals:
                retention_signals.append(entry)

            if len(churn_drivers) >= top_drivers and len(retention_signals) >= top_signals:
                break

        logger.debug(f"Top churn driver: {churn_drivers[0]['feature']} = {churn_drivers[0]['shap_value']}")
        return churn_drivers, retention_signals