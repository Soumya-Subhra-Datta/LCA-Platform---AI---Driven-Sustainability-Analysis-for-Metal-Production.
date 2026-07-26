import pandas as pd
import numpy as np
from typing import Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import KNNImputer
import joblib
from pathlib import Path
from backend.app.config import settings
from backend.app.pipeline.data_loader import REE_OXIDES, LREE, HREE
from backend.app.utils.logger import logger


ARTIFACTS_DIR = Path(settings.MODEL_DIR) / "preprocessing"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


class MiningProjectsPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        logger.info("Preprocessing mining projects data")
        processed = df.copy()

        existing_oxides = [o for o in REE_OXIDES if o in processed.columns]
        complete_mask = processed[existing_oxides].notna().sum(axis=1) >= 10
        processed = processed[complete_mask].copy()
        logger.info(f"Filtered to {len(processed)} projects with >=10 REE oxide values")

        for oxide in existing_oxides:
            if processed[oxide].isna().any():
                median_val = processed[oxide].median()
                processed[oxide] = processed[oxide].fillna(median_val)

        if "resource_tonnes" in processed.columns:
            processed["resource_tonnes"] = pd.to_numeric(processed["resource_tonnes"], errors="coerce")
            valid_resource = processed["resource_tonnes"].notna()
            processed.loc[valid_resource, "log_resource"] = np.log10(
                processed.loc[valid_resource, "resource_tonnes"].clip(lower=1)
            )
            processed["log_resource"] = processed["log_resource"].fillna(processed["log_resource"].median())

        if "grade_pct" in processed.columns:
            processed["grade_pct"] = pd.to_numeric(processed["grade_pct"], errors="coerce")
            processed["grade_pct"] = processed["grade_pct"].fillna(processed["grade_pct"].median())

        if "continent" in processed.columns:
            le = LabelEncoder()
            processed["continent_encoded"] = le.fit_transform(processed["continent"].fillna("Unknown"))
            self.label_encoders["continent"] = le

        if "deposit_type" in processed.columns:
            le = LabelEncoder()
            processed["deposit_type_encoded"] = le.fit_transform(processed["deposit_type"].fillna("Unknown"))
            self.label_encoders["deposit_type"] = le

        existing_norm = [f"{o}_norm" for o in existing_oxides if f"{o}_norm" in processed.columns]
        feature_cols = []
        for col in ["log_resource", "grade_pct", "continent_encoded", "deposit_type_encoded"]:
            if col in processed.columns:
                feature_cols.append(col)
        feature_cols.extend(existing_norm)

        self.feature_names = feature_cols
        X = processed[feature_cols].copy()

        for col in X.columns:
            if X[col].isna().any():
                X[col] = X[col].fillna(X[col].median())

        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=feature_cols,
            index=processed.index
        )

        hree_pct = processed.get("hree_pct")
        if hree_pct is None and "hree_pct" in df.columns:
            hree_pct = processed["hree_pct"]

        self.is_fitted = True
        self.save()
        logger.info(f"Preprocessing complete: X shape={X_scaled.shape}, features={feature_cols}")
        return X_scaled, hree_pct

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            self.load()
        processed = df.copy()
        existing_oxides = [o for o in REE_OXIDES if o in processed.columns]

        for oxide in existing_oxides:
            if oxide in processed.columns and processed[oxide].isna().any():
                processed[oxide] = processed[oxide].fillna(0)

        if "resource_tonnes" in processed.columns:
            processed["resource_tonnes"] = pd.to_numeric(processed["resource_tonnes"], errors="coerce")
            processed["log_resource"] = np.log10(
                processed["resource_tonnes"].clip(lower=1).fillna(1)
            )

        if "grade_pct" in processed.columns:
            processed["grade_pct"] = pd.to_numeric(processed["grade_pct"], errors="coerce")
            processed["grade_pct"] = processed["grade_pct"].fillna(0)

        if "continent" in processed.columns and "continent" in self.label_encoders:
            le = self.label_encoders["continent"]
            processed["continent_encoded"] = processed["continent"].apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else -1
            )

        if "deposit_type" in processed.columns and "deposit_type" in self.label_encoders:
            le = self.label_encoders["deposit_type"]
            processed["deposit_type_encoded"] = processed["deposit_type"].apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else -1
            )

        existing_norm = [f"{o}_norm" for o in existing_oxides if f"{o}_norm" in processed.columns]
        feature_cols = []
        for col in ["log_resource", "grade_pct", "continent_encoded", "deposit_type_encoded"]:
            if col in processed.columns:
                feature_cols.append(col)
        feature_cols.extend(existing_norm)

        X = processed[feature_cols].fillna(0)
        X_scaled = pd.DataFrame(
            self.scaler.transform(X),
            columns=feature_cols,
            index=processed.index
        )
        return X_scaled

    def save(self):
        joblib.dump(self.scaler, ARTIFACTS_DIR / "mining_scaler.pkl")
        joblib.dump(self.label_encoders, ARTIFACTS_DIR / "mining_label_encoders.pkl")
        joblib.dump(self.feature_names, ARTIFACTS_DIR / "mining_feature_names.pkl")

    def load(self):
        if (ARTIFACTS_DIR / "mining_scaler.pkl").exists():
            self.scaler = joblib.load(ARTIFACTS_DIR / "mining_scaler.pkl")
            self.label_encoders = joblib.load(ARTIFACTS_DIR / "mining_label_encoders.pkl")
            self.feature_names = joblib.load(ARTIFACTS_DIR / "mining_feature_names.pkl")
            self.is_fitted = True


