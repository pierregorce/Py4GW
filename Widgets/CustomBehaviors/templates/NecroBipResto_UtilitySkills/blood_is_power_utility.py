from typing import Any, Generator, override
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE, Profession
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class BloodIsPowerUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition = ScoreStaticDefinition(33), allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]):
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=allowed_states)
        self.sacrifice_life_limit_percent: float = 0.55
        self.sacrifice_life_limit_absolute: float = 175
        self.score_definition: ScoreStaticDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        heath_max = GLOBAL_CACHE.Agent.GetMaxHealth(GLOBAL_CACHE.Player.GetAgentID())
        amount_we_can_sacrifice = heath_max * 0.33
        player_health_absolute = custom_behavior_helpers.Resources.get_player_absolute_health()
        player_health_percent = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID())
        
        # Check if we have enough health to sacrifice
        if player_health_absolute - amount_we_can_sacrifice < self.sacrifice_life_limit_absolute or (player_health_absolute - amount_we_can_sacrifice) / heath_max <= self.sacrifice_life_limit_percent:
            return None

        # Check if we have a valid target with low energy
        allowed_classes = [Profession.Mesmer.value, Profession.Ritualist.value]
        allowed_agent_names = ["to_be_implemented"]
        from HeroAI.utils import CheckForEffect
    
        target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id:
                    agent_id != GLOBAL_CACHE.Player.GetAgentID() and
                    custom_behavior_helpers.Resources.get_energy_percent_in_party(agent_id) < 0.40 and
                    GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and
                    not CheckForEffect(agent_id, self.custom_skill.skill_id),
                sort_key=(TargetingOrder.ENERGY_ASC, TargetingOrder.DISTANCE_ASC),
                range_to_count_enemies=None,
                range_to_count_allies=None)

        if target is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        
        allowed_classes = [Profession.Mesmer.value, Profession.Ritualist.value]
        allowed_agent_names = ["to_be_implemented"]
        from HeroAI.utils import CheckForEffect
    
        target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id:
                    agent_id != GLOBAL_CACHE.Player.GetAgentID() and
                    custom_behavior_helpers.Resources.get_energy_percent_in_party(agent_id) < 0.40 and
                    GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and
                    not CheckForEffect(agent_id, self.custom_skill.skill_id),
                sort_key=(TargetingOrder.ENERGY_ASC, TargetingOrder.DISTANCE_ASC),
                range_to_count_enemies=None,
                range_to_count_allies=None)

        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target)
        return result 