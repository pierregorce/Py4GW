from typing import Any, Generator, override, Optional, Callable

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Py4GWCoreLib.enums import SpiritModelID
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class GazeOfFuryUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition) -> None:
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.score_definition: ScoreStaticDefinition = score_definition

        self.owned_spirit_model_id: SpiritModelID = SpiritModelID.FURY

        self.vampirism_skill: CustomSkill = CustomSkill("Vampirism")
        self.vampirism_spirit_model_id: SpiritModelID = SpiritModelID.VAMPIRISM

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
       
        if not Routines.Checks.Skills.IsSkillIDReady(self.vampirism_skill.skill_id): return None # if vampirism not-ready, we can't cast
        
        is_gaze_of_fury_spirit_exist = custom_behavior_helpers.Targets.get_first_or_default_from_spirits_raw(within_range=Range.Spirit, spirit_model_ids=[self.owned_spirit_model_id], condition=lambda agent_id: True)
        if is_gaze_of_fury_spirit_exist: return None # no cast, if gaze of fury spirit exist

        is_vampirism_spirit_exist = custom_behavior_helpers.Targets.get_first_or_default_from_spirits_raw(within_range=Range.Spirit, spirit_model_ids=[self.vampirism_spirit_model_id], condition=lambda agent_id: True)
        if not is_vampirism_spirit_exist: return None # no cast, if vampirism spirit not exist

        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        # we target vampirism spirit to destroy it

        vampirism_spirit: custom_behavior_helpers.SpiritAgentData | None = custom_behavior_helpers.Targets.get_first_or_default_from_spirits_raw(within_range=Range.Spirit, spirit_model_ids=[self.vampirism_spirit_model_id], condition=lambda agent_id: True)
        if vampirism_spirit is None: return BehaviorResult.ACTION_SKIPPED

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=vampirism_spirit.agent_id)
        return result