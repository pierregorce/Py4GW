from typing import Any, Generator, override, Tuple

from Py4GWCoreLib import GLOBAL_CACHE, Range, Agent, Player
from Py4GWCoreLib.AgentArray import AgentArray
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_allegiance import TargetingAllyAllegiance
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class DeathNovaUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(29),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Death_Nova"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
        
        self.score_definition: ScoreStaticDefinition = score_definition

    @staticmethod
    def _get_target() -> int | None:

        minions = TargetingAlly().create().get_allies(
            within_range=Range.Spellcast.value,
            allegiance_to_include=TargetingAllyAllegiance.Minion,
            condition_predicate=lambda ally_data: Agent.GetHealth(ally_data.agent_id) > 0.05 and not Agent.IsEnchanted(ally_data.agent_id),
            sort_asc_predicate=lambda ally_data: Agent.GetHealth(ally_data.agent_id),
        )
        if len(minions) == 0: return None
        return minions[0].agent_id

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        target = self._get_target()
        if target is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        target = self._get_target()
        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target)
        return result
