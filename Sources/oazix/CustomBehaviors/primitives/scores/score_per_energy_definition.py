from typing import override

from Py4GWCoreLib import Agent, Player
from Sources.oazix.CustomBehaviors.primitives.scores.score_definition import ScoreDefinition


class ScorePerEnergyDefinition(ScoreDefinition):
   
    def __init__(self,
                 score_nominal: float,
                 score_boosted: float,
                 only_cast_if_energy_below: float = 0.85,
                 low_mana_threshold: float = 0.30):
        super().__init__()
        self.score_nominal: float = score_nominal
        self.score_boosted: float = score_boosted
        self.low_mana_threshold: float = low_mana_threshold # above this threshold, score is None 
        self.only_cast_if_energy_below: float = only_cast_if_energy_below # below this threshold, score is boosted

    def get_score(self) -> float | None:
        
        player_agent_id = Player.GetAgentID()
        player_energy_percent = Agent.GetEnergy(player_agent_id)
        if player_energy_percent > self.low_mana_threshold:
            return None

        if player_energy_percent < self.only_cast_if_energy_below:
            return self.score_boosted
        
        return self.score_nominal

    @override
    def score_definition_debug_ui(self) -> str:
        return f"score is {self.score_boosted:06.4f} (<={self.only_cast_if_energy_below*100:.0f}%) / {self.score_nominal:06.4f} (@{self.low_mana_threshold*100:.0f}%) / blocked above {self.low_mana_threshold*100:.0f}%"
    