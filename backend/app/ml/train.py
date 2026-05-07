import json
from pathlib import Path

import joblib
import numpy as np
import optuna
import pandas as pd
from loguru import logger
from sklearn.metrics import roc_auc_score, recall_score, precision_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from pathlib import Path

from app.core.config import SAVED_MODELS_DIR

optuna.logging.set_verbosity(optuna.logging.WARNING)

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BACKEND_DIR / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"


# ── Step 1: Load & Clean ──────────────────────────────────────────────────────

def load_and_clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    logger.info(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Fix TotalCharges — spaces where new customers have 0 tenure
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0.0)

    # Drop customerID — not a feature
    df.drop(columns=["customerID"], inplace=True)

    # Encode target
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
    df["gender"] = df["gender"].map({"Male": 1, "Female": 0})

    # Binary Yes/No columns
    binary_cols = ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]
    for col in binary_cols:
        df[col] = df[col].map({"Yes": 1, "No": 0})

    logger.info(f"Churn rate: {df['Churn'].mean():.2%}")
    return df


# ── Step 2: Feature Engineering ───────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Tenure bucket — captures trial phase (0-12 months = highest churn)
    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=[0, 1, 2, 3],
        include_lowest=True,
    ).astype(int)

    # 2. Charge ratio — high ratio = paying a lot for very little tenure = evaluating
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)

    # 3. Service count — more services = higher switching cost = lower churn
    service_cols = [
        "PhoneService", "MultipleLines", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
    ]
    df["service_count"] = df[service_cols].apply(
        lambda x: (x != "No").sum(), axis=1
    )

    # 4. Contract score — encodes commitment as ordinal (preserves ordering)
    df["contract_score"] = df["Contract"].map({
        "Month-to-month": 0,
        "One year": 1,
        "Two year": 2,
    })

    logger.info("Feature engineering complete: tenure_bucket, charge_ratio, service_count, contract_score")
    return df


# ── Step 3: Encode Categoricals ───────────────────────────────────────────────

def encode_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    cat_cols = [
        "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
        "Contract", "PaymentMethod",
    ]
    df = pd.get_dummies(df, columns=cat_cols, drop_first=False)

    feature_cols = [c for c in df.columns if c != "Churn"]
    logger.info(f"Total features after encoding: {len(feature_cols)}")
    return df, feature_cols


# ── Step 4: Business Cost Matrix Threshold ────────────────────────────────────

def find_optimal_threshold(model: XGBClassifier, X: np.ndarray, y: np.ndarray) -> float:
    """
    FN (missed churner) = ₹2400 lost revenue
    FP (false alarm)    = ₹200 wasted offer
    FN is 12x more expensive → shift threshold below 0.5
    """
    probs = model.predict_proba(X)[:, 1]
    thresholds = np.arange(0.1, 0.9, 0.05)
    best_threshold = 0.5
    best_cost = float("inf")

    logger.info("\nThreshold | Total Cost | FN  | FP  | Recall | Precision")
    logger.info("-" * 60)

    for t in thresholds:
        preds = (probs >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, preds).ravel()
        total_cost = (fn * 2400) + (fp * 200)

        logger.info(
            f"  {t:.2f}    | ₹{total_cost:,}    | {fn}  | {fp}  "
            f"| {recall_score(y, preds):.2f}  | {precision_score(y, preds):.2f}"
        )

        if total_cost < best_cost:
            best_cost = total_cost
            best_threshold = t

    logger.info(f"\nOptimal threshold: {best_threshold:.2f} — Total cost: ₹{best_cost:,}")
    return float(best_threshold)


# ── Step 5: Optuna Hyperparameter Tuning ──────────────────────────────────────

def tune_xgboost(X: np.ndarray, y: np.ndarray) -> dict:
    scale_pos_weight = (len(y) - y.sum()) / y.sum()  # ≈ 2.77

    def objective(trial):
        params = {
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "scale_pos_weight": scale_pos_weight,
            "eval_metric": "auc",
            "random_state": 42,
            "n_jobs": -1,
        }
        model = XGBClassifier(**params)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
        return scores.mean()

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=30)
    logger.info(f"Best ROC-AUC: {study.best_value:.4f}")
    logger.info(f"Best params: {study.best_params}")
    return study.best_params


# ── Step 6: Train Final Model ─────────────────────────────────────────────────

def train(data_path: Path = DATA_PATH) -> None:
    df = load_and_clean(data_path)
    df = engineer_features(df)
    df, feature_cols = encode_features(df)

    X = df[feature_cols].values
    y = df["Churn"].values

    # Tune
    best_params = tune_xgboost(X, y)
    scale_pos_weight = (len(y) - y.sum()) / y.sum()

    # Train final model on full data
    model = XGBClassifier(
        **best_params,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    # Evaluate
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    auc_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
    logger.info(f"CV ROC-AUC: {auc_scores.mean():.4f} ± {auc_scores.std():.4f}")

    if auc_scores.mean() < 0.82:
        logger.warning("ROC-AUC below 0.82 — consider adding more features before proceeding")

    # Business cost threshold
    threshold = find_optimal_threshold(model, X, y)

    # Final evaluation at optimal threshold
    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= threshold).astype(int)
    recall = recall_score(y, preds)
    precision = precision_score(y, preds)

    logger.info(f"\nFinal Model @ threshold={threshold:.2f}")
    logger.info(f"Recall (churners caught): {recall:.4f}")
    logger.info(f"Precision: {precision:.4f}")

    if recall < 0.75:
        logger.warning("Recall below 0.75 — too many churners being missed")

    # Save model
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_data = {
        "model": model,
        "threshold": threshold,
        "feature_cols": feature_cols,
    }
    joblib.dump(model_data, SAVED_MODELS_DIR / "churn_model.pkl")
    logger.info(f"Model saved to {SAVED_MODELS_DIR / 'churn_model.pkl'}")

    # Save feature names separately for inference
    with open(SAVED_MODELS_DIR / "feature_names.json", "w") as f:
        json.dump(feature_cols, f, indent=2)
    logger.info(f"Feature names saved to {SAVED_MODELS_DIR / 'feature_names.json'}")


if __name__ == "__main__":
    train()