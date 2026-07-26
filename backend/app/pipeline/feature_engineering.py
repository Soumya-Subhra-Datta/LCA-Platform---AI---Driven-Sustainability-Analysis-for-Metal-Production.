import pandas as pd
import numpy as np
from backend.app.pipeline.data_loader import REE_OXIDES, LREE, HREE
from backend.app.utils.logger import logger


def engineer_mining_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Engineering features for mining projects")
    features = df.copy()

    existing_oxides = [o for o in REE_OXIDES if o in features.columns]
    existing_lree = [o for o in LREE if o in features.columns]
    existing_hree = [o for o in HREE if o in features.columns]

    features["ree_total_pct"] = features[existing_oxides].sum(axis=1) if existing_oxides else 0
    features["lree_total_pct"] = features[existing_lree].sum(axis=1) if existing_lree else 0
    features["hree_total_pct"] = features[existing_hree].sum(axis=1) if existing_hree else 0

    features["lree_hree_ratio"] = np.where(
        features["hree_total_pct"] > 0,
        features["lree_total_pct"] / features["hree_total_pct"],
        np.inf
    )

    features["nd_dy_ratio"] = np.where(
        features.get("Dy2O3", 0) > 0,
        features.get("Nd2O3", 0) / features["Dy2O3"],
        np.inf
    )

    features["ce_la_ratio"] = np.where(
        features.get("La2O3", 0) > 0,
        features.get("Ce2O3", 0) / features["La2O3"],
        np.inf
    )

    for oxide in existing_oxides:
        features[f"log_{oxide}"] = np.log10(features[oxide].clip(lower=0.001))

    if "resource_tonnes" in features.columns:
        if "grade_pct" in features.columns:
            features["contained_metal_tonnes"] = features["resource_tonnes"] * features["grade_pct"] / 100

        features["resource_log"] = np.log10(features["resource_tonnes"].clip(lower=1))

    if "continent" in features.columns:
        continent_dummies = pd.get_dummies(features["continent"], prefix="continent")
        features = pd.concat([features, continent_dummies], axis=1)

    if "deposit_type" in features.columns:
        deposit_dummies = pd.get_dummies(features["deposit_type"], prefix="deposit")
        features = pd.concat([features, deposit_dummies], axis=1)

    features["oxide_coverage"] = features[existing_oxides].notna().sum(axis=1) / len(REE_OXIDES) if existing_oxides else 0

    if existing_oxides:
        oxide_matrix = features[existing_oxides].fillna(0)
        for i, o1 in enumerate(existing_oxides):
            for o2 in existing_oxides[i+1:]:
                features[f"{o1}_x_{o2}"] = oxide_matrix[o1] * oxide_matrix[o2]

    logger.info(f"Feature engineering complete: {features.shape[1]} features")
    return features


def engineer_environmental_features(waste_df: pd.DataFrame, minerals_df: pd.DataFrame,
                                      commodities_df: pd.DataFrame, processing_df: pd.DataFrame,
                                      transport_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    logger.info("Engineering environmental features from Open Database")
    results = {}

    if not waste_df.empty:
        waste_agg = waste_df.groupby("facility_id").agg(
            total_waste_tonnes=("value_tonnes", "sum"),
            avg_stripping_ratio=("stripping_ratio", "mean"),
            waste_years_active=("year", "nunique"),
            waste_types=("waste_type", "nunique"),
        ).reset_index()
        results["waste_features"] = waste_agg

    if not minerals_df.empty:
        ore_mined = minerals_df[minerals_df["type"] == "Ore mined"].groupby("facility_id").agg(
            total_ore_mined=("value_tonnes", "sum"),
            mining_years=("year", "nunique"),
        ).reset_index()
        ore_processed = minerals_df[minerals_df["type"] == "Ore processed"].groupby("facility_id").agg(
            total_ore_processed=("value_tonnes", "sum"),
            processing_years=("year", "nunique"),
        ).reset_index()
        mineral_features = ore_mined.merge(ore_processed, on="facility_id", how="outer")
        mineral_features["processing_ratio"] = np.where(
            mineral_features["total_ore_mined"] > 0,
            mineral_features["total_ore_processed"] / mineral_features["total_ore_mined"],
            0
        )
        results["mineral_features"] = mineral_features

    if not commodities_df.empty:
        comm_agg = commodities_df.groupby("facility_id").agg(
            total_production=("value_tonnes", "sum"),
            avg_grade=("grade_ppm", "mean"),
            avg_recovery=("recovery_rate", "mean"),
            commodity_count=("commodity", "nunique"),
            production_years=("year", "nunique"),
        ).reset_index()
        results["commodity_features"] = comm_agg

    if not processing_df.empty:
        proc_agg = processing_df.groupby("facility_id").agg(
            total_output=("output_value_tonnes", "sum"),
            avg_recovery=("recovery_rate", "mean"),
            processing_types=("facility_type", "nunique"),
            processing_years=("year", "nunique"),
        ).reset_index()
        results["processing_features"] = proc_agg

    if not transport_df.empty:
        trans_agg = transport_df.groupby("facility_id").agg(
            total_transport_volume=("value_tonnes", "sum"),
            avg_emission_factor=("emission_factor", "mean"),
            export_fraction=("export", lambda x: (x == "Yes").mean() if x.notna().any() else 0),
            transport_years=("year", "nunique"),
        ).reset_index()
        results["transport_features"] = trans_agg

    return results


def build_unified_facility_features(facility_ids: list[str], env_features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    logger.info(f"Building unified facility features for {len(facility_ids)} facilities")
    unified = pd.DataFrame({"facility_id": facility_ids})

    for name, feat_df in env_features.items():
        if not feat_df.empty:
            unified = unified.merge(feat_df, on="facility_id", how="left")

    numeric_cols = unified.select_dtypes(include=[np.number]).columns
    unified[numeric_cols] = unified[numeric_cols].fillna(0)

    logger.info(f"Unified features: {unified.shape}")
    return unified


def compute_correlation_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    available = [c for c in columns if c in df.columns]
    return df[available].corr()


def compute_feature_importance_from_correlations(df: pd.DataFrame, target: str, features: list[str]) -> pd.Series:
    available = [f for f in features if f in df.columns and f != target]
    correlations = df[available].corrwith(df[target]).abs().sort_values(ascending=False)
    return correlations
