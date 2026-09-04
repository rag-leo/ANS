"""
Confirms each adapter's rate limit is actually enforced during
fetch() at runtime — not just parsed into config and left unused.

Each test drives two consecutive fetch() calls through the real
adapter code path (robots.txt check -> rate limiter -> the actual
HTTP/Selenium call), with only the network/browser boundary mocked
out, and asserts wall-clock time actually elapsed by at least the
configured min_interval_seconds.
"""

import time
from unittest.mock import MagicMock, patch

from backend.ingestion.adapters.agrowon import AgrowonAdapter
from backend.ingestion.adapters.config import load_source_config
from backend.ingestion.adapters.et_agriculture import ETAgricultureAdapter
from backend.ingestion.adapters.krishi_jagran import KrishiJagranAdapter

_TEST_INTERVAL_SECONDS = 0.3


def _load_config_with_short_interval(name: str):

    config = load_source_config(
        f"backend/ingestion/configs/{name}.yaml"
    )
    config.rate_limit.min_interval_seconds = _TEST_INTERVAL_SECONDS
    config.rate_limit.respect_crawl_delay = False
    config.retry.max_attempts = 1

    return config


def _stub_robots(adapter) -> None:
    """Bypasses the real robots.txt network fetch for these tests."""

    adapter._robots.is_allowed = lambda url: True
    adapter._robots.crawl_delay = lambda: None


def test_et_agriculture_fetch_respects_configured_interval():

    config = _load_config_with_short_interval("et_agriculture")
    adapter = ETAgricultureAdapter(config)
    _stub_robots(adapter)

    fake_response = MagicMock()
    fake_response.text = "<html></html>"
    fake_response.raise_for_status.return_value = None

    with patch.object(
        adapter._session, "get", return_value=fake_response
    ) as mock_get:

        start = time.monotonic()
        adapter.fetch("https://agriculture.economictimes.indiatimes.com/x")
        adapter.fetch("https://agriculture.economictimes.indiatimes.com/y")
        elapsed = time.monotonic() - start

    assert mock_get.call_count == 2
    assert elapsed >= _TEST_INTERVAL_SECONDS, (
        f"two fetches completed in {elapsed:.3f}s, "
        f"expected >= {_TEST_INTERVAL_SECONDS}s from the rate limiter"
    )


def test_krishi_jagran_fetch_respects_configured_interval():

    config = _load_config_with_short_interval("krishi_jagran")
    adapter = KrishiJagranAdapter(config)
    _stub_robots(adapter)

    fake_response = MagicMock()
    fake_response.text = "<html></html>"
    fake_response.raise_for_status.return_value = None

    with patch.object(
        adapter._session, "get", return_value=fake_response
    ) as mock_get:

        start = time.monotonic()
        adapter.fetch("https://krishijagran.com/news/x/")
        adapter.fetch("https://krishijagran.com/news/y/")
        elapsed = time.monotonic() - start

    assert mock_get.call_count == 2
    assert elapsed >= _TEST_INTERVAL_SECONDS, (
        f"two fetches completed in {elapsed:.3f}s, "
        f"expected >= {_TEST_INTERVAL_SECONDS}s from the rate limiter"
    )


def test_agrowon_fetch_respects_configured_interval():

    config = _load_config_with_short_interval("agrowon")
    adapter = AgrowonAdapter(config)
    _stub_robots(adapter)

    fake_driver = MagicMock()
    fake_driver.page_source = "<html><h1>x</h1></html>"

    with patch.object(
        AgrowonAdapter, "_create_driver", return_value=fake_driver
    ):

        start = time.monotonic()
        adapter.fetch("https://agrowon.esakal.com/section/article-abc123")
        adapter.fetch("https://agrowon.esakal.com/section/article-def456")
        elapsed = time.monotonic() - start

    assert fake_driver.get.call_count == 2
    assert elapsed >= _TEST_INTERVAL_SECONDS, (
        f"two fetches completed in {elapsed:.3f}s, "
        f"expected >= {_TEST_INTERVAL_SECONDS}s from the rate limiter"
    )


def test_rate_limit_is_read_from_config_not_hardcoded():
    """
    Sets a distinct interval per source and confirms each adapter's
    live RateLimiter instance actually picked up its own source's
    configured value, not a shared/hardcoded default.
    """

    intervals = {}

    for index, (name, adapter_cls) in enumerate(
        [
            ("agrowon", AgrowonAdapter),
            ("et_agriculture", ETAgricultureAdapter),
            ("krishi_jagran", KrishiJagranAdapter),
        ]
    ):

        distinct_value = 1.0 + index  # 1.0, 2.0, 3.0 - all different
        config = load_source_config(
            f"backend/ingestion/configs/{name}.yaml"
        )
        config.rate_limit.min_interval_seconds = distinct_value
        config.rate_limit.respect_crawl_delay = False

        adapter = adapter_cls(config)
        intervals[name] = adapter._get_rate_limiter()._min_interval

        assert intervals[name] == distinct_value

    # every source's limiter reflects its own config, not one shared value
    assert len(set(intervals.values())) == 3
