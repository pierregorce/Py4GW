from Py4GWCoreLib import Agent
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE


class SimpleInterruptPotentialScoring:

    def __init__(self, skills_cast_time_longer_than: float = 0.250):
        self.skills_cast_time_longer_than: float = skills_cast_time_longer_than

    def get_score(self, agent_id: int) -> float:

        # simple algorithm for now.

        if not Agent.IsCasting(agent_id): return 0.0
        casting_skill_id = Agent.GetCastingSkillID(agent_id)
        casting_skill_activation = GLOBAL_CACHE.Skill.Data.GetActivation(casting_skill_id)
        if casting_skill_activation < self.skills_cast_time_longer_than: return 0.0
        return 100
        