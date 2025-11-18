from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock

import httpx
import pytest

from src.ingestion.loki_client import LokiClient, LokiClientError
from src.models.log_schema import LogEntry, MetricSnapshot


def _log_entry() -> LogEntry:
    return LogEntry(
        timestamp=datetime.now(tz=timezone.utc),
        service_name="seo-optimizer",
        level="INFO",
        message="Request processed",
        metrics=MetricSnapshot(response_time_ms=123.4),
        metadata={"foo": "bar"},
    )


def test_push_log_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Mock(spec=httpx.Client)
    response = Mock(spec=httpx.Response)
    response.raise_for_status.return_value = None
    client.post.return_value = response

    loki_client = LokiClient(client=client)
    loki_client.push_log(_log_entry())

    client.post.assert_called_once()


def test_push_entries_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Mock(spec=httpx.Client)
    response = Mock(spec=httpx.Response)
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error",
        request=Mock(spec=httpx.Request),
        response=Mock(status_code=500, text="failure"),
    )
    client.post.return_value = response

    loki_client = LokiClient(client=client)

    with pytest.raises(LokiClientError):
        loki_client.push_entries([_log_entry()])


def test_async_push_entries_closes_owned_client(monkeypatch: pytest.MonkeyPatch) -> None:
    async_client = Mock(spec=httpx.AsyncClient)
    response = Mock(spec=httpx.Response)
    response.raise_for_status.return_value = None

    async def fake_post(*args, **kwargs):
        return response

    async_client.post.side_effect = fake_post

    loki_client = LokiClient()

    async def run_async() -> None:
        await loki_client.apush_entries([_log_entry()], client=async_client)

    import asyncio

    asyncio.run(run_async())

    async_client.post.assert_called_once()
