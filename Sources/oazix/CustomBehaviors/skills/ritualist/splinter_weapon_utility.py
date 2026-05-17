from typing import Any, Generator, override
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums import Profession, Range
from Py4GWCoreLib import Agent, Player, Routines
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
from Sources.oazix.CustomBehaviors.skills.plugins.targeting_modifiers.buff_configurator import BuffConfigurator
from Sources.oazix.CustomBehaviors.skills.plugins.targeting_modifiers.should_target_pets_with_weapon_spell import ShouldTargetPetsWithWeaponSpell

class SplinterWeaponUtility(CustomSkillUtilityBase):

    def __init__(self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(30),
        mana_required_to_cast: int = 10,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Splinter_Weapon"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
                
        self.score_definition: ScoreStaticDefinition = score_definition

        self.add_plugin_targetting_modifier(lambda x: BuffConfigurator(event_bus, self.custom_skill, buff_configuration_per_profession= BuffConfigurationPerProfession.BUFF_CONFIGURATION_MARTIAL))
        self.add_plugin_targetting_modifier(lambda x: ShouldTargetPetsWithWeaponSpell(self.custom_skill, False))
        self.ebon_vanguard_assassin_model_id = 5903

    def _get_target(self) -> int | None:

        # Check if we have a valid target
        targets = TargetingAlly.create().get_allies(
                within_range=Range.Spellcast.value * 1.2,
                condition_predicate=lambda ally_data:
                    ally_data.agent_id != Player.GetAgentID() and
                    self.get_plugin_targeting_modifiers_filtering_predicate_any()(ally_data.agent_id) and not Agent.IsWeaponSpelled(ally_data.agent_id),
                sort_asc_predicate=lambda ally_data: (-ally_data.distance_from_player))
        if len(targets) > 0:
            return targets[0].agent_id

        # Fallback: if all martial allies are already weapon-spelled (or none available),
        # allow splintering the Ebon Vanguard Assassin support summon.
        npc_agent_id: int = Routines.Agents.GetNearestAliveAgentByModelID(
            self.ebon_vanguard_assassin_model_id,
            Range.Spellcast.value,
        )
        if npc_agent_id is not None and npc_agent_id != 0 and not Agent.IsWeaponSpelled(npc_agent_id):
            return npc_agent_id

        return None

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        target = self._get_target()
        if target is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        target = self._get_target()
        if target is None: return BehaviorResult.ACTION_SKIPPED
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target)
        return result
