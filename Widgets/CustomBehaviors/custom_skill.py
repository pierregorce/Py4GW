from Py4GWCoreLib import GLOBAL_CACHE

class CustomSkill:
    def __init__(self, skill_name: str):
        self.skill_name: str = skill_name
        self.skill_id: int = GLOBAL_CACHE.Skill.GetID(skill_name)