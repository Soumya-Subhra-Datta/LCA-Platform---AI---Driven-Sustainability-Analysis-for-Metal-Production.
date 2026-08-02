import numpy as np
import pandas as pd
from typing import Any, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, accuracy_score, f1_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
from pathlib import Path
from backend.app.config import settings
from backend.app.utils.logger import logger


MODELS_DIR = Path(settings.MODEL_DIR)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

_model_cache: dict[str, "BaseModel"] = {}


def invalidate_model_cache():
    _model_cache.clear()


class BaseModel:
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.metrics = {}
        self.label_encoder = None

    def save(self):
        model_dir = MODELS_DIR / self.name
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_dir / "model.pkl")
        joblib.dump(self.scaler, model_dir / "scaler.pkl")
        joblib.dump(self.feature_names, model_dir / "features.pkl")
        joblib.dump(self.metrics, model_dir / "metrics.pkl")
        if self.label_encoder:
            joblib.dump(self.label_encoder, model_dir / "label_encoder.pkl")
        logger.info(f"Saved model {self.name} to {model_dir}")

    def load(self) -> bool:
        model_dir = MODELS_DIR / self.name
        if not (model_dir / "model.pkl").exists():
            return False
        self.model = joblib.load(model_dir / "model.pkl")
        self.scaler = joblib.load(model_dir / "scaler.pkl")
        self.feature_names = joblib.load(model_dir / "features.pkl")
        self.metrics = joblib.load(model_dir / "metrics.pkl")
        le_path = model_dir / "label_encoder.pkl"
        if le_path.exists():
            self.label_encoder = joblib.load(le_path)
        logger.info(f"Loaded model {self.name}")
        return True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise ValueError(f"Model {self.name} not loaded")
        X_scaled = self.scaler.transform(X.reshape(1, -1) if X.ndim == 1 else X)
        return self.model.predict(X_scaled)

    def get_feature_importance(self) -> dict[str, float]:
        if self.model is None or not hasattr(self.model, "feature_importances_"):
            return {}
        return dict(zip(self.feature_names, self.model.feature_importances_))


class HREEPredictor(BaseModel):
    def __init__(self):
        super().__init__("hree_predictor")

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        logger.info("Training HREE Predictor")
        self.feature_names = list(X.columns)

        valid_mask = y.notna() & np.isfinite(y)
        X_clean = X[valid_mask].copy()
        y_clean = y[valid_mask].copy()

        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model = GradientBoostingRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            subsample=0.8, min_samples_split=5, random_state=42
        )
        self.model.fit(X_train_scaled, y_train)

        y_pred = self.model.predict(X_test_scaled)

        self.metrics = {
            "r2": float(r2_score(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "cv_r2_mean": float(cross_val_score(self.model, X_train_scaled, y_train, cv=3, scoring="r2").mean()),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        self.save()
        logger.info(f"HREE Predictor trained: R2={self.metrics['r2']:.4f}, RMSE={self.metrics['rmse']:.4f}")
        return self.metrics

    def predict_hree(self, X: pd.DataFrame) -> dict[str, Any]:
        if self.model is None:
            self.load()
        X_arr = X.values if isinstance(X, pd.DataFrame) else X
        X_scaled = self.scaler.transform(X_arr.reshape(1, -1) if X_arr.ndim == 1 else X_arr)
        prediction = self.model.predict(X_scaled)[0]
        importance = self.get_feature_importance()
        top_features = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])
        return {
            "hree_percentage": float(prediction),
            "top_features": top_features,
            "confidence": "high" if self.metrics.get("r2", 0) > 0.7 else "medium" if self.metrics.get("r2", 0) > 0.4 else "low"
        }


class DepositClassifier(BaseModel):
    def __init__(self):
        super().__init__("deposit_classifier")

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        logger.info("Training Deposit Classifier")
        self.feature_names = list(X.columns)

        valid_mask = y.notna()
        X_clean = X[valid_mask].copy()
        y_clean = y[valid_mask].copy()

        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y_clean)

        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_encoded, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=5,
            random_state=42, class_weight="balanced"
        )
        self.model.fit(X_train_scaled, y_train)

        y_pred = self.model.predict(X_test_scaled)

        self.metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
            "f1_weighted": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
            "classes": list(self.label_encoder.classes_),
            "classification_report": classification_report(
                y_test, y_pred,
                labels=list(range(len(self.label_encoder.classes_))),
                target_names=self.label_encoder.classes_,
                zero_division=0, output_dict=True
            ),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        self.save()
        logger.info(f"Deposit Classifier trained: Accuracy={self.metrics['accuracy']:.4f}")
        return self.metrics

    def predict_deposit(self, X: pd.DataFrame) -> dict[str, Any]:
        if self.model is None:
            self.load()
        X_arr = X.values if isinstance(X, pd.DataFrame) else X
        X_scaled = self.scaler.transform(X_arr.reshape(1, -1) if X_arr.ndim == 1 else X_arr)
        pred_encoded = self.model.predict(X_scaled)[0]
        pred_label = self.label_encoder.inverse_transform([pred_encoded])[0]
        proba = self.model.predict_proba(X_scaled)[0]
        class_probs = dict(zip(self.label_encoder.classes_, proba.tolist()))
        return {
            "deposit_type": pred_label,
            "probabilities": class_probs,
            "confidence": float(max(proba))
        }


