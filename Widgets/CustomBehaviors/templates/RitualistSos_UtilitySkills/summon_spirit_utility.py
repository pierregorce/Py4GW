from typing import Any, Generator, override, Optional, Callable

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Py4GWCoreLib.enums import SpiritModelID
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class SummonSpiritUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition, owned_spirits: list[SpiritModelID]) -> None:
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO])
        self.score_definition: ScoreStaticDefinition = score_definition
        self.owned_spirits: list[SpiritModelID] = owned_spirits

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
       
       # we check life & distance of owned spirits

       spirits: list[custom_behavior_helpers.SpiritAgentData] = custom_behavior_helpers.Targets.get_all_spirits_raw(
        within_range=Range.Compass,
        spirit_model_ids=self.owned_spirits,
        condition=lambda agent_id: True
       )

       # if distance > Spirit, we summon spirit
       if current_state is BehaviorState.FAR_FROM_AGGRO:
            for spirit in spirits:
                if spirit.distance_from_player > Range.Compass.value * 0.75:
                    return self.score_definition.get_score()

       if current_state is BehaviorState.CLOSE_TO_AGGRO or current_state is BehaviorState.IN_AGGRO:
            for spirit in spirits:
                if spirit.distance_from_player > Range.Area.value:
                    return self.score_definition.get_score()

       # if any spirit has life lower than < 0.5, we summon spirit
       for spirit in spirits:
        if spirit.hp < 0.5:
            return self.score_definition.get_score()

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result