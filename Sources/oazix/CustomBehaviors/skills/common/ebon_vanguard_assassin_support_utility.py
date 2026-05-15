from enum import Enum
from typing import List, Any, Generator, Callable, cast, override

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.infrastructure.persistence_locator import PersistenceLocator
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.skills.plugins.options.raw_boolean_option import RawBooleanOption

class EbonVanguardAssassinSupportUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(40),
        mana_required_to_cast: int = 20,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO],
        is_spike_mode_activated : bool = True
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Ebon_Vanguard_Assassin_Support"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.score_definition: ScoreStaticDefinition = score_definition
        self.add_plugin_option(lambda x: RawBooleanOption(x.custom_skill, "is_spike_mode_activated", is_spike_mode_activated))

    def _get_targets(self) -> list[custom_behavior_helpers.SortableAgentData]:
        return custom_behavior_helpers.Targets.get_all_possible_enemies_ordered_by_priority_raw(
            within_range=Range.Spellcast,
            sort_key=(TargetingOrder.AGENT_QUANTITY_WITHIN_RANGE_ASC, TargetingOrder.DISTANCE_ASC),
            range_to_count_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id),
            condition=lambda agent_id: Agent.GetHealth(agent_id) > 0.2)
    
    def _get_lock_key(self, agent_id: int) -> str:
        return f"EbonVanguardAssassinSupport_{agent_id}"

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        targets = self._get_targets()
        if len(targets) == 0: return None

        # Only check lock in CHAINED mode
        is_spike_mode_activated_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("is_spike_mode_activated"))
        is_spike_mode_activated = is_spike_mode_activated_option.option_value

        if not is_spike_mode_activated:
            lock_key = self._get_lock_key(targets[0].agent_id)
            if CustomBehaviorParty().get_shared_lock_manager().is_lock_taken(lock_key):
                return None  # someone is already doing that, we want to delay a bit when lock is available to chain interruptions

        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        enemies = self._get_targets()
        if len(enemies) == 0: return BehaviorResult.ACTION_SKIPPED
        target = enemies[0]

        # Only use lock in CHAINED mode
        is_spike_mode_activated_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("is_spike_mode_activated"))
        is_spike_mode_activated = is_spike_mode_activated_option.option_value

        if not is_spike_mode_activated:
            lock_key = self._get_lock_key(target.agent_id)
            if CustomBehaviorParty().get_shared_lock_manager().try_aquire_lock(lock_key, timeout_seconds=3) == False:
                yield
                return BehaviorResult.ACTION_SKIPPED

            try:
                result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)
            finally:
                # we explicitly don't release the lock, and keep it for 3 seconds so the skill will be chain-casted
                pass
        else:
            # SPIKE mode: no lock, just cast
            result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)

        return result