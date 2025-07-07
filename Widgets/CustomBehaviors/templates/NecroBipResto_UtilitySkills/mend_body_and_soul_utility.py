from typing import Any, Generator, override
from Py4GWCoreLib.enums import Profession
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.healing_score import HealingScore
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_health_gravity_definition import ScorePerHealthGravityDefinition

class MendBodyAndSoulUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(0), allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]):
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=allowed_states)
        self.score_definition: ScorePerHealthGravityDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        
        lowest_target: custom_behavior_helpers.SortableAgentData | None = self._get_lowest_hp_target()
        if lowest_target is None: return None
        
        is_spirit_exist:bool = custom_behavior_helpers.Resources.is_spirit_exist(within_range=Range.Earshot)
        is_conditioned:bool = GLOBAL_CACHE.Agent.IsConditioned(lowest_target.agent_id)
        blind_or_crippled_melee_target: custom_behavior_helpers.SortableAgentData | None = self._get_melee_blind_or_crippled_if_exist()

        if lowest_target.hp < 0.40:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)
        
        if is_spirit_exist:
        
            if blind_or_crippled_melee_target is not None:
                return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)
        
            if lowest_target.hp < 0.85 and is_conditioned:
                return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED)

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        
        lowest_target: custom_behavior_helpers.SortableAgentData | None = self._get_lowest_hp_target()
        if lowest_target is None: return BehaviorResult.ACTION_SKIPPED
        
        second_target: custom_behavior_helpers.SortableAgentData | None = self._get_melee_blind_or_crippled_if_exist()
        if second_target is None: return BehaviorResult.ACTION_SKIPPED

        final_target_id: int = lowest_target.agent_id if second_target is None else second_target.agent_id
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=final_target_id)
        return result 
    
    def _get_lowest_hp_target(self) -> custom_behavior_helpers.SortableAgentData | None:

        targets: list[custom_behavior_helpers.SortableAgentData] = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spellcast,
            condition=lambda agent_id: True,
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC))
        return targets[0] if len(targets) > 0 else None

    def _get_melee_blind_or_crippled_if_exist(self) -> custom_behavior_helpers.SortableAgentData | None:
        
        from HeroAI.utils import CheckForEffect
        blind_skill_id = GLOBAL_CACHE.Skill.GetID("Blind")
        crippled_skill_id = GLOBAL_CACHE.Skill.GetID("Crippled")
        allowed_classes = [Profession.Assassin.value, Profession.Ranger.value]
        
        targets: list[custom_behavior_helpers.SortableAgentData] = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spirit,
            condition=lambda agent_id: 
                GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and 
                (CheckForEffect(agent_id, blind_skill_id) or CheckForEffect(agent_id, crippled_skill_id)),
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC))
        
        return targets[0] if len(targets) > 0 else None