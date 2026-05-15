from typing import Any, Generator, cast, override

from Py4GWCoreLib import Range, Agent, Player
from Sources.oazix.CustomBehaviors.primitives.infrastructure.persistence_locator import PersistenceLocator
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.scores.healing_score import HealingScore
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.bonds.custom_buff_multiple_target import CustomBuffMultipleTarget
from Sources.oazix.CustomBehaviors.primitives.skills.bonds.custom_buff_target_per_profession import BuffConfigurationPerProfession
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.skills.plugins.options.raw_boolean_option import RawBooleanOption
from Sources.oazix.CustomBehaviors.skills.plugins.targeting_modifiers.buff_configurator import BuffConfigurator
from Sources.oazix.CustomBehaviors.skills.plugins.targeting_modifiers.should_target_player import ShouldTargetPlayer


class ConfigurableHealUtility(CustomSkillUtilityBase):
    """Single-target heal with configurable target filtering and persistence.

    Like RawSimpleHealUtility but adds CustomBuffMultipleTarget for
    per-profession or per-email target selection, persisted via PersistenceLocator.
    """

    def __init__(
        self,
        event_bus: EventBus,
        skill: CustomSkill,
        current_build: list[CustomSkill],
        score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(5),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO],
        should_target_player: bool = True,
    ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=skill,
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )

        self.score_definition: ScorePerHealthGravityDefinition = score_definition

        self.add_plugin_targetting_modifier(lambda x: BuffConfigurator(event_bus, self.custom_skill, buff_configuration_per_profession= BuffConfigurationPerProfession.BUFF_CONFIGURATION_ALL))
        self.add_plugin_targetting_modifier(lambda x: ShouldTargetPlayer(x.custom_skill, should_target_player))

    def _get_targets(self) -> list[custom_behavior_helpers.SortableAgentData]:

        targets: list[custom_behavior_helpers.SortableAgentData] = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spellcast.value * 1.2,
            condition=lambda agent_id: (
                Agent.GetHealth(agent_id) < 0.9
                and self.get_plugin_targeting_modifiers_filtering_predicate_all()(agent_id)
            ),
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC),
        )
        return targets

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self._get_targets()
        if len(targets) == 0:
            return None

        if targets[0].hp < 0.40:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)
        if targets[0].hp < 0.85:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED)

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        targets = self._get_targets()
        if len(targets) == 0:
            return BehaviorResult.ACTION_SKIPPED
        target = targets[0]
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)
        return result