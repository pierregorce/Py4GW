from typing import Any, Generator, Callable, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.interrupt_potential_scoring import InterruptPotentialScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class CryOfPainUtility(CustomSkillUtilityBase):

    def __init__(self,
                event_bus: EventBus,
                current_build: list[CustomSkill],
                score_definition: ScoreStaticDefinition = ScoreStaticDefinition(90),
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Cry_of_Pain"),
            in_game_build=current_build,
            score_definition=score_definition)
        
        self.score_definition: ScoreStaticDefinition = score_definition

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.interrupt(agent_id)

    def detect_casting_enemies(self) -> list[TargetingEnemyData]:

        condition = lambda agent_id: Agent.IsHexed(agent_id)
        sort = lambda enemy_data: (-enemy_data.interrupt_potential_score, -enemy_data.enemy_quantity_within_range, 0 if enemy_data.is_caster else 1)

        if not self.is_another_interrupt_ready(): # it's better to interrupt even without hex-effect
            condition = lambda agent_id: True
            sort = lambda enemy_data: (-enemy_data.interrupt_potential_score, 0 if enemy_data.is_caster else 1)

        targets = TargetingEnemy\
                .create_with_custom_interrupt_potential_scoring(InterruptPotentialScoring(skills_cast_time_longer_than=0.450))\
                .get_enemies(
                    within_range=Range.Spellcast.value,
                    condition_predicate=lambda enemy_data: 
                        condition(enemy_data.agent_id) 
                        and enemy_data.interrupt_potential_score > 0 
                        and TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)),
                    sort_asc_predicate=lambda enemy_data: sort(enemy_data),
                    range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
                )
        
        return targets
    
    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self.detect_casting_enemies()
        if len(targets) == 0: return None
        return self.score_definition.get_score()
    
    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        targets = self.detect_casting_enemies()
        if len(targets) == 0: return BehaviorResult.ACTION_SKIPPED
        target_id = targets[0].agent_id

        return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(self._get_lock_key(target_id), self.custom_skill, target_agent_id=target_id))
