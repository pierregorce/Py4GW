from typing import Any, Generator, override

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, Agent, AgentArray, Range, Player
from Py4GWCoreLib.Py4GWcorelib import ThrottledTimer
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class MinionInvocationFromCorpseUtility(CustomSkillUtilityBase):

    def __init__(self,
    event_bus: EventBus,
    skill: CustomSkill,
    current_build: list[CustomSkill],
    score_definition: ScoreStaticDefinition = ScoreStaticDefinition(65),
    mana_required_to_cast: int = 5,
    allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]
    ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=skill,
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.score_definition: ScoreStaticDefinition = score_definition
        self.far_from_aggro_timer = ThrottledTimer(5_000)  # 5s max window for FAR_FROM_AGGRO
        self._previous_state: BehaviorState | None = None

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.corpse_usage(agent_id)
    
    def _get_exploitable_corpses(self) -> list[int]:
        corpse_enemies = TargetingEnemy.create().get_enemies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda enemy_data: Agent.IsExploitableCorpse(enemy_data.agent_id) and TargetingCore().is_lock_key_available(self._get_lock_key(enemy_data.agent_id)),
            sort_asc_predicate=lambda enemy_data: (enemy_data.distance_from_player),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id),
            is_alive=False
        )

        corpse_allies = TargetingAlly.create().get_allies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda ally_data: Agent.IsExploitableCorpse(ally_data.agent_id) and TargetingCore().is_lock_key_available(self._get_lock_key(ally_data.agent_id)),
            sort_asc_predicate=lambda ally_data: (ally_data.distance_from_player),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id),
            is_alive=False
        )

        corpses = corpse_enemies + corpse_allies
        return [corpse.agent_id for corpse in corpses]

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        # Track state transitions - reset timer when entering FAR_FROM_AGGRO
        if self._previous_state != current_state:
            if current_state == BehaviorState.FAR_FROM_AGGRO:
                self.far_from_aggro_timer.Reset()
            self._previous_state = current_state

        # In FAR_FROM_AGGRO, only allow for 5s max
        if current_state == BehaviorState.FAR_FROM_AGGRO:
            if self.far_from_aggro_timer.IsExpired():
                return None

        targets = self._get_exploitable_corpses()
        if len(targets) == 0: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        targets = self._get_exploitable_corpses()
        if len(targets) == 0: return BehaviorResult.ACTION_SKIPPED
        target = targets[0]
        return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(self._get_lock_key(target), self.custom_skill, target_agent_id=target))
    
    @override
    def customized_debug_ui(self, current_state):
            PyImGui.bullet_text(f"timer : {self.far_from_aggro_timer.GetTimeRemaining()}")
            PyImGui.bullet_text(f"is in timeout : {self.far_from_aggro_timer.IsExpired()}")
