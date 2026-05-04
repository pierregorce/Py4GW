from typing import Any, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Range, Agent
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class ShatterHexUtility(CustomSkillUtilityBase):
    def __init__(self,
                 event_bus: EventBus,
                 current_build: list[CustomSkill],
                 score_definition: ScorePerAgentQuantityDefinition = ScorePerAgentQuantityDefinition(lambda enemy_qte: 95 if enemy_qte >= 2 else 20),
                 mana_required_to_cast: int = 15,
                 allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]
                 ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Shatter_Hex"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.score_definition: ScorePerAgentQuantityDefinition = score_definition

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.hex_removal(agent_id)
    
    def _get_targets(self) -> list[TargetingAllyData]:

        allies = TargetingAlly.create().get_allies(
            within_range=Range.Spellcast.value * 1.2,
            condition_predicate=lambda ally_data: Agent.IsHexed(ally_data.agent_id) and TargetingCore().is_lock_key_available(self._get_lock_key(ally_data.agent_id)),
            sort_asc_predicate=lambda ally_data: (-ally_data.hex_priority_score, -ally_data.enemy_quantity_within_range, ally_data.hp),
            range_to_count_clustered_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
        )

        return allies

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        allies = self._get_targets()
        if len(allies) == 0: return None

        lock_key = self._get_lock_key(allies[0].agent_id)
        if CustomBehaviorParty().get_shared_lock_manager().is_lock_taken(lock_key): return None #someone is already shattering
        return self.score_definition.get_score(allies[0].enemy_quantity_within_range)

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        allies = self._get_targets()
        if len(allies) == 0: return BehaviorResult.ACTION_SKIPPED
        target = allies[0]

        lock_key = self._get_lock_key(allies[0].agent_id)
        return (yield from custom_behavior_helpers.Actions.cast_skill_to_target_with_lock(lock_key, self.custom_skill, target_agent_id=target.agent_id))