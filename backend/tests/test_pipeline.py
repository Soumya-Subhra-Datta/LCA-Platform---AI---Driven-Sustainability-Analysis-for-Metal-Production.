import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np
from backend.app.pipeline.data_loader import load_mining_projects, load_factory, load_world_commodities
from backend.app.pipeline.preprocessor import MiningProjectsPreprocessor, FactoryPreprocessor
from backend.app.pipeline.feature_engineering import engineer_mining_features


class TestDataLoading:
    def test_load_mining_projects(self):
        df = load_mining_projects()
        assert not df.empty
        assert len(df) > 100
        assert "project_name" in df.columns

    def test_load_factory(self):
        df = load_factory()
        assert not df.empty
        assert "company" in df.columns

    def test_ree_oxide_columns_present(self):
        df = load_mining_projects()
        ree_cols = ["La2O3", "Ce2O3", "Nd2O3", "Dy2O3", "Y2O3"]
        for col in ree_cols:
            assert col in df.columns, f"Missing REE column: {col}"

    def test_numeric_conversion(self):
        df = load_mining_projects()
        assert df["La2O3"].dtype in [np.float64, np.float32, float]


class TestPreprocessing:
    def test_mining_preprocessor_fit_transform(self):
        df = load_mining_projects()
        preprocessor = MiningProjectsPreprocessor()
        X, y = preprocessor.fit_transform(df)
        assert not X.empty
        assert X.shape[0] > 30

    def test_label_encoding(self):
        df = load_mining_projects()
        preprocessor = MiningProjectsPreprocessor()
        X, y = preprocessor.fit_transform(df)
        assert "continent_encoded" in X.columns
        assert "deposit_type_encoded" in X.columns

    def test_factory_preprocessor(self):
        df = load_factory()
        preprocessor = FactoryPreprocessor()
        result = preprocessor.process(df)
        assert "status_label" in result.columns
        assert "supply_chain_completeness" in result.columns


class TestFeatureEngineering:
    def test_engineer_features(self):
        df = load_mining_projects()
        features = engineer_mining_features(df)
        assert "lree_hree_ratio" in features.columns
        assert "ce_la_ratio" in features.columns
        assert features.shape[1] > df.shape[1]
