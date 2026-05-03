from dataclasses import dataclass

@dataclass
class TargetingEnemyData:
    agent_id: int
    distance_from_player: float
    hp: float
    is_caster: bool
    is_melee: bool
    is_martial: bool

    enemy_quantity_within_range: int
    enemy_and_ally_quantity_within_range: int
    
    melee_optimised_aoe_score: float
    interrupt_potential_score: float

    '''
    multiple implementations can be set, such as 
        - per_model_id_priority
        - per_name_priority, per_profession_priority
        - per_party_leader_target, 
        etc...
    '''
    overidden_score: float | None