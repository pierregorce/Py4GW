from typing import Any, Generator, override
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition

class BloodBondUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 25 if enemy_qte >= 2 else 0), mana_required_to_cast: int = 15):
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, mana_required_to_cast=mana_required_to_cast)
        self.score_definition: ScorePerAgentQuantityDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        if current_state is BehaviorState.FAR_FROM_AGGRO: return None
        if current_state is BehaviorState.CLOSE_TO_AGGRO: return None

        if custom_behavior_helpers.Resources.get_player_absolute_energy() < 15: return None

        # Check if we have a valid target
        targets = custom_behavior_helpers.Targets.get_all_possible_enemies_ordered_by_priority_raw(
            within_range=Range.Spellcast,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.4,
            sort_key=(TargetingOrder.DISTANCE_ASC, TargetingOrder.HP_ASC),
            range_to_count_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id))
        
        if len(targets) == 0: return 0
        return self.score_definition.get_score(targets[0].enemy_quantity_within_range)

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        targets = custom_behavior_helpers.Targets.get_all_possible_enemies_ordered_by_priority_raw(
            within_range=Range.Spellcast,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.4,
            sort_key=(TargetingOrder.DISTANCE_ASC, TargetingOrder.HP_ASC),
            range_to_count_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id))

        if len(targets) == 0: return BehaviorResult.ACTION_SKIPPED
        target_id = targets[0].agent_id
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target_id)
        return result 