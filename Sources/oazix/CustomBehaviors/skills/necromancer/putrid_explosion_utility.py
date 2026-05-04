from typing import Any, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class PutridExplosionUtility(CustomSkillUtilityBase):
    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 83 if enemy_qte >= 2 else 35),
        mana_required_to_cast: int = 5,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO],
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Putrid_Explosion"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )

        self.score_definition : ScorePerAgentQuantityDefinition = score_definition

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.corpse_usage(agent_id)

    def _get_exploitable_corpses(self) -> list[tuple[int, int]]:
        corpse_enemies = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: Agent.IsExploitableCorpse(enemy_data.agent_id) and TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)),
            sort_asc_predicate=lambda enemy_data: (-enemy_data.enemy_quantity_within_range, enemy_data.distance_from_player),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id),
            is_alive=False
        )

        corpse_allies = TargetingAlly.create().get_allies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda ally_data: Agent.IsExploitableCorpse(ally_data.agent_id) and TargetingCore().is_lock_key_available(self._get_lock_key(ally_data.agent_id)),
            sort_asc_predicate=lambda ally_data: (-ally_data.enemy_quantity_within_range, ally_data.distance_from_player),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id),
            is_alive=False
        )

        corpses = corpse_enemies + corpse_allies
        return [ (corpses[0].agent_id, corpses[0].enemy_quantity_within_range) for corpse in corpses]
    
    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        corpses = self._get_exploitable_corpses()
        if len(corpses) == 0: return None
        best_corpse = corpses[0]
        return self.score_definition.get_score(best_corpse[1])

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        corpses = self._get_exploitable_corpses()
        if len(corpses) == 0: return BehaviorResult.ACTION_SKIPPED
        best_corpse = corpses[0]

        return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(self._get_lock_key(best_corpse[0]), self.custom_skill, target_agent_id=best_corpse[0]))

