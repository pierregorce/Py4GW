from typing import Any, Generator, override


from Py4GWCoreLib import Range, Player
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally import TargetingAlly
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.bonds.custom_buff_target_per_profession import BuffConfigurationPerProfession
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.skills.plugins.watchdogs.should_lock_until_buff_completion import ShouldLockUntilBuffCompletion
from Sources.oazix.CustomBehaviors.skills.plugins.preconditions.should_wait_for_heroic_refrain import ShouldWaitForHeroicRefrain
from Sources.oazix.CustomBehaviors.skills.plugins.targeting_modifiers.buff_configurator import BuffConfigurator


class StrengthOfHonorUtility(CustomSkillUtilityBase):
    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(20),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Strength_of_Honor"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
                
        self.score_definition: ScoreStaticDefinition = score_definition

        self.add_plugin_targetting_modifier(lambda x: BuffConfigurator(event_bus, self.custom_skill, buff_configuration_per_profession= BuffConfigurationPerProfession.BUFF_CONFIGURATION_MARTIAL))
        self.add_plugin_precondition(lambda x: ShouldWaitForHeroicRefrain(x.custom_skill, default_value= False))
        self.add_plugin_watchdog(lambda x: ShouldLockUntilBuffCompletion(x.custom_skill, is_buff_config_fulfilled= lambda: self._get_target() is None, default_value= True))

    def _get_target(self) -> int | None:
        targets = TargetingAlly.create().get_allies(
                within_range=Range.Spellcast.value * 1.2,
                condition_predicate=lambda ally_data: self.get_plugin_targeting_modifiers_filtering_predicate_any()(ally_data.agent_id),
                sort_asc_predicate=lambda ally_data: ally_data.distance_from_player)

        return targets[0].agent_id if len(targets) > 0 else None

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        target = self._get_target()
        if target is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        target = self._get_target()
        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target)
        return result 
