from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from src.anomaly_detector.orchestrator import DetectionOrchestrator, generate_rca_summary
from src.anomaly_detector.types import DetectionResult
from src.config import get_settings
from src.main_scheduler import main_loop, parse_args
from src.state import anomaly_store


@pytest.fixture(autouse=True)
def clear_settings_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()  # type: ignore[attr-defined]
    anomaly_store.reset_store()
    monkeypatch.setattr("src.anomaly_detector.drift_monitor.evaluate_drift", lambda *_, **__: None)
    yield
    get_settings.cache_clear()  # type: ignore[attr-defined]
    anomaly_store.reset_store()


def _sample_raw_event() -> dict:
    return {
        "timestamp": "2025-11-14T00:00:00Z",
        "service_name": "seo-optimizer",
        "performance": {"duration_ms": 1600},
        "http": {"response": {"status_code": 200}},
        "seo_context": {"generation_strategy": "LLM_RAG_v2"},
    }


def test_run_once_triggers_notification(monkeypatch: pytest.MonkeyPatch) -> None:
    detector = Mock()
    notifier = Mock()
    http_client = Mock()

    orchestrator = DetectionOrchestrator(
        detector=detector,
        notifier=notifier,
        loki_query="{service=\"seo-optimizer\"}",
        http_client=http_client,
    )

    events = [_sample_raw_event()]
    monkeypatch.setattr(orchestrator, "_fetch_recent_logs", Mock(return_value=events))

    detection = DetectionResult(raw_event=_sample_raw_event(), score=-0.5, prediction=-1)
    detector.detect.return_value = detection

    detection, events = orchestrator.run_once()

    notifier.notify.assert_called_once()
    _, kwargs = notifier.notify.call_args
    context = kwargs["context"]
    assert context["prediction"] == -1
    assert "rca_prompt" in context
    assert detection is not None
    assert events


def test_run_once_skips_notification_when_no_anomaly(monkeypatch: pytest.MonkeyPatch) -> None:
    detector = Mock()
    notifier = Mock()
    http_client = Mock()

    orchestrator = DetectionOrchestrator(
        detector=detector,
        notifier=notifier,
        loki_query="{service=\"seo-optimizer\"}",
        http_client=http_client,
    )

    events = [_sample_raw_event()]
    monkeypatch.setattr(orchestrator, "_fetch_recent_logs", Mock(return_value=events))

    detection = DetectionResult(raw_event=_sample_raw_event(), score=0.1, prediction=1)
    detector.detect.return_value = detection

    detection, events = orchestrator.run_once()

    notifier.notify.assert_not_called()
    assert detection is not None
    assert events


def test_generate_rca_summary_contains_sections() -> None:
    prompt = generate_rca_summary(_sample_raw_event())
    assert "## Observabilidad" in prompt
    assert "## SEO Context" in prompt
    assert "## Log Completo" in prompt


def test_emit_metric_logs_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    detector = Mock()
    detector.detect.return_value = DetectionResult(
        raw_event=_sample_raw_event(), score=0.5, prediction=1
    )
    notifier = Mock()
    orchestrator = DetectionOrchestrator(
        detector=detector,
        notifier=notifier,
        loki_query="{}",
    )

    logged_payload: list[dict] = []

    def fake_info(message: str) -> None:
        logged_payload.append(json.loads(message))

    monkeypatch.setattr("src.anomaly_detector.orchestrator.metrics_logger.info", fake_info)
    monkeypatch.setattr(orchestrator, "_fetch_recent_logs", Mock(return_value=[_sample_raw_event()]))

    orchestrator.run_once()

    assert logged_payload, "Expected metrics payload to be logged"
    payload = logged_payload[0]
    assert payload["stream"]
    assert payload["prediction"] == 1


def test_main_loop_handles_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator = Mock()
    orchestrator.run_once.side_effect = [ (None, []), KeyboardInterrupt() ]

    sleep_calls: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("src.main_scheduler.time.sleep", fake_sleep)

    main_loop(orchestrator, interval=1, retrain_manager=None)

    assert orchestrator.run_once.call_count == 2
    assert sleep_calls and sleep_calls[0] >= 0


def test_parse_args_respects_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DETECTION_INTERVAL_SECONDS", "45")
    monkeypatch.setenv("DETECTION_LOOKBACK_MINUTES", "7")
    monkeypatch.setenv("DETECTOR_CONTAMINATION", "0.12")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    settings = get_settings()
    args = parse_args(settings, [])
    assert args.interval == 45
    assert args.lookback == 7
    assert args.contamination == 0.12
