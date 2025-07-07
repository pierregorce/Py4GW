from typing import Any, Generator, override, Optional, Callable

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Py4GWCoreLib.enums import SpiritModelID
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class SignetOfSpiritsUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition) -> None:
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.score_definition: ScoreStaticDefinition = score_definition
        self._hate_spirit = SpiritModelID.HATE
        self._suffering_spirit = SpiritModelID.SUFFERING
        self._anger_spirit = SpiritModelID.ANGER
        self.owned_spirit_model_ids: list[SpiritModelID] = [self._hate_spirit, self._suffering_spirit, self._anger_spirit]

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
       
        # we only recast if one of the 3 spirits is dead

        spirits: list[custom_behavior_helpers.SpiritAgentData] = custom_behavior_helpers.Targets.get_all_spirits_raw(
            within_range=Range.Spirit,
            spirit_model_ids=self.owned_spirit_model_ids,
            condition=lambda agent_id: True
        )

        if len(spirits) >= 3: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result