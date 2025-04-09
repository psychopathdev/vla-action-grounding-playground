from voicebench_load.config import ScenarioConfig
from voicebench_load.scenario import ScenarioPicker


def test_scenario_picker_returns_config() -> None:
    picker = ScenarioPicker([ScenarioConfig("a", 1), ScenarioConfig("b", 1)], seed=1)
    assert picker.pick().name in {"a", "b"}
