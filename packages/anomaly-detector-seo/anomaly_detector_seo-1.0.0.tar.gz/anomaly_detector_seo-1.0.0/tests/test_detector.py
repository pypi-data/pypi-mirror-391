from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.anomaly_detector.detector_core import AnomalyDetector

# Tests exercise internal helpers for coverage of feature engineering.
# pylint: disable=protected-access


def _make_event(duration_ms: float, strategy: str = "LLM_RAG_v2") -> dict:
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    seo_context = {
        "generation_strategy": strategy,
        "experiment_group": "control",
        "traffic_segment": "organic",
    }
    return {
        "timestamp": timestamp,
        "service_name": "seo-optimizer",
        "performance": {"duration_ms": duration_ms},
        "metadata": {
            "performance": {"duration_ms": duration_ms},
            "seo_context": seo_context,
        },
        "seo_context": seo_context,
    }


def test_prepare_data_encodes_context_columns() -> None:
    detector = AnomalyDetector(contamination=0.1, random_state=42)

    frame = detector._prepare_data([_make_event(1200.0, strategy="Keyword_Templating")])

    assert "duration_ms" in frame.columns
    encoded_columns = [col for col in frame.columns if col.startswith("generation_strategy_")]
    assert encoded_columns, "Expected one-hot encoded generation strategy column"


def test_export_model_requires_training() -> None:
    detector = AnomalyDetector(contamination=0.1, random_state=42)

    with pytest.raises(RuntimeError):
        detector.export_model()


def test_detect_flags_outlier_event() -> None:
    detector = AnomalyDetector(contamination=0.05, random_state=42)

    normal_events = [
        _make_event(1100 + i * 5, strategy="LLM_RAG_v2" if i % 3 else "Keyword_Templating")
        for i in range(30)
    ]
    detector.fit(normal_events)

    anomalous_event = _make_event(4000.0, strategy="Keyword_Templating")
    detection = detector.detect(normal_events + [anomalous_event])

    assert detection.raw_event == anomalous_event
    assert detection.prediction in (-1, 1)
    assert detection.score != 0.0

    # High latency outliers should be flagged as anomalies with the chosen contamination ratio
    assert detection.prediction == -1
