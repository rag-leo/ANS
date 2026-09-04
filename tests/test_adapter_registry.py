from backend.ingestion.adapters.agrowon import AgrowonAdapter
from backend.ingestion.adapters.et_agriculture import ETAgricultureAdapter
from backend.ingestion.adapters.krishi_jagran import KrishiJagranAdapter
from backend.ingestion.adapters.registry import load_all_adapters


def test_load_all_adapters_registers_all_three_sources():

    adapters = load_all_adapters()

    by_name = {a.config.name: a for a in adapters}

    assert set(by_name) == {"agrowon", "et_agriculture", "krishi_jagran"}
    assert isinstance(by_name["agrowon"], AgrowonAdapter)
    assert isinstance(by_name["et_agriculture"], ETAgricultureAdapter)
    assert isinstance(by_name["krishi_jagran"], KrishiJagranAdapter)


def test_each_adapter_has_its_own_source_label():

    adapters = load_all_adapters()
    labels = {a.config.source_label for a in adapters}

    assert labels == {"Agrowon", "ET Agriculture", "Krishi Jagran"}
