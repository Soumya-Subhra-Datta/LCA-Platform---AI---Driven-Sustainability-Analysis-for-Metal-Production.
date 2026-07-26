import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, engine, Base


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def registered_user(client):
    resp = client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "test@example.com",
        "password": "TestPass123", "full_name": "Test User"
    })
    return resp.json()


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestAuthentication:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "newuser", "email": "new@example.com",
            "password": "NewPass123", "full_name": "New User"
        })
        assert resp.status_code == 201

    def test_register_duplicate(self, client, registered_user):
        resp = client.post("/api/v1/auth/register", json={
            "username": "testuser", "email": "test@example.com",
            "password": "TestPass123", "full_name": "Test"
        })
        assert resp.status_code == 409

    def test_register_invalid_email(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "bad", "email": "not-an-email",
            "password": "TestPass123", "full_name": ""
        })
        assert resp.status_code == 400

    def test_register_weak_password(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "weak", "email": "weak@test.com",
            "password": "123", "full_name": ""
        })
        assert resp.status_code == 400

    def test_login_success(self, client, registered_user):
        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "TestPass123"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "WrongPass"
        })
        assert resp.status_code == 401


class TestDatasets:
    def test_list_datasets(self, client):
        resp = client.get("/api/v1/datasets/")
        assert resp.status_code == 200
        data = resp.json()
        assert "datasets" in data

    def test_get_dataset_info(self, client):
        resp = client.get("/api/v1/datasets/mining_projects")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "mining_projects"
        assert data["rows"] > 0

    def test_get_dataset_not_found(self, client):
        resp = client.get("/api/v1/datasets/nonexistent")
        assert resp.status_code == 404

    def test_get_dataset_sample(self, client):
        resp = client.get("/api/v1/datasets/mining_projects/sample?rows=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["sample"]) <= 3

    def test_get_dataset_stats(self, client):
        resp = client.get("/api/v1/datasets/mining_projects/stats")
        assert resp.status_code == 200
        assert "numeric_stats" in resp.json()


class TestPredictions:
    def test_list_models(self, client):
        resp = client.get("/api/v1/predictions/models")
        assert resp.status_code == 200
        models = resp.json()["models"]
        assert len(models) == 4

    def test_train_models(self, client):
        resp = client.post("/api/v1/predictions/train")
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert "hree_predictor" in results

    def test_predict_hree(self, client):
        resp = client.post("/api/v1/predictions/predict", json={
            "model_name": "hree_predictor",
            "input_data": {
                "log_resource": 6.0, "grade_pct": 3.0,
                "continent_encoded": 1, "deposit_type_encoded": 1,
            }
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert "hree_percentage" in data["result"]

    def test_predict_deposit(self, client):
        resp = client.post("/api/v1/predictions/predict", json={
            "model_name": "deposit_classifier",
            "input_data": {
                "log_resource": 5.0, "grade_pct": 2.0,
                "continent_encoded": 0, "deposit_type_encoded": 0,
            }
        })
        assert resp.status_code == 200
        assert "deposit_type" in resp.json()["result"]

    def test_get_metrics(self, client):
        resp = client.get("/api/v1/predictions/metrics")
        assert resp.status_code == 200


class TestLCA:
    def test_run_lca_assessment(self, client):
        resp = client.post("/api/v1/environmental/assess", json={
            "facility_name": "Test Mine",
            "resource_tonnes": 100000,
            "grade_pct": 5.0,
            "mining_type": "Surface",
            "transport_distance_km": 200,
            "processing_method": "crushing,grinding,leaching,solvent_extraction",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "carbon_footprint" in data
        assert "water_footprint" in data
        assert "summary" in data

    def test_get_benchmarks(self, client):
        resp = client.get("/api/v1/environmental/benchmarks")
        assert resp.status_code == 200


class TestCircularity:
    def test_calculate_circularity(self, client):
        resp = client.post("/api/v1/circularity/calculate", json={
            "ore_processed_tonnes": 100000,
            "waste_generated_tonnes": 50000,
            "water_used_m3": 100000,
            "energy_consumed_mj": 500000,
            "recycled_material_tonnes": 500,
            "product_output_tonnes": 5000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "circularity_score" in data
        assert 0 <= data["circularity_score"] <= 100

    def test_calculate_sustainability(self, client):
        resp = client.post("/api/v1/circularity/sustainability", json={
            "carbon_footprint_kg_co2": 500000,
            "water_footprint_m3": 100000,
            "energy_consumption_mj": 2000000,
            "waste_generation_kg": 5000000,
            "recycling_rate": 15,
            "community_investment_usd": 50000,
            "employees": 200,
            "revenue_usd": 50000000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_score" in data
        assert "grade" in data


class TestReports:
    def test_generate_report(self, client):
        resp = client.post("/api/v1/reports/generate?report_type=comprehensive&title=Test Report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test Report"
        assert "content" in data

    def test_list_reports(self, client):
        resp = client.get("/api/v1/reports/")
        assert resp.status_code == 200


class TestDashboard:
    def test_get_dashboard(self, client):
        resp = client.get("/api/v1/dashboard/")
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "datasets" in data
