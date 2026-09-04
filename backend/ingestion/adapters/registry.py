# backend/ingestion/adapters/registry.py

from pathlib import Path

from backend.config.logging_config import get_logger
from backend.ingestion.adapters.agrowon import AgrowonAdapter
from backend.ingestion.adapters.base import ScraperAdapter
from backend.ingestion.adapters.config import load_source_config
from backend.ingestion.adapters.et_agriculture import ETAgricultureAdapter
from backend.ingestion.adapters.krishi_jagran import KrishiJagranAdapter

logger = get_logger(__name__)

_CONFIGS_DIR = Path(__file__).parent.parent / "configs"

# Explicit registration of which adapter class implements each config's
# `name`. Config files are data (base URL, selectors, rate limits) and
# can't say which Python class parses their HTML — that link has to be
# code somewhere, and here is the one place it lives. Adding a fourth
# source means adding one line here plus its config file, nothing else
# in the pipeline changes.
ADAPTER_CLASSES: dict[str, type[ScraperAdapter]] = {
    "agrowon": AgrowonAdapter,
    "et_agriculture": ETAgricultureAdapter,
    "krishi_jagran": KrishiJagranAdapter,
}


def load_all_adapters(
    configs_dir: Path = _CONFIGS_DIR,
) -> list[ScraperAdapter]:
    """
    Loads every *.yaml config in configs_dir and instantiates its
    registered adapter class. A config whose `name` has no registered
    class is skipped with a warning rather than failing the whole
    pipeline — it likely means a config was added without its adapter
    being registered yet, not that the run should abort.
    """

    adapters = []

    for config_path in sorted(configs_dir.glob("*.yaml")):

        config = load_source_config(config_path)
        adapter_class = ADAPTER_CLASSES.get(config.name)

        if adapter_class is None:
            logger.warning(
                "No adapter registered for config; skipping",
                extra={"name": config.name, "config_path": str(config_path)},
            )
            continue

        adapters.append(adapter_class(config))

    return adapters
