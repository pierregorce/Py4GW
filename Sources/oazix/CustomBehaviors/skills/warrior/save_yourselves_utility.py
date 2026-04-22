from collections.abc import Callable
from typing import Any, Generator, override


from Py4GWCoreLib import Agent, Player, Routines
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class SaveYourselvesUtility(CustomSkillUtilityBase):

    LOCK_KEY = f"SaveYourselves"

    def __init__(self,
        event_bus: EventBus,
        skill: CustomSkill,
        current_build: list[CustomSkill],
        allies_health_less_than_percent: float = 0.90,
        allies_quantity_required: int = 2,
        emergency_health_percent: float = 0.45,
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(90),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=skill,
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)

        self.score_definition: ScoreStaticDefinition = score_definition
        self.allies_health_less_than_percent: float = allies_health_less_than_percent
        self.allies_quantity_required: int = allies_quantity_required
        self.emergency_health_percent: float = emergency_health_percent
        self.save_yourselves_duration_in_seconds: int = 6

    def _get_lock_key(self) -> str:
        return f"{SaveYourselvesUtility.LOCK_KEY}"
    
    def _get_allies(self) -> list[custom_behavior_helpers.SortableAgentData]:
        return custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Earshot.value,
            condition=lambda agent_id: agent_id != Player.GetAgentID(),
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC)
        )

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        
        if CustomBehaviorParty().get_shared_lock_manager().is_lock_taken(self._get_lock_key()): return None

        allies = self._get_allies()
        if len(allies) == 0: return None

        hurt_allies = [ally for ally in allies if ally.hp < self.allies_health_less_than_percent]
        if len(hurt_allies) >= self.allies_quantity_required: return self.score_definition.get_score()

        emergency_allies = [ally for ally in allies if ally.hp < self.emergency_health_percent]
        if len(emergency_allies) >= 1: return self.score_definition.get_score()

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        lock_key = self._get_lock_key()
        if CustomBehaviorParty().get_shared_lock_manager().try_aquire_lock(lock_key, timeout_seconds=self.save_yourselves_duration_in_seconds) == False:
            yield
            return BehaviorResult.ACTION_SKIPPED
        
        # nudge toward optimal ally coverage before casting
        agent_ids = [ally.agent_id for ally in self._get_allies()]

        gravity_center = custom_behavior_helpers.Targets.find_optimal_gravity_center(Range.Earshot, agent_ids=agent_ids)
        if gravity_center is not None and gravity_center.distance_from_player > 50:
            exit_condition: Callable[[], bool] = lambda: False
            yield from Routines.Yield.Movement.FollowPath(
                path_points=[gravity_center.coordinates],
                custom_exit_condition=exit_condition,
                tolerance=30,
                log=False,
                timeout=2000,
            )
            
        # we take a lock for the duration of the skill, it's simplest way to ensure we don't overlap save yourselfs
        
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)

        # we do not release the lock, it will be released automatically at the end of the duration
        
        return result