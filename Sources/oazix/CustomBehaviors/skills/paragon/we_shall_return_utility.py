from typing import Any, Generator, override

from Py4GWCoreLib import Agent, Player, Range, Routines
from Py4GWCoreLib.Py4GWcorelib import Utils
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.lock_key_helper import LockKeyHelper
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.healing_score import HealingScore
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class WeShallReturnUtility(CustomSkillUtilityBase):
    """'We Shall Return!' — paragon shout that resurrects all dead party members in earshot.

    Moves into earshot range of dead allies before casting. Uses shared lock
    to prevent multiple characters from moving to rez simultaneously.
    Follows the UnyieldingAuraDropUtility movement pattern.
    """

    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(0),
        mana_required_to_cast: int = 25,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO],
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("We_Shall_Return"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )
        self.score_definition: ScorePerHealthGravityDefinition = score_definition
        self._blocked_targets: dict[int, float] = {}  # agent_id → expiry time
        self._BLOCK_DURATION: float = 3.0  # seconds to skip a target after failed movement — short to allow retries during wipes

    def _get_lock_key(self, agent_id: int) -> str:
        return LockKeyHelper.resurrection(agent_id)

    def _get_dead_allies(self) -> list[custom_behavior_helpers.SortableAgentData]:
        import time as _time
        now = _time.time()
        # Expire old blocks
        self._blocked_targets = {k: v for k, v in self._blocked_targets.items() if v > now}
        return custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spellcast.value * 1.5,
            sort_key=(TargetingOrder.DISTANCE_ASC,),
            is_alive=False,
            condition=lambda aid: aid not in self._blocked_targets,
        )

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        dead = self._get_dead_allies()
        if not dead:
            return None
        return self.score_definition.get_score(HealingScore.RESURRECTION)

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        import time as _time

        dead = self._get_dead_allies()
        if not dead:
            return BehaviorResult.ACTION_SKIPPED

        dead_agent_id = dead[0].agent_id # we should take a lock on all dead allies. todo to improve
        lock_key = self._get_lock_key(dead_agent_id)
        if not CustomBehaviorParty().get_shared_lock_manager().try_aquire_lock(lock_key):
            return BehaviorResult.ACTION_SKIPPED

        try:
            earshot_threshold = Range.Earshot.value * 0.9
            dead_pos = Agent.GetXY(dead_agent_id)
            player_pos = Agent.GetXY(Player.GetAgentID())

            # Move into earshot if needed — move directly to corpse, let game pathfinding handle terrain
            if Utils.Distance(player_pos, dead_pos) > earshot_threshold:
                Player.Move(dead_pos[0], dead_pos[1])
                deadline = _time.time() + 3.0
                while _time.time() < deadline:
                    cur_pos = Agent.GetXY(Player.GetAgentID())
                    if Utils.Distance(cur_pos, dead_pos) <= earshot_threshold:
                        break
                    yield

            # Verify we're actually in range before casting
            cur_pos = Agent.GetXY(Player.GetAgentID())
            if Utils.Distance(cur_pos, dead_pos) > earshot_threshold:
                self._blocked_targets[dead_agent_id] = _time.time() + self._BLOCK_DURATION
                return BehaviorResult.ACTION_SKIPPED

            # Cast the shout (no target needed — affects all dead in earshot)
            result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
            return result
        finally:
            CustomBehaviorParty().get_shared_lock_manager().release_lock(lock_key)
