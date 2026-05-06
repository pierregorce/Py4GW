from collections.abc import Callable
from typing import Any, Generator, override

from Py4GWCoreLib import Agent, Player, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class JunundoBiteUtility(CustomSkillUtilityBase):

    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(80),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO],
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Junundu_Bite"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )

        self.score_definition: ScoreStaticDefinition = score_definition

    def _get_targets(self) -> list[TargetingEnemyData]:

        filtering_predicate: Callable[[TargetingEnemyData], bool] = lambda enemy_data: True

        if Agent.GetHealth(Player.GetAgentID()) < 0.6:
            # we limit to knockdown enemies when we are below 60% health
            filtering_predicate = lambda enemy_data: Agent.IsKnockedDown(enemy_data.agent_id)
        else:
            # any enemy is valid
            filtering_predicate = lambda enemy_data: True

        return TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast,
            condition_predicate=filtering_predicate,
            sort_asc_predicate=lambda enemy_data: enemy_data.distance_from_player,
        )

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self._get_targets()
        if targets is None: return None
        if len(targets) == 0: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        target = self._get_targets()
        if target is None: return BehaviorResult.ACTION_SKIPPED
        if len(target) == 0: return BehaviorResult.ACTION_SKIPPED

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target[0].agent_id)
        return result


