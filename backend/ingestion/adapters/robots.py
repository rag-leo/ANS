# backend/ingestion/adapters/robots.py

import urllib.request

from protego import Protego

from backend.config.logging_config import get_logger

logger = get_logger(__name__)


class RobotsChecker:
    """
    Fetches and caches robots.txt for a single source (base URL +
    user agent), shared by an adapter across all its requests.

    Uses `protego` rather than the standard library's
    `urllib.robotparser`: many sites' robots.txt rely on `*`
    wildcard Disallow patterns, which `robotparser` silently fails
    to match (it treats `*` as a literal character). `protego`
    implements the wildcard-aware matching real crawlers use.
    """

    def __init__(self, robots_txt_url: str, user_agent: str) -> None:

        self._robots_txt_url = robots_txt_url
        self._user_agent = user_agent
        self._parser: Protego | None = None
        self._fetched = False

    def _get_parser(self) -> Protego | None:
        """
        Returns None if robots.txt can't be retrieved at all, in
        which case callers should fail open rather than block
        scraping over a transient network issue.
        """

        if self._fetched:
            return self._parser

        self._fetched = True

        try:
            request = urllib.request.Request(
                self._robots_txt_url,
                headers={"User-Agent": self._user_agent},
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                content = response.read().decode("utf-8", errors="replace")

            self._parser = Protego.parse(content)

        except Exception:
            logger.exception(
                "Failed to fetch robots.txt; "
                "proceeding without robots.txt checks",
                extra={"robots_txt_url": self._robots_txt_url},
            )
            self._parser = None

        return self._parser

    def is_allowed(self, url: str) -> bool:

        parser = self._get_parser()

        if parser is None:
            return True

        return parser.can_fetch(url, self._user_agent)

    def crawl_delay(self) -> float | None:

        parser = self._get_parser()

        if parser is None:
            return None

        delay = parser.crawl_delay(self._user_agent)

        return float(delay) if delay else None
