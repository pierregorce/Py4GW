from typing import Any, Generator, override, Tuple

from Py4GWCoreLib import GLOBAL_CACHE, Range, Agent, Player
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_boosted_definition import ScoreBoostedDefinition
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_energy_definition import ScorePerEnergyDefinition
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class SignetOfLostSoulsUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerEnergyDefinition = ScorePerEnergyDefinition(score_nominal=33, score_boosted=83, only_cast_if_energy_below=0.85, low_mana_threshold=0.30),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO],
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Signet_of_Lost_Souls"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.score_definition: ScorePerEnergyDefinition = score_definition

    @staticmethod
    def _get_target() -> int | None:
        targets: list[TargetingEnemyData] = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: enemy_data.hp < 0.5,
            sort_asc_predicate=lambda enemy_data: (enemy_data.distance_from_player, enemy_data.hp)
        )
        if len(targets) == 0: return None

        return targets[0].agent_id

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        target = self._get_target()

        if not target: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        target = self._get_target()
        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target)
        return result