class FactoryPreprocessor:
    def __init__(self):
        self.is_fitted = False

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Preprocessing factory data")
        processed = df.copy()

        if "capacity_tpa" in processed.columns:
            processed["has_capacity"] = processed["capacity_tpa"].notna().astype(int)
            processed["log_capacity"] = np.log10(
                processed["capacity_tpa"].clip(lower=1).fillna(1)
            )

        if "yield_pct" in processed.columns:
            processed["has_yield"] = processed["yield_pct"].notna().astype(int)

        status_map = {
            1: "crushing_concentration",
            3: "mixed_reo",
            4: "separated_reo",
            5: "metal",
            6: "trial_production",
            7: "pre_feasibility",
            8: "terminated",
        }
        if "status_code" in processed.columns:
            processed["status_label"] = processed["status_code"].map(status_map).fillna("unknown")

        processed["supply_chain_completeness"] = (
            processed.get("has_upstream", 0).astype(int) +
            processed.get("has_downstream", 0).astype(int)
        ) / 2.0

        self.is_fitted = True
        logger.info(f"Factory preprocessing complete: {processed.shape}")
        return processed


class OpenDBPreprocessor:
    def __init__(self):
        self.is_fitted = False

    def process_commodities(self, df: pd.DataFrame) -> pd.DataFrame:
        processed = df.copy()
        if "value_tonnes" in processed.columns:
            processed["value_tonnes"] = pd.to_numeric(processed["value_tonnes"], errors="coerce")
        if "grade_ppm" in processed.columns:
            processed["grade_ppm"] = pd.to_numeric(processed["grade_ppm"], errors="coerce")
        if "recovery_rate" in processed.columns:
            processed["recovery_rate"] = pd.to_numeric(processed["recovery_rate"], errors="coerce")
        return processed

    def process_waste(self, df: pd.DataFrame) -> pd.DataFrame:
        processed = df.copy()
        if "value_tonnes" in processed.columns:
            processed["value_tonnes"] = pd.to_numeric(processed["value_tonnes"], errors="coerce")
        if "total_material_tonnes" in processed.columns:
            processed["total_material_tonnes"] = pd.to_numeric(processed["total_material_tonnes"], errors="coerce")
        if "stripping_ratio" in processed.columns:
            processed["stripping_ratio"] = pd.to_numeric(processed["stripping_ratio"], errors="coerce")

        processed["waste_ratio"] = np.where(
            processed.get("total_material_tonnes", 0) > 0,
            processed.get("value_tonnes", 0) / processed.get("total_material_tonnes", 1),
            0
        )
        return processed

    def process_transport(self, df: pd.DataFrame) -> pd.DataFrame:
        processed = df.copy()
        if "value_tonnes" in processed.columns:
            processed["value_tonnes"] = pd.to_numeric(processed["value_tonnes"], errors="coerce")

        mode_weights = {"Truck": 0.15, "Rail": 0.03, "Ship": 0.01, "Pipeline": 0.005}
        processed["transport_mode"] = processed.get("transport_by", "").astype(str)
        processed["emission_factor"] = processed["transport_mode"].apply(
            lambda x: max([v for k, v in mode_weights.items() if k.lower() in str(x).lower()] or [0.05])
        )
        return processed

    def process_minerals(self, df: pd.DataFrame) -> pd.DataFrame:
        processed = df.copy()
        if "value_tonnes" in processed.columns:
            processed["value_tonnes"] = pd.to_numeric(processed["value_tonnes"], errors="coerce")
        return processed

    def process_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        processed = df.copy()
        if "output_value_tonnes" in processed.columns:
            processed["output_value_tonnes"] = pd.to_numeric(processed["output_value_tonnes"], errors="coerce")
        if "recovery_rate" in processed.columns:
            processed["recovery_rate"] = pd.to_numeric(processed["recovery_rate"], errors="coerce")
        return processed


class WorldCommoditiesPreprocessor:
    def __init__(self):
        self.is_fitted = False

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Preprocessing world commodities data")
        processed = df.copy()

        year_cols = [c for c in processed.columns if c.isdigit()]
        for col in year_cols:
            processed[col] = pd.to_numeric(processed[col], errors="coerce")

        if year_cols:
            processed["mean_production"] = processed[year_cols].mean(axis=1)
            processed["std_production"] = processed[year_cols].std(axis=1)
            processed["trend"] = processed[year_cols[-1]] - processed[year_cols[0]] if len(year_cols) > 1 else 0

        if "mined_raw_mat" in processed.columns:
            processed["is_rare_earth"] = processed["mined_raw_mat"].str.contains(
                "Rare Earth", case=False, na=False
            ).astype(int)

        self.is_fitted = True
        return processed


def get_preprocessor(name: str):
    preprocessors = {
        "mining_projects": MiningProjectsPreprocessor,
        "factory": FactoryPreprocessor,
        "open_db": OpenDBPreprocessor,
        "world_commodities": WorldCommoditiesPreprocessor,
    }
    return preprocessors.get(name, None)
