from typing import Any, Generator, override
from Py4GWCoreLib import Agent, Range, GLOBAL_CACHE, Player
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.scores.healing_score import HealingScore
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.bonds.custom_buff_target_per_profession import BuffConfigurationPerProfession
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class BreathOfTheGreatDwarfUtility(CustomSkillUtilityBase):
    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(1),
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]
        ) -> None:

            super().__init__(
                event_bus=event_bus,
                skill=CustomSkill("Breath_of_the_Great_Dwarf"),
                in_game_build=current_build,
                score_definition=score_definition,
                allowed_states=allowed_states)
            
            self.score_definition: ScorePerHealthGravityDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        if custom_behavior_helpers.Heals.is_party_damaged(within_range=Range.Spirit.value, min_allies_count=3, less_health_than_percent=0.4):
            return self.score_definition.get_score(HealingScore.PARTY_DAMAGE_EMERGENCY)

        first_member_damaged: int | None = custom_behavior_helpers.Heals.get_first_member_damaged(within_range=Range.Spirit.value, less_health_than_percent=0.4, exclude_player=False)
        if first_member_damaged is not None:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)

        if custom_behavior_helpers.Heals.is_party_damaged(within_range=Range.Spirit.value, min_allies_count=3, less_health_than_percent=0.75):
            return self.score_definition.get_score(HealingScore.PARTY_DAMAGE)

        # more than X allies burning

        burning_skill_id:int = GLOBAL_CACHE.Skill.GetID("Burning")

        allies = TargetingAlly.create().get_allies(
            within_range=Range.Spirit.value,
            condition_predicate= lambda ally_data: Agent.GetHealth(ally_data.agent_id) < 0.85
                and custom_behavior_helpers.Resources.is_ally_under_specific_effect(ally_data.agent_id, burning_skill_id),
            sort_asc_predicate= lambda ally_data: (ally_data.hp, ally_data.distance_from_player))

        if len(allies) > 1: return self.score_definition.get_score(HealingScore.PARTY_DAMAGE)

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result 