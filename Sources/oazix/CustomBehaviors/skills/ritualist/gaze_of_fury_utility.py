from typing import Any, Generator, override

from Py4GWCoreLib import Routines, Range, Agent
from Py4GWCoreLib.enums import SpiritModelID
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_allegiance import TargetingAllyAllegiance
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class GazeOfFuryUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(75),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Gaze_of_Fury"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
                
        self.score_definition: ScoreStaticDefinition = score_definition

        self.owned_spirit_model_id: SpiritModelID = SpiritModelID.FURY

        # todo propose to be customizable
        self.vampirism_skill: CustomSkill = CustomSkill("Vampirism")
        self.vampirism_spirit_model_id: SpiritModelID = SpiritModelID.VAMPIRISM

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        if not Routines.Checks.Skills.IsSkillIDReady(self.vampirism_skill.skill_id): return None # if vampirism not-ready, we can't cast
        
        gaze_of_fury_spirits = TargetingAlly.create().get_allies(
            within_range=Range.Spirit.value,
            allegiance_to_include=TargetingAllyAllegiance.Spirit,
            condition_predicate=lambda ally_data: Agent.GetModelID(ally_data.agent_id) == int(self.owned_spirit_model_id))
        if len(gaze_of_fury_spirits) > 0: return None # no cast, if gaze of fury spirit exist

        vampirism_spirits = TargetingAlly.create().get_allies(
            within_range=Range.Spirit.value,
            allegiance_to_include=TargetingAllyAllegiance.Spirit,
            condition_predicate=lambda ally_data: Agent.GetModelID(ally_data.agent_id) == int(self.vampirism_spirit_model_id))
        if len(vampirism_spirits) == 0: return None # no cast, if vampirism spirit not exist

        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        # we target vampirism spirit to destroy it

        vampirism_spirits: list[TargetingAllyData] = TargetingAlly.create().get_allies(
            within_range=Range.Spirit.value,
            allegiance_to_include=TargetingAllyAllegiance.Spirit,
            condition_predicate=lambda ally_data: Agent.GetModelID(ally_data.agent_id) == int(self.vampirism_spirit_model_id))
        if len(vampirism_spirits) == 0: return BehaviorResult.ACTION_SKIPPED

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=vampirism_spirits[0].agent_id)
        return result