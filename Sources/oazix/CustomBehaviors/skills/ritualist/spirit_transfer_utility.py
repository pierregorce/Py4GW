from typing import Any, Generator, override

import PyImGui

from Py4GWCoreLib import Agent, Range, Player
from Py4GWCoreLib.enums_src.Model_enums import SpiritModelID
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.bus.event_message import EventMessage
from Sources.oazix.CustomBehaviors.primitives.bus.event_type import EventType
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_allegiance import TargetingAllyAllegiance
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.scores.healing_score import HealingScore
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class SpiritTransferUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(8),
        mana_required_to_cast: int = 10,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Spirit_Transfer"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
                
        self.score_definition: ScorePerHealthGravityDefinition = score_definition
        self.owned_spirits: list[SpiritModelID] = []

        self.event_bus.subscribe(EventType.SPIRIT_CREATED, self.on_spirit_created, subscriber_name=self.custom_skill.skill_name)

    def on_spirit_created(self, message: EventMessage) -> Generator[Any, Any, Any]:

        spirit_model_id: SpiritModelID = message.data
        if spirit_model_id is None: return

        if spirit_model_id not in self.owned_spirits:
            self.owned_spirits.append(spirit_model_id)
        yield

    def _get_targets(self) -> list[TargetingAllyData]:

        targets: list[TargetingAllyData] = TargetingAlly.create().get_allies(
            within_range=Range.Spellcast.value,
            condition_predicate=lambda ally_data: Agent.GetHealth(ally_data.agent_id) < 0.5,
            sort_asc_predicate=lambda ally_data: (ally_data.hp, ally_data.distance_from_player))
        return targets

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self._get_targets()
        if len(targets) == 0: return None


        spirits: list[TargetingAllyData] = TargetingAlly.create().get_allies(
            within_range=Range.Spellcast.value,
            allegiance_to_include=TargetingAllyAllegiance.Spirit,
            condition_predicate=lambda ally_data: Agent.GetModelID(ally_data.agent_id) in [int(spirit_id) for spirit_id in self.owned_spirits]
        )

        if len(spirits) == 0: return None

        return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        targets = self._get_targets()
        if len(targets) == 0: return BehaviorResult.ACTION_SKIPPED
        target = targets[0]
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)
        return result

    @override
    def customized_debug_ui(self, current_state: BehaviorState) -> None:
        PyImGui.bullet_text(f"owned_spirits :")
        for spirit in self.owned_spirits:
            PyImGui.text(f"spirit : {spirit}")