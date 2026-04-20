from re import S
from typing import Any, Callable, Generator, override
import random

from Py4GWCoreLib import Player
from Py4GWCoreLib.enums_src.GameData_enums import SkillType
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class SignetOfAggressionUtility(CustomSkillUtilityBase):
    def __init__(
            self,
            event_bus: EventBus,
            current_build: list[CustomSkill],
            skill: CustomSkill = CustomSkill("Signet_of_Aggression"),
            score_definition: ScoreStaticDefinition = ScoreStaticDefinition(20),
            allowed_states: list[BehaviorState] = [BehaviorState.CLOSE_TO_AGGRO, BehaviorState.IN_AGGRO]
            ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=skill,
            in_game_build=current_build,
            score_definition=score_definition,
            allowed_states=allowed_states)
        
        self.score_definition: ScoreStaticDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        has_buff =  custom_behavior_helpers.Resources.is_ally_under_specific_effect_types(Player.GetAgentID(), [SkillType.Shout, SkillType.Chant])
        if has_buff: return self.score_definition.get_score()
        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        # todo only get power if needed
        result:BehaviorResult = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result
