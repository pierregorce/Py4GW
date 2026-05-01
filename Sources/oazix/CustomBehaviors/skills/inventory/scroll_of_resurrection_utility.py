from typing import Any, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Range, Player
from Py4GWCoreLib.enums import ModelID
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.primitives.skills.utility_skill_typology import UtilitySkillTypology

class ScrollOfResurrectionUtility(CustomSkillUtilityBase):
    """Utility skill that uses Scroll of Resurrection when 2+ allies are dead and scroll is in inventory."""
    
    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(0),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.FAR_FROM_AGGRO, BehaviorState.CLOSE_TO_AGGRO]
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Scroll_Of_Resurrection"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
            utility_skill_typology=UtilitySkillTypology.INVENTORY,
        )
        
        self.score_definition: ScorePerAgentQuantityDefinition = score_definition
        self.min_dead_allies_required = 2
        self.scroll_of_resurrection_model_id = ModelID.Scroll_Of_Resurrection.value  # 26501

    def _has_scroll_in_inventory(self) -> bool:
        """Check if Scroll of Resurrection is available in inventory."""
        return GLOBAL_CACHE.Inventory.GetModelCount(self.scroll_of_resurrection_model_id) > 0

    def _get_dead_allies(self) -> list[custom_behavior_helpers.SortableAgentData]:
        """Get count of dead allies within range."""
        player_agent_id = Player.GetAgentID()
        
        dead_allies = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Earshot.value,
            condition=lambda agent_id: agent_id != player_agent_id,
            is_alive=False,
            sort_key=(TargetingOrder.DISTANCE_ASC,)
        )
        return dead_allies

    def _use_scroll(self) -> bool:
        """Use the Scroll of Resurrection from inventory."""
        item_id = GLOBAL_CACHE.Item.GetItemIdFromModelID(self.scroll_of_resurrection_model_id)
        if item_id:
            GLOBAL_CACHE.Inventory.UseItem(item_id)
            return True
        return False

    def _get_lock_keys(self, agent_ids: list[int]) -> list[str]:
        return [LockKeyHelper.resurrection(agent_id) for agent_id in agent_ids]

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        
        if not self._has_scroll_in_inventory(): 
            return None

        dead_allies = self._get_dead_allies()
        if len(dead_allies) < self.min_dead_allies_required: 
            return None
        
        lock_keys = self._get_lock_keys([ally.agent_id for ally in dead_allies])
        if CustomBehaviorParty().get_shared_lock_manager().count_available_locks(lock_keys) < self.min_dead_allies_required:
            return None
        
        return self.score_definition.get_score(len(dead_allies))

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        """Execute scroll usage."""
        
        if not self._has_scroll_in_inventory(): return BehaviorResult.ACTION_SKIPPED
        dead_allies = self._get_dead_allies()
        if len(dead_allies) < self.min_dead_allies_required: return BehaviorResult.ACTION_SKIPPED
        
        lock_keys = self._get_lock_keys([ally.agent_id for ally in dead_allies])
        acquired_locks = CustomBehaviorParty().get_shared_lock_manager().try_aquire_locks(lock_keys, min_locks_to_acquire=self.min_dead_allies_required)
        if acquired_locks is None: return BehaviorResult.ACTION_SKIPPED
        
        try:
            if self._use_scroll():
                yield
                return BehaviorResult.ACTION_PERFORMED
            else:
                return BehaviorResult.ACTION_SKIPPED
        finally:
            CustomBehaviorParty().get_shared_lock_manager().release_locks(acquired_locks)
