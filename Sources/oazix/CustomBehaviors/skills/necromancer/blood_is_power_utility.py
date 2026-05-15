from typing import Any, Generator, cast, override

import PyImGui

from Py4GWCoreLib import Range, Player
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.bonds.custom_buff_target_per_profession import BuffConfigurationPerProfession
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.skills.plugins.options.raw_number_option import RawNumberOption
from Sources.oazix.CustomBehaviors.skills.plugins.targeting_modifiers.buff_configurator import BuffConfigurator

class BloodIsPowerUtility(CustomSkillUtilityBase):
    def __init__(self, 
        event_bus:EventBus,
        current_build: list[CustomSkill], 
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(33),
        sacrifice_life_limit_percent: float = 0.40,
        sacrifice_life_limit_absolute: int = 175,
        required_target_mana_lower_than_percent: float = 0.50,
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Blood_is_Power"), 
            in_game_build=current_build, 
            score_definition=score_definition, 
            mana_required_to_cast=mana_required_to_cast, 
            allowed_states=allowed_states)
        
        self.score_definition: ScoreStaticDefinition = score_definition

        self.add_plugin_targetting_modifier(lambda x: BuffConfigurator(event_bus, self.custom_skill, buff_configuration_per_profession= BuffConfigurationPerProfession.BUFF_CONFIGURATION_CASTERS))
        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "sacrifice_life_limit_percent", sacrifice_life_limit_percent))
        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "sacrifice_life_limit_absolute", sacrifice_life_limit_absolute))
        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "required_target_mana_lower_than_percent", required_target_mana_lower_than_percent))

    def _get_target(self) -> int | None:

        required_target_mana_lower_than_percent_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("required_target_mana_lower_than_percent"))
        required_target_mana_lower_than_percent = required_target_mana_lower_than_percent_option.option_value
 
        target: int | None = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast.value,
                condition=lambda agent_id:
                    agent_id != Player.GetAgentID() and
                    custom_behavior_helpers.Resources.get_energy_percent_in_party(agent_id) < required_target_mana_lower_than_percent and
                    self.get_plugin_targeting_modifiers_filtering_predicate_any()(agent_id),
                sort_key=(TargetingOrder.ENERGY_ASC, TargetingOrder.DISTANCE_ASC),
                range_to_count_enemies=None,
                range_to_count_allies=None)

        return target

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        sacrifice_life_limit_percent_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("sacrifice_life_limit_percent"))
        sacrifice_life_limit_percent = sacrifice_life_limit_percent_option.option_value

        sacrifice_life_limit_absolute_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("sacrifice_life_limit_absolute"))
        sacrifice_life_limit_absolute = sacrifice_life_limit_absolute_option.option_value

        if not custom_behavior_helpers.Resources.player_can_sacrifice_health(33, sacrifice_life_limit_percent, cast(int, sacrifice_life_limit_absolute)):
            return None

        if self._get_target() is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        target = self._get_target()
        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target)
        return result