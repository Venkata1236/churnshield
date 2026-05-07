import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from loguru import logger

from app.core.config import settings
from app.ml.explainer import ChurnExplainer
from app.models.schemas import RiskTier


# ── Model Manager ─────────────────────────────────────────────────────────────

class ModelManager:
    def __init__(self):
        self.model = None
        self.threshold = 0.5
        self.feature_names: list[str] = []
        self.explainer: ChurnExplainer = None
        self.is_loaded = False

    def load(self) -> None:
        model_path = Path(settings.model_path)
        feature_path = Path(settings.feature_names_path)

        if not model_path.exists():
            logger.warning(f"Model not found at {model_path} — train first")
            return

        model_data = joblib.load(model_path)
        self.model = model_data["model"]
        self.threshold = model_data["threshold"]
        self.feature_names = model_data["feature_cols"]

        self.explainer = ChurnExplainer(self.model, self.feature_names)
        self.is_loaded = True
        logger.info(f"Model loaded — threshold: {self.threshold:.2f}, features: {len(self.feature_names)}")

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply same feature engineering as train.py."""

        # Binary mappings
        df["gender"] = df["gender"].map({"Male": 1, "Female": 0}).fillna(0)
        binary_cols = ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]
        for col in binary_cols:
            if col in df.columns:
                df[col] = df[col].map({"Yes": 1, "No": 0}).fillna(0)

        # Engineered features
        df["tenure_bucket"] = pd.cut(
            df["tenure"],
            bins=[0, 12, 24, 48, 72],
            labels=[0, 1, 2, 3],
            include_lowest=True,
        ).astype(int)

        df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)

        service_cols = [
            "PhoneService", "MultipleLines", "OnlineSecurity", "OnlineBackup",
            "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
        ]
        df["service_count"] = df[service_cols].apply(
            lambda x: (x != "No").sum(), axis=1
        )

        df["contract_score"] = df["Contract"].map({
            "Month-to-month": 0,
            "One year": 1,
            "Two year": 2,
        }).fillna(0)

        return df

    def _encode_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """One-hot encode categoricals — align to training feature names."""
        cat_cols = [
            "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
            "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
            "Contract", "PaymentMethod",
        ]
        existing_cats = [c for c in cat_cols if c in df.columns]
        df = pd.get_dummies(df, columns=existing_cats, drop_first=False)

        # Align columns to training features — add missing cols as 0
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0

        return df[self.feature_names]

    def _get_risk_tier(self, probability: float) -> RiskTier:
        if probability >= 0.7:
            return RiskTier.HIGH
        elif probability >= 0.4:
            return RiskTier.MEDIUM
        return RiskTier.LOW

    def predict(self, customer_data: dict) -> dict:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded — call model_manager.load() first")

        # Build raw DataFrame from input
        df = pd.DataFrame([{
            "tenure": customer_data["tenure"],
            "MonthlyCharges": customer_data["monthly_charges"],
            "TotalCharges": customer_data["total_charges"],
            "Contract": customer_data["contract"],
            "PaymentMethod": customer_data["payment_method"],
            "InternetService": customer_data["internet_service"],
            "TechSupport": customer_data["tech_support"],
            "OnlineSecurity": customer_data["online_security"],
            "OnlineBackup": customer_data.get("online_backup", "No"),
            "DeviceProtection": customer_data.get("device_protection", "No"),
            "StreamingTV": customer_data.get("streaming_tv", "No"),
            "StreamingMovies": customer_data.get("streaming_movies", "No"),
            "PhoneService": customer_data.get("phone_service", "Yes"),
            "MultipleLines": customer_data.get("multiple_lines", "No"),
            "gender": customer_data.get("gender", "Male"),
            "SeniorCitizen": customer_data.get("senior_citizen", 0),
            "Partner": customer_data.get("partner", "No"),
            "Dependents": customer_data.get("dependents", "No"),
            "PaperlessBilling": customer_data.get("paperless_billing", "Yes"),
        }])

        df = self._engineer_features(df)
        df_encoded = self._encode_features(df)

        X = df_encoded.values
        probability = float(self.model.predict_proba(X)[0][1])
        prediction = "HIGH_RISK" if probability >= self.threshold else "LOW_RISK"
        risk_tier = self._get_risk_tier(probability)

        # SHAP explanations
        churn_drivers, retention_signals = self.explainer.explain(X)

        logger.info(
            f"Prediction for {customer_data['customer_id']}: "
            f"prob={probability:.3f}, tier={risk_tier}, threshold={self.threshold:.2f}"
        )

        return {
            "customer_id": customer_data["customer_id"],
            "churn_probability": round(probability, 4),
            "churn_prediction": prediction,
            "risk_tier": risk_tier,
            "top_churn_drivers": churn_drivers,
            "retention_signals": retention_signals,
            "proceed_to_retention": probability >= 0.4,
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

model_manager = ModelManager()