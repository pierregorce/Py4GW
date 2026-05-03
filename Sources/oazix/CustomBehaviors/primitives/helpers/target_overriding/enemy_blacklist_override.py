from Py4GWCoreLib.EnemyBlacklist import EnemyBlacklist
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData

class EnemyBlacklistOverride:
    def __init__(self):
        pass

    @staticmethod
    def override(data_to_sort: list[TargetingEnemyData]) -> list[TargetingEnemyData]:

        # Filter out enemies whose model ID or name is on the blacklist
        _bl = EnemyBlacklist()
        if not _bl.is_empty():
            result = [a for a in data_to_sort if not _bl.is_blacklisted(a.agent_id)]
            return result
        
        return data_to_sort