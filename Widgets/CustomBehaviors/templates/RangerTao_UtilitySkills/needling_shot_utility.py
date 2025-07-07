from typing import Any, Generator, override
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Range, GLOBAL_CACHE, Routines
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class NeedlingShotUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition):
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition)

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        if current_state is not BehaviorState.IN_AGGRO: return None
        if custom_behavior_helpers.Resources.get_player_absolute_energy() < 10: return None

        # Check if we have a valid target with less than 50% health
        target = custom_behavior_helpers.Targets.get_first_or_default_from_enemy_ordered_by_priority(
            within_range=Range.Spellcast,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < 0.50,
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.CASTER_THEN_MELEE, TargetingOrder.AGENT_QUANTITY_WITHIN_RANGE_ASC)
        )

        if target is None: return None
        return 90  # High priority for low health targets

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        target = custom_behavior_helpers.Targets.get_first_or_default_from_enemy_ordered_by_priority(
            within_range=Range.Spellcast,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < 0.50,
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.CASTER_THEN_MELEE, TargetingOrder.AGENT_QUANTITY_WITHIN_RANGE_ASC)
        )

        if target is None: return BehaviorResult.ACTION_SKIPPED

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target)
        return result 