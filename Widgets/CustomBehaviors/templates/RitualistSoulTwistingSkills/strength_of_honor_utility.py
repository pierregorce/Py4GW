from typing import Any, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Player, Routines, Range
from Py4GWCoreLib.enums import Profession
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class StrengthOfHonorUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition) -> None:
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO])
        self.score_definition: ScoreStaticDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        
        # Check if we have a valid target with low energy
        allowed_classes = [Profession.Assassin.value]
        allowed_agent_names = ["to_be_implemented"]
        from HeroAI.utils import CheckForEffect
    
        target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id:
                    agent_id != GLOBAL_CACHE.Player.GetAgentID() and
                    GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and
                    not CheckForEffect(agent_id, self.custom_skill.skill_id),
                sort_key=(TargetingOrder.DISTANCE_ASC,),
                range_to_count_enemies=None,
                range_to_count_allies=None)

        if target is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        
        allowed_classes = [Profession.Assassin.value]
        allowed_agent_names = ["to_be_implemented"]
        from HeroAI.utils import CheckForEffect
    
        target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id:
                    agent_id != GLOBAL_CACHE.Player.GetAgentID() and
                    GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and
                    not CheckForEffect(agent_id, self.custom_skill.skill_id),
                sort_key=(TargetingOrder.DISTANCE_ASC,),
                range_to_count_enemies=None,
                range_to_count_allies=None)

        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target)
        return result 