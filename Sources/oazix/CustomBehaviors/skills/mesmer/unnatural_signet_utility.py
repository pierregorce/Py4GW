from typing import List, Any, Generator, Callable, cast, override

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class UnnaturalSignetUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 70 if enemy_qte >= 3 else 40 if enemy_qte <= 2 else 0),
        score_without_aoe_effect_definition: ScoreStaticDefinition | None = None,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Unnatural_Signet"),
            in_game_build=current_build,
            score_definition=score_definition,
            allowed_states=allowed_states)

        self.score_definition: ScorePerAgentQuantityDefinition = score_definition
        self.score_without_aoe_effect_definition: ScoreStaticDefinition | None = score_without_aoe_effect_definition

    def _get_targets(self) -> list[TargetingEnemyData]:
        targets = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: Agent.IsHexed(enemy_data.agent_id) or Agent.IsEnchanted(enemy_data.agent_id),
            sort_asc_predicate=lambda enemy_data: (-enemy_data.enemy_quantity_within_range, -enemy_data.hp),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
        )

        return targets
    
    def _get_targets_without_aoe_effect(self) -> list[TargetingEnemyData]:
        targets = TargetingEnemy.create().get_enemies(
                within_range=Range.Spellcast.value,
                sort_asc_predicate=lambda enemy_data: (-enemy_data.enemy_quantity_within_range, -enemy_data.hp),
                range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
            )
        return targets

        


    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self._get_targets()

        if len(targets) > 0:
            return self.score_definition.get_score(targets[0].enemy_quantity_within_range)

        if len(targets) == 0: 
            if self.score_without_aoe_effect_definition is None: return None
            targets = self._get_targets_without_aoe_effect()
            if len(targets) == 0: return None
            return self.score_without_aoe_effect_definition.get_score()
        
        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        enemies = self._get_targets()
        if len(enemies) == 0: return BehaviorResult.ACTION_SKIPPED
        target = enemies[0]
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)
        return result