from typing import Any, Generator, Callable, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Player, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.interrupt_potential_scoring import InterruptPotentialScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.tarteging_enemy_allegiance import TargetingEnemyAllegiance
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class PsychicInstabilityUtility(CustomSkillUtilityBase):

    def __init__(self,
                event_bus: EventBus,
                current_build: list[CustomSkill],
                score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 95 if enemy_qte >= 2 else 20),
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Psychic_Instability"),
            in_game_build=current_build,
            score_definition=score_definition)
        
        self.score_definition: ScorePerAgentQuantityDefinition = score_definition

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.interrupt(agent_id)

    def detect_casting_enemies(self) -> list[TargetingEnemyData]:
        targets = TargetingEnemy\
            .create_with_custom_interrupt_potential_scoring(InterruptPotentialScoring(skills_cast_time_longer_than=1.00))\
            .get_enemies(
                within_range=Range.Spellcast.value,
                allegiance_to_include=TargetingEnemyAllegiance.Enemy,
                condition_predicate=lambda enemy_data: TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)), # only skills that are longer than 1s. too much changes to fail otherwise
                sort_asc_predicate=lambda enemy_data: (-enemy_data.enemy_quantity_within_range, 0 if enemy_data.is_caster else 1),
                range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
            )
        return targets

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self.detect_casting_enemies()
        if len(targets) == 0: return None
        return self.score_definition.get_score(targets[0].enemy_quantity_within_range)
    
    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        targets = self.detect_casting_enemies()
        if len(targets) == 0: return BehaviorResult.ACTION_SKIPPED
        target_id = targets[0].agent_id

        # https://wiki.guildwars.com/wiki/Game_updates:2023
        # The odds that the skill will perform the interrupt are higher the longer you have targeted the player before executing the skill, up to approximately ¼ second (depending on latency). 
        # The reasoning behind this change is to make these skills more strategic in nature and, not coincidentally, more difficult for bots to execute. 

        lock_manager = CustomBehaviorParty().get_shared_lock_manager()
        lock_key = self._get_lock_key(target_id)
        
        try:
            if not lock_manager.try_aquire_lock(lock_key): return BehaviorResult.ACTION_SKIPPED
            Player.ChangeTarget(target_id)
            yield from custom_behavior_helpers.Helpers.wait_for(180)
            
            if not Agent.IsCasting(target_id): return BehaviorResult.ACTION_SKIPPED
            Player.ChangeTarget(target_id)
            result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
            # result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target_id)
        finally:
            lock_manager.release_lock(lock_key)
        
        return result