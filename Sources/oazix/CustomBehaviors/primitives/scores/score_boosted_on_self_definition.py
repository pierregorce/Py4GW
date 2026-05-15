from typing import override

from Py4GWCoreLib import Player
from Sources.oazix.CustomBehaviors.primitives.scores.score_definition import ScoreDefinition


class ScoreBoostedOnSelfDefinition(ScoreDefinition):
    """
    Score definition with two values: boosted and nominal.
    Used when a skill should have different priorities based on whether it targets self or other.
    """

    def __init__(self, score_nominal: float, score_boosted: float | None = None):
        super().__init__()
        self.score_nominal: float = score_nominal
        self.score_boosted: float = score_boosted if score_boosted is not None else score_nominal

    def get_score(self, agent_id: int) -> float:
        if agent_id == Player.GetAgentID():
            return self.score_boosted
        
        return self.score_nominal

    @override
    def score_definition_debug_ui(self) -> str:
        return f"score is {self.score_boosted:06.4f} (boosted) / {self.score_nominal:06.4f} (nominal)"

