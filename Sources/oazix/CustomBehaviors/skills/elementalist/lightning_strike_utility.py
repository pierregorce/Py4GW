from typing import Any, Generator, override

from Py4GWCoreLib import Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.others import glimmer_observer
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class LightningStrikeUtility(CustomSkillUtilityBase):
    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(65),
        mana_required_to_cast: int = 5,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO],
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Lightning_Strike"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )
        self.score_definition = score_definition

    def _get_target(self) -> int | None:

        targets = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: (not glimmer_observer.had_glimmer_recently(enemy_data.agent_id) and Agent.IsConditioned(enemy_data.agent_id)),
            sort_asc_predicate=lambda enemy_data: enemy_data.distance_from_player
        )
        return targets[0].agent_id if len(targets) > 0 else None

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        target = self._get_target()
        if target is None: return None

        # ensure we have enough resources to cast
        if not custom_behavior_helpers.Resources.has_enough_resources(self.custom_skill):
            return None

        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        target = self._get_target()
        if target is None:
            return BehaviorResult.ACTION_SKIPPED

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target)
        return result