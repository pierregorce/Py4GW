from typing import Any, Generator, Callable, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class SignetOfClumsinessUtility(CustomSkillUtilityBase):
    """
    Signet of Clumsiness utility that targets attacking enemies in clusters.
    Combines interrupt + cluster targeting.
    """
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 76 if enemy_qte >= 2 else 41 if enemy_qte <= 2 else 0),
        mana_required_to_cast: int = 10,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Signet_of_Clumsiness"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
                
        self.score_definition: ScorePerAgentQuantityDefinition = score_definition

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.interrupt(agent_id)

    def _get_targets(self) -> list[TargetingEnemyData]:
        """Get attacking enemies ordered by cluster size."""
        targets = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: 
                Agent.IsAttacking(enemy_data.agent_id)
                and TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)),
            sort_asc_predicate=lambda enemy_data: -enemy_data.enemy_quantity_within_range,
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
        )
        return targets

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        
        targets = self._get_targets()
        if len(targets) == 0: return None
        return self.score_definition.get_score(targets[0].enemy_quantity_within_range)

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        enemies = self._get_targets()
        if len(enemies) == 0: return BehaviorResult.ACTION_SKIPPED
        target = enemies[0] 

        lock_key = self._get_lock_key(target.agent_id)
        return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(lock_key, self.custom_skill, target_agent_id=target.agent_id))