class ResourceEstimator(BaseModel):
    def __init__(self):
        super().__init__("resource_estimator")

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        logger.info("Training Resource Estimator")
        self.feature_names = list(X.columns)

        valid_mask = y.notna() & (y > 0)
        X_clean = X[valid_mask].copy()
        y_clean = np.log10(y[valid_mask].clip(lower=1))

        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model = RandomForestRegressor(
            n_estimators=100, max_depth=8, min_samples_split=5, random_state=42
        )
        self.model.fit(X_train_scaled, y_train)

        y_pred = self.model.predict(X_test_scaled)

        self.metrics = {
            "r2": float(r2_score(y_test, y_pred)),
            "rmse_log": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae_log": float(mean_absolute_error(y_test, y_pred)),
            "cv_r2_mean": float(cross_val_score(self.model, X_train_scaled, y_train, cv=3, scoring="r2").mean()),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        self.save()
        logger.info(f"Resource Estimator trained: R2={self.metrics['r2']:.4f}")
        return self.metrics

    def predict_resource(self, X: pd.DataFrame) -> dict[str, Any]:
        if self.model is None:
            self.load()
        X_arr = X.values if isinstance(X, pd.DataFrame) else X
        X_scaled = self.scaler.transform(X_arr.reshape(1, -1) if X_arr.ndim == 1 else X_arr)
        log_pred = self.model.predict(X_scaled)[0]
        resource_tonnes = 10 ** log_pred
        return {
            "resource_tonnes": float(resource_tonnes),
            "log_resource": float(log_pred),
            "resource_kt": float(resource_tonnes / 1000),
            "resource_mt": float(resource_tonnes / 1e6),
            "confidence": "high" if self.metrics.get("r2", 0) > 0.7 else "medium"
        }


class DyPredictor(BaseModel):
    def __init__(self):
        super().__init__("dy_predictor")

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        logger.info("Training Dy2O3 Predictor")
        self.feature_names = list(X.columns)

        valid_mask = y.notna()
        X_clean = X[valid_mask].copy()
        y_clean = y[valid_mask].copy()

        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            subsample=0.8, random_state=42
        )
        self.model.fit(X_train_scaled, y_train)

        y_pred = self.model.predict(X_test_scaled)

        self.metrics = {
            "r2": float(r2_score(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "cv_r2_mean": float(cross_val_score(self.model, X_train_scaled, y_train, cv=3, scoring="r2").mean()),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        self.save()
        logger.info(f"Dy2O3 Predictor trained: R2={self.metrics['r2']:.4f}")
        return self.metrics

    def predict_dy(self, X: pd.DataFrame) -> dict[str, Any]:
        if self.model is None:
            self.load()
        X_arr = X.values if isinstance(X, pd.DataFrame) else X
        X_scaled = self.scaler.transform(X_arr.reshape(1, -1) if X_arr.ndim == 1 else X_arr)
        prediction = self.model.predict(X_scaled)[0]
        importance = self.get_feature_importance()
        top_features = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])
        return {
            "dy2o3_content": float(prediction),
            "top_features": top_features,
            "confidence": "high" if self.metrics.get("r2", 0) > 0.7 else "medium"
        }


MODEL_REGISTRY = {
    "hree_predictor": HREEPredictor,
    "deposit_classifier": DepositClassifier,
    "resource_estimator": ResourceEstimator,
    "dy_predictor": DyPredictor,
}


def get_model(name: str) -> Optional[BaseModel]:
    cls = MODEL_REGISTRY.get(name)
    if cls is None:
        return None
    cached = _model_cache.get(name)
    if cached is not None:
        return cached
    model = cls()
    if not model.load():
        logger.warning(f"Model {name} not found, needs training")
    _model_cache[name] = model
    return model


def get_all_models() -> dict[str, BaseModel]:
    models = {}
    for name in MODEL_REGISTRY:
        models[name] = get_model(name)
    return models
