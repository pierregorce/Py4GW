
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.helpers.custom_behavior_helpers_party import CustomBehaviorHelperParty

class PartyLeaderCalledTargetOverride:

    def __init__(self):
        pass

    @staticmethod
    def override(data_to_sort: list[TargetingEnemyData]) -> list[TargetingEnemyData]:
        
        party_forced_target_agent_id: int | None = CustomBehaviorHelperParty.get_party_custom_target()

        if party_forced_target_agent_id is None: return data_to_sort

        result = data_to_sort.copy()

        # Final sort: move party forced target to the front if it exists in the array
        forced_target_index = next((i for i, x in enumerate(result) if x.agent_id == party_forced_target_agent_id), None)
        if forced_target_index is not None:
            forced_target = result.pop(forced_target_index)
            result.insert(0, forced_target)
                
        return result