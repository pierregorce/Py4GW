from typing import Any, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.interrupt_potential_scoring import InterruptPotentialScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.tarteging_enemy_allegiance import TargetingEnemyAllegiance
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class OverloadUtility(CustomSkillUtilityBase):

    def __init__(self,
                event_bus: EventBus,
                current_build: list[CustomSkill],
                interrupt_score_definition: ScoreStaticDefinition = ScoreStaticDefinition(88),
                hex_spread_score_definition: ScoreStaticDefinition | None = ScoreStaticDefinition(55),
                mana_required_to_cast: int = 5,
                allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO],
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Overload"),
            in_game_build=current_build,
            score_definition=interrupt_score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.interrupt_score_definition: ScoreStaticDefinition = interrupt_score_definition
        self.hex_spread_score_definition: ScoreStaticDefinition | None = hex_spread_score_definition

    def _get_lock_key(self, agent_id: int) -> str:
        return f"Overload_{agent_id}"

    def _get_casting_enemies(self) -> list[TargetingEnemyData]:
        targets = TargetingEnemy\
            .create_with_custom_interrupt_potential_scoring(InterruptPotentialScoring(skills_cast_time_longer_than=0.250))\
            .get_enemies(
                within_range=Range.Spellcast.value,
                allegiance_to_include=TargetingEnemyAllegiance.Enemy,
                condition_predicate=lambda enemy_data: enemy_data.interrupt_potential_score > 0 and TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)),
                sort_asc_predicate=lambda enemy_data: (-enemy_data.interrupt_potential_score, -enemy_data.enemy_quantity_within_range, 0 if enemy_data.is_caster else 1),
                range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
            )
        return targets

    def get_hex_spread_targets(self) -> list[TargetingEnemyData]:
        targets = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            allegiance_to_include=TargetingEnemyAllegiance.Enemy | TargetingEnemyAllegiance.Minion | TargetingEnemyAllegiance.Pet,
            condition_predicate=lambda enemy_data: not Agent.IsHexed(enemy_data.agent_id) and TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)),
            sort_asc_predicate=lambda enemy_data: (-enemy_data.enemy_quantity_within_range, -enemy_data.hp),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
        )
        return targets

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        casting_targets = self._get_casting_enemies()
        if len(casting_targets) > 0: return self.interrupt_score_definition.get_score()

        if self.hex_spread_score_definition is None: return None
        hex_targets = self.get_hex_spread_targets()
        if len(hex_targets) > 0: return self.hex_spread_score_definition.get_score()

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        casting_targets = self._get_casting_enemies()
        if len(casting_targets) > 0:
            casting_target = casting_targets[0]
            return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(self._get_lock_key(casting_target.agent_id), self.custom_skill, target_agent_id=casting_target.agent_id))
        
        if self.hex_spread_score_definition is not None:
            hex_targets = self.get_hex_spread_targets()
            if len(hex_targets) > 0:
                hex_target = hex_targets[0]
                return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(self._get_lock_key(hex_target.agent_id), self.custom_skill, target_agent_id=hex_target.agent_id))

        return BehaviorResult.ACTION_SKIPPED
