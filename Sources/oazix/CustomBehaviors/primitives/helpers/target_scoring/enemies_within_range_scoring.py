

from Py4GWCoreLib import Agent
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData

class AgentsWithinRangeScoring:

    def __init__(self):
        pass

    @staticmethod
    def get_score(enemy_id: int, agent_ids: list[int], within_range: float) -> int:
        agent_pos = Agent.GetXY(enemy_id)
        agent_count = 0
        for other_agent_id in agent_ids:
            if other_agent_id == enemy_id: continue
            if Utils.Distance(agent_pos, Agent.GetXY(other_agent_id)) <= within_range:
                agent_count += 1

        return agent_count