from typing import Any, Generator, override, List

from Py4GWCoreLib import GLOBAL_CACHE, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.others import glimmer_observer
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.skills.generic.raw_aoe_attack_utility import RawAoeAttackUtility


class ChainLightningUtility(RawAoeAttackUtility):
    def __init__(self,
                 event_bus: EventBus,
                 current_build: list[CustomSkill],
                 score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 55 if enemy_qte >= 2 else 51),
                 mana_required_to_cast: int = 10,
                 allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
                 ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Chain_Lightning"),
            current_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.score_definition: ScorePerAgentQuantityDefinition = score_definition

    def _get_all_targets(self) -> List[TargetingEnemyData]:
        # avoid targeting already-hexed foes (would remove hex) — also ignore agents that currently have Glimmering_Mark
        return TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: (not glimmer_observer.had_glimmer_recently(enemy_data.agent_id)),
            sort_asc_predicate=lambda enemy_data: (-enemy_data.enemy_quantity_within_range, -enemy_data.hp),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
        )

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        # ignore if player energy below 60%
        try:
            current_energy = custom_behavior_helpers.Resources.get_player_absolute_energy()
            if current_energy is not None and current_energy < 60:
                return None
        except Exception:
            # if energy check fails, be conservative and skip
            return None

        targets = self._get_all_targets()
        if len(targets) == 0:
            return None

        return self.score_definition.get_score(len(targets))

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        enemies = self._get_all_targets()
        if len(enemies) == 0:
            return BehaviorResult.ACTION_SKIPPED

        target = enemies[0]
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)
        return result
