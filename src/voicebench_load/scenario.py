from __future__ import annotations

import random

from .config import ScenarioConfig


class ScenarioPicker:
    """Weighted deterministic scenario picker."""

    def __init__(self, scenarios: list[ScenarioConfig], seed: int = 1) -> None:
        self.scenarios = scenarios
        self.rng = random.Random(seed)
        self.total = sum(s.weight for s in scenarios)

    def pick(self) -> ScenarioConfig:
        point = self.rng.uniform(0, self.total)
        running = 0.0
        for scenario in self.scenarios:
            running += scenario.weight
            if point <= running:
                return scenario
        return self.scenarios[-1]
