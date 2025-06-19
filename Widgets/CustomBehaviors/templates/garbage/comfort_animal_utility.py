from typing import Optional, override
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Py4GWCoreLib import GLOBAL_CACHE
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_definition import ScoreDefinition

class ComfortAnimalUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreDefinition):
        super().__init__(skill, current_build, score_definition)

    @override
    def _evaluate(self, cached_data) -> Optional[float]:
        if not self.custom_skill.is_ready():
            return None

        # Get pet ID
        pet_id = GLOBAL_CACHE.Party.Pets.GetPetID(GLOBAL_CACHE.Player.GetAgentID())
        if pet_id is None:
            return None

        # Check if pet needs healing
        if GLOBAL_CACHE.Agent.GetHealth(pet_id) >= 0.75:  # Only heal if below 75% health
            return None

        return 90  # High priority for pet healing

    @override
    def _execute(self, cached_data) -> BehaviorResult:
        pet_id = GLOBAL_CACHE.Party.Pets.GetPetID(GLOBAL_CACHE.Player.GetAgentID())
        if pet_id is None:
            return BehaviorResult.NO_ACTION

        return custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=pet_id) 