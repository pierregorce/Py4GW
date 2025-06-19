from typing import List, Any, Generator, Callable, override

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_behavior_helpers import SortableAgentData, Targets
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder

class CriticalAgilityUtility(CustomSkillUtilityBase):

    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], additive_score_weight: float) -> None:
        super().__init__(skill=skill, in_game_build=current_build, score_definition=None)

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        if current_state is BehaviorState.FAR_FROM_AGGRO: return None
        return 95

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result 