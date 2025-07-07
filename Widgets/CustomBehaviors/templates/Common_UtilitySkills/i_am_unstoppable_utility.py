from tkinter.constants import N
from typing import Any, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class IAmUnstoppableUtility(CustomSkillUtilityBase):
    def __init__(self, 
    current_build: list[CustomSkill], 
    score_definition: ScoreStaticDefinition,
    mana_required_to_cast: int = 0,
    allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]):

        super().__init__(skill=CustomSkill("I_Am_Unstoppable"), in_game_build=current_build, score_definition=score_definition, mana_required_to_cast=mana_required_to_cast, allowed_states=allowed_states)
        self.score_definition: ScoreStaticDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        player_agent_id = GLOBAL_CACHE.Player.GetAgentID()
        current_heath_percent = GLOBAL_CACHE.Agent.GetHealth(player_agent_id)

        if current_heath_percent < 1: return self.score_definition.get_score()
        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result