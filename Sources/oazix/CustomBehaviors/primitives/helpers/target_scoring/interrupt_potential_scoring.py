from Py4GWCoreLib import Agent
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE


class InterruptPotentialScoring:
    def __init__(self):
        pass

    def get_score(self, agent_id: int) -> float:

        # simple algorithm for now.

        if not Agent.IsCasting(agent_id): return 0.0
        casting_skill_id = Agent.GetCastingSkillID(agent_id)
        casting_skill_activation = GLOBAL_CACHE.Skill.Data.GetActivation(casting_skill_id)
        if casting_skill_activation < 0.250: return 0.0
        return 100
        