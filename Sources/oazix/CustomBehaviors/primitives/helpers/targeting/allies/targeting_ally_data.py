from dataclasses import dataclass

@dataclass
class TargetingAllyData:
    agent_id: int
    distance_from_player: float
    hp: float
    energy: float

    enemy_quantity_within_range: int
    anemy_and_ally_quantity_within_range: int
    ally_quantity_within_range: int

    hex_priority_score: int
    condition_priority_score: int
        

    overidden_score: float | None