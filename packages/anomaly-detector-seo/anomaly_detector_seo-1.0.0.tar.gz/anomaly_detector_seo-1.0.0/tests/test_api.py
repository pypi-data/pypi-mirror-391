from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api import main
from src.config import get_settings
from src.state import anomaly_store
from src.anomaly_detector.types import DetectionResult


@pytest.fixture(autouse=True)
def reset_store_fixture() -> None:
    anomaly_store.reset_store()
    yield
    anomaly_store.reset_store()


def _sample_event() -> dict:
    return {
        "timestamp": "2025-11-14T00:00:00Z",
        "service_name": "seo-optimizer",
        "performance": {"duration_ms": 1600},
        "http": {"response": {"status_code": 200}},
        "seo_context": {"generation_strategy": "LLM_RAG_v2"},
        "path": "/images/banner.jpg",
    }


def test_healthz_endpoint_returns_status() -> None:
    client = TestClient(main.create_app())

    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "environment" in payload


def test_latest_anomalies_returns_recent_events() -> None:
    client = TestClient(main.create_app())

    detection = DetectionResult(raw_event=_sample_event(), score=-0.7, prediction=-1)
    anomaly_store.record_detection(detection)

    response = client.get("/latest-anomalies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["prediction"] == -1


def test_metrics_endpoint_includes_drift() -> None:
    client = TestClient(main.create_app())
    detection = DetectionResult(raw_event=_sample_event(), score=-0.7, prediction=-1)
    anomaly_store.record_detection(detection)
    anomaly_store.set_drift_summary({"recent_anomaly_rate": 0.5, "baseline_anomaly_rate": 0.1, "drift_score": 0.4})

    response = client.get("/metrics")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_detections"] >= 1
    assert "drift_summary" in summary


def test_model_info_reports_path() -> None:
    client = TestClient(main.create_app())
    settings = get_settings()

    response = client.get("/model-info")
    assert response.status_code == 200
    info = response.json()
    assert info["path"] == str(settings.model_path)
    # The model artifact should exist in the repository
    assert Path(info["path"]).exists()


def test_latest_anomalies_filters_by_tenant_with_api_key(monkeypatch, tmp_path) -> None:
    base_settings = get_settings()
    tenant_settings = base_settings.model_copy(
        update={
            "multi_tenant_enabled": True,
            "tenants": ["default", "marketing"],
            "default_tenant": "default",
            "tenant_api_keys": {"marketing": "secret-token"},
            "anomaly_store_backend": "sqlite",
            "anomaly_store_sqlite_path": tmp_path / "anomalies.db",
        }
    )

    monkeypatch.setattr("src.config.get_settings", lambda: tenant_settings)
    monkeypatch.setattr("src.api.routes.get_settings", lambda: tenant_settings)
    monkeypatch.setattr("src.state.anomaly_store.get_settings", lambda: tenant_settings)
    monkeypatch.setattr("src.api.main.get_settings", lambda: tenant_settings)

    anomaly_store.reset_store()
    detection = DetectionResult(raw_event=_sample_event(), score=-0.9, prediction=-1)
    anomaly_store.record_detection(detection, tenant_id="marketing")

    client = TestClient(main.create_app())
    response = client.get(
        "/latest-anomalies",
        params={"tenant": "marketing"},
        headers={"x-api-key": "secret-token"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["service"] == "seo-optimizer"

    # Default tenant should not see marketing detections
    response_default = client.get("/latest-anomalies")
    assert response_default.status_code == 200
    assert response_default.json() == []


def test_prometheus_endpoint_exposed_when_enabled(monkeypatch) -> None:
    base_settings = get_settings()
    prometheus_settings = base_settings.model_copy(
        update={
            "prometheus_enabled": True,
            "prometheus_endpoint": "/prom",
        }
    )

    monkeypatch.setattr("src.config.get_settings", lambda: prometheus_settings)
    monkeypatch.setattr("src.api.routes.get_settings", lambda: prometheus_settings)
    monkeypatch.setattr("src.state.anomaly_store.get_settings", lambda: prometheus_settings)
    monkeypatch.setattr("src.api.main.get_settings", lambda: prometheus_settings)

    client = TestClient(main.create_app())
    response = client.get("/prom")
    assert response.status_code == 200
    assert "# HELP" in response.text
