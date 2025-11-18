from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest

from src.anomaly_detector.detector_core import AnomalyDetector, DetectionResult
from src.anomaly_detector.retrainer import RetrainManager
from src.anomaly_detector.trainer import train_model_from_events
from src.config import get_settings


def _make_event(duration_ms: float) -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "timestamp": now,
        "service_name": "seo-optimizer",
        "performance": {"duration_ms": duration_ms},
        "metadata": {"performance": {"duration_ms": duration_ms}},
        "seo_context": {"generation_strategy": "LLM_RAG_v2"},
    }


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()  # type: ignore[attr-defined]
    yield
    get_settings.cache_clear()  # type: ignore[attr-defined]


def _build_settings(tmp_path: Path, **overrides: object):
    base = get_settings()
    update = {
        "training_dataset_path": tmp_path / "training_logs.json",
        "model_path": tmp_path / "model.joblib",
        "retrain_state_path": tmp_path / "retrain_state.json",
        "retrain_anomaly_threshold": 1,
        "retrain_lookback_minutes": 5,
        "loki_training_limit": 50,
        "retrain_canary_enabled": False,
    }
    update.update(overrides)
    return base.model_copy(update=update)


def _make_http_client(payload: dict) -> httpx.Client:
    client = Mock(spec=httpx.Client)
    response = Mock(spec=httpx.Response)
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    client.get.return_value = response
    return client


def _make_detector(settings) -> AnomalyDetector:
    return AnomalyDetector(contamination=settings.detector_contamination)


def _prepare_base_model(settings, events: list[dict[str, object]]) -> None:
    train_model_from_events(events, contamination=settings.detector_contamination, model_path=settings.model_path)


def test_retrain_manager_uses_fallback_dataset(tmp_path: Path) -> None:
    fallback = [_make_event(1200.0), _make_event(1150.0)]
    dataset = tmp_path / "training_logs.json"
    dataset.write_text(json.dumps(fallback), encoding="utf-8")

    settings = _build_settings(tmp_path)
    _prepare_base_model(settings, fallback)
    http_client = _make_http_client({"data": {"result": []}})

    detector = _make_detector(settings)
    manager = RetrainManager(detector=detector, settings=settings, http_client=http_client)

    detection = DetectionResult(raw_event=_make_event(3000.0), score=1.0, prediction=-1)
    assert manager.maybe_retrain(detection, fallback) is True

    assert settings.model_path.exists()
    assert settings.retrain_state_path.exists()


def test_retrain_manager_skips_when_no_data(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    http_client = _make_http_client({"data": {"result": []}})

    base_events = [_make_event(1100.0), _make_event(1120.0)]
    _prepare_base_model(settings, base_events)
    detector = _make_detector(settings)
    manager = RetrainManager(detector=detector, settings=settings, http_client=http_client)

    detection = DetectionResult(raw_event=_make_event(2500.0), score=1.2, prediction=-1)
    assert manager.maybe_retrain(detection, None) is False


def test_retrain_manager_uses_loki_payload(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)

    events = [_make_event(1100.0), _make_event(1150.0)]
    _prepare_base_model(settings, events)
    loki_payload = {
        "data": {
            "result": [
                {
                    "stream": {"service": "seo-optimizer"},
                    "values": [["1700000000000000000", json.dumps(event)] for event in events],
                }
            ]
        }
    }

    http_client = _make_http_client(loki_payload)
    detector = _make_detector(settings)
    manager = RetrainManager(detector=detector, settings=settings, http_client=http_client)

    detection = DetectionResult(raw_event=_make_event(4000.0), score=1.0, prediction=-1)
    assert manager.maybe_retrain(detection, events) is True
    assert settings.model_path.exists()


def test_retrain_manager_canary_promotion(tmp_path: Path) -> None:
    fallback = [_make_event(1200.0 + i * 10) for i in range(5)]
    dataset = tmp_path / "training_logs.json"
    dataset.write_text(json.dumps(fallback), encoding="utf-8")

    settings = _build_settings(
        tmp_path,
        retrain_canary_enabled=True,
        retrain_canary_validation_cycles=2,
        retrain_canary_divergence_threshold=0.5,
    )

    http_client = _make_http_client({"data": {"result": []}})
    base_events = [_make_event(1200.0 + i * 5) for i in range(5)]
    _prepare_base_model(settings, base_events)
    detector = _make_detector(settings)
    manager = RetrainManager(detector=detector, settings=settings, http_client=http_client)

    detection = DetectionResult(raw_event=_make_event(5000.0), score=1.0, prediction=-1)
    assert manager.maybe_retrain(detection, fallback) is True

    candidate_path = settings.model_path.with_name(settings.model_path.name + ".candidate")
    assert candidate_path.exists()
    assert manager._candidate_detector is not None  # pylint: disable=protected-access

    # Evaluate candidate across required cycles
    for _ in range(settings.retrain_canary_validation_cycles):
        assert manager.maybe_retrain(None, fallback) is False

    assert not candidate_path.exists()
    assert settings.model_path.exists()
