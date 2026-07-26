import numpy as np
import pandas as pd
from typing import Any, Optional
from backend.app.utils.logger import logger


class SHAPExplainer:
    def __init__(self):
        self.explainer = None
        self.shap_values = None

    def explain(self, model, X: pd.DataFrame, background_samples: int = 50) -> dict[str, Any]:
        try:
            import shap
            X_arr = X.values if isinstance(X, pd.DataFrame) else X
            if hasattr(model, 'model') and model.model is not None:
                sklearn_model = model.model
                if hasattr(sklearn_model, 'feature_importances_'):
                    background = shap.sample(
                        pd.DataFrame(X_arr, columns=model.feature_names) if isinstance(X, pd.DataFrame) else X,
                        min(background_samples, len(X_arr))
                    )
                    self.explainer = shap.TreeExplainer(sklearn_model)
                    self.shap_values = self.explainer.shap_values(
                        X_arr[:1] if X_arr.ndim > 1 else X_arr.reshape(1, -1)
                    )

                    if isinstance(self.shap_values, np.ndarray) and self.shap_values.ndim > 1:
                        vals = self.shap_values[0]
                    else:
                        vals = self.shap_values

                    feature_names = model.feature_names if hasattr(model, 'feature_names') else [f"feat_{i}" for i in range(len(vals))]
                    importance = dict(zip(feature_names, np.abs(vals).tolist()))
                    sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15])

                    shap_direction = {}
                    for fname, fval in zip(feature_names, vals):
                        shap_direction[fname] = {"magnitude": abs(float(fval)), "direction": "positive" if fval > 0 else "negative"}

                    return {
                        "method": "SHAP TreeExplainer",
                        "top_features": sorted_importance,
                        "direction": shap_direction,
                        "base_value": float(self.explainer.expected_value) if np.isscalar(self.explainer.expected_value) else float(self.explainer.expected_value[0]),
                        "feature_count": len(feature_names)
                    }
        except ImportError:
            logger.warning("SHAP not installed, using feature importance fallback")
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")

        return self._fallback_explanation(model)

    def _fallback_explanation(self, model) -> dict[str, Any]:
        if hasattr(model, 'get_feature_importance'):
            importance = model.get_feature_importance()
            if importance:
                sorted_imp = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15])
                total = sum(sorted_imp.values())
                normalized = {k: v/total if total > 0 else 0 for k, v in sorted_imp.items()}
                return {
                    "method": "Feature Importance (model-based)",
                    "top_features": normalized,
                    "direction": {k: {"magnitude": v, "direction": "positive"} for k, v in normalized.items()},
                    "base_value": 0.0,
                    "feature_count": len(importance)
                }
        return {
            "method": "No explanation available",
            "top_features": {},
            "direction": {},
            "base_value": 0.0,
            "feature_count": 0
        }


class NaturalLanguageExplainer:
    TEMPLATES = {
        "hree_predictor": {
            "high_hree": "The model predicts a high HREE content ({value:.2f}%), indicating this project is enriched in heavy rare earth elements. This is typically associated with {top_factor} deposit types and specific geochemical signatures.",
            "low_hree": "The model predicts a low HREE content ({value:.2f}%), suggesting this is a light rare earth dominant deposit. The primary factors are {top_factor}.",
        },
        "deposit_classifier": {
            "default": "The model classifies this deposit as {deposit_type} with {confidence:.1%} confidence. The key discriminants are {top_factor}."
        },
        "resource_estimator": {
            "large": "Estimated resource: {value:.0f} tonnes ({unit}). This is classified as a {'significant' if value > 1e6 else 'moderate' if value > 1e5 else 'small'} deposit.",
            "default": "Estimated resource size: {value:.0f} tonnes."
        },
        "dy_predictor": {
            "high_dy": "Predicted Dy2O3 content: {value:.4f}%. Dysprosium is a critical HREE for permanent magnets and wind turbines.",
            "default": "Predicted Dy2O3 content: {value:.4f}%."
        }
    }

    def explain_prediction(self, model_name: str, prediction: dict, shap_explanation: dict) -> str:
        top_features = shap_explanation.get("top_features", {})
        top_factor = list(top_features.keys())[0] if top_features else "unknown"

        if model_name == "hree_predictor":
            hree = prediction.get("hree_percentage", 0)
            template_key = "high_hree" if hree > 20 else "low_hree"
            template = self.TEMPLATES["hree_predictor"].get(template_key, self.TEMPLATES["hree_predictor"]["low_hree"])
            return template.format(value=hree, top_factor=top_factor)

        elif model_name == "deposit_classifier":
            deposit = prediction.get("deposit_type", "Unknown")
            confidence = prediction.get("confidence", 0)
            template = self.TEMPLATES["deposit_classifier"]["default"]
            return template.format(deposit_type=deposit, confidence=confidence, top_factor=top_factor)

        elif model_name == "resource_estimator":
            resource = prediction.get("resource_tonnes", 0)
            unit = prediction.get("resource_mt", 0)
            if unit >= 1:
                unit_str = f"{unit:.2f} million tonnes"
            else:
                unit_str = f"{prediction.get('resource_kt', 0):.0f} kilotonnes"
            template = self.TEMPLATES["resource_estimator"]["default"]
            return template.format(value=resource, unit=unit_str)

        elif model_name == "dy_predictor":
            dy = prediction.get("dy2o3_content", 0)
            template = self.TEMPLATES["dy_predictor"]["default"]
            return template.format(value=dy)

        return f"Prediction for {model_name}: {prediction}"


class ExplainabilityService:
    def __init__(self):
        self.shap_explainer = SHAPExplainer()
        self.nl_explainer = NaturalLanguageExplainer()

    def explain(self, model, X: pd.DataFrame, model_name: str, prediction: dict) -> dict[str, Any]:
        shap_result = self.shap_explainer.explain(model, X)
        nl_explanation = self.nl_explainer.explain_prediction(model_name, prediction, shap_result)

        return {
            "shap": shap_result,
            "natural_language": nl_explanation,
            "model_name": model_name,
            "prediction_summary": prediction,
        }
