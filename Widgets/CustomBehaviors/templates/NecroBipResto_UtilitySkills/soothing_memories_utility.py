from typing import Any, Generator, override
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.healing_score import HealingScore

class SoothingMemoriesUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(0), allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]):
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=allowed_states)
        self.score_definition: ScorePerHealthGravityDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        targets: list[custom_behavior_helpers.SortableAgentData] = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spellcast,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < 0.9,
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC)
        )
        
        if len(targets) == 0: return None
        is_player_holding_an_item: bool = custom_behavior_helpers.Resources.is_player_holding_an_item()

        if targets[0].hp < 0.85 and is_player_holding_an_item:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED)
        if targets[0].hp < 0.40:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
            within_range=Range.Spellcast,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < 0.95,
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC)
        )

        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target)
        return result 