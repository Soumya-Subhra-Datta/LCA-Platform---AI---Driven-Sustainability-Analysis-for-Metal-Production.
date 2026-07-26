import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np
import pandas as pd
from backend.app.lca.engine import LCAEngine
from backend.app.circular.engine import CircularityCalculator, SustainabilityScorer


class TestLCAEngine:
    def setup_method(self):
        self.engine = LCAEngine()

    def test_full_assessment_surface(self):
        result = self.engine.full_assessment(
            resource_tonnes=100000, grade_pct=5.0, mining_type="Surface",
            processing_steps=["crushing", "grinding", "leaching", "solvent_extraction"],
            transport_distance_km=200
        )
        assert "carbon_footprint" in result
        assert "water_footprint" in result
        assert "energy_consumption" in result
        assert "waste_generation" in result
        assert "summary" in result
        assert result["summary"]["total_co2_tonnes"] > 0

    def test_full_assessment_underground(self):
        result = self.engine.full_assessment(
            resource_tonnes=50000, grade_pct=3.0, mining_type="Underground",
            processing_steps=["crushing", "leaching"],
            transport_distance_km=100
        )
        assert result["carbon_footprint"]["mining_kg_co2"] > 0

    def test_impact_score_range(self):
        result = self.engine.full_assessment(
            resource_tonnes=100000, grade_pct=5.0, mining_type="Surface",
            processing_steps=["crushing"], transport_distance_km=50
        )
        score = result["environmental_impact_score"]
        assert 0 <= score <= 100

    def test_carbon_calculator(self):
        calc = self.engine.carbon_calc
        result = calc.calculate(100000, 5.0, "Surface", ["crushing"], 200)
        assert result["total_kg_co2"] > 0
        assert result["mining_kg_co2"] > 0

    def test_water_calculator(self):
        calc = self.engine.water_calc
        result = calc.calculate(100000, "Surface", ["leaching"])
        assert result["total_m3"] > 0

    def test_energy_calculator(self):
        calc = self.engine.energy_calc
        result = calc.calculate(100000, "Surface", ["grinding"])
        assert result["total_mj"] > 0

    def test_waste_calculator(self):
        calc = self.engine.waste_calc
        result = calc.calculate(100000, "Surface")
        assert result["total_tonnes"] > 0
        assert result["waste_to_ore_ratio"] > 0


class TestCircularity:
    def setup_method(self):
        self.calc = CircularityCalculator()

    def test_high_recycling(self):
        result = self.calc.calculate(
            ore_processed_tonnes=100000, waste_generated_tonnes=50000,
            water_used_m3=100000, energy_consumed_mj=500000,
            recycled_material_tonnes=5000, product_output_tonnes=10000
        )
        assert 0 <= result["circularity_score"] <= 100
        assert result["material_recovery_rate"] == 50.0

    def test_zero_recycling(self):
        result = self.calc.calculate(
            ore_processed_tonnes=100000, waste_generated_tonnes=50000,
            water_used_m3=100000, energy_consumed_mj=500000,
            recycled_material_tonnes=0, product_output_tonnes=10000
        )
        assert result["material_recovery_rate"] == 0.0

    def test_recommendations_generated(self):
        result = self.calc.calculate(
            ore_processed_tonnes=100000, waste_generated_tonnes=50000,
            water_used_m3=100000, energy_consumed_mj=500000,
            recycled_material_tonnes=0, product_output_tonnes=10000
        )
        assert len(result["recommendations"]) > 0


class TestSustainability:
    def setup_method(self):
        self.scorer = SustainabilityScorer()

    def test_high_performer(self):
        result = self.scorer.calculate(
            carbon_kg=10000, water_m3=5000, energy_mj=100000,
            waste_kg=50000, recycling_rate=80, community_investment_usd=500000,
            employees=500, revenue_usd=200000000
        )
        assert result["overall_score"] > 50

    def test_grade_assignment(self):
        result = self.scorer.calculate(
            carbon_kg=1000000, water_m3=500000, energy_mj=10000000,
            waste_kg=50000000, recycling_rate=5, community_investment_usd=0,
            employees=0, revenue_usd=0
        )
        assert result["grade"] in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

    def test_benchmark_comparison(self):
        result = self.scorer.calculate(
            carbon_kg=100000, water_m3=50000, energy_mj=2000000,
            waste_kg=1000000, recycling_rate=20, community_investment_usd=100000,
            employees=200, revenue_usd=50000000
        )
        assert "benchmark_comparison" in result
        assert "vs_industry" in result["benchmark_comparison"]
