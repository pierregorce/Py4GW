from typing import Any, Generator, cast, override

import PyImGui

from Py4GWCoreLib import Agent, Player, Range, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.skills.plugins.options.raw_number_option import RawNumberOption


class EtherRenewalRecoveryUtility(CustomSkillUtilityBase):
    """Energy crisis manager for Ether Renewal builds.

    Activates when energy drops below ``recovery_enter`` (hysteresis: deactivates
    above ``recovery_exit``).  Scores 79 — above all healing skills (max 78) but
    below ER (81) and Aura (80) maintenance.

    During recovery:
    - If ER is down and recastable: ACTION_SKIPPED (budget shield — score 79
      blocks heals from spending energy that ER needs).
    - Otherwise: casts the cheapest ready spell on any ally in range to trigger
      ER energy/health generation.

    Replaces both ``EmoSpamOnPartyIfManaLowUtility`` (score 12, never won) and
    ``DismissBuffIfNoManaUtility`` (panic strip — now handled by the
    ``EnergyAwareBondShedding`` watchdog).
    """

    def __init__(
        self,
        event_bus: EventBus,
        spam_skills: list[CustomSkillUtilityBase],
        er_skill: CustomSkill,
        current_build: list[CustomSkill],
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(79),
        recovery_enter: float = 0.20,
        recovery_exit: float = 0.60,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Ether_Renewal_Recovery"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=0,
            allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO],
        )

        self.score_definition: ScoreStaticDefinition = score_definition
        self.spam_skills: list[CustomSkillUtilityBase] = spam_skills
        self.er_skill: CustomSkill = er_skill
        self._recovery_active: bool = False
   
        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "recovery_enter", recovery_enter))
        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "recovery_exit", recovery_exit))

    @override
    def are_common_pre_checks_valid(self, current_state: BehaviorState) -> bool:
        # Virtual skill — no slot, no energy cost. Only gate on state.
        if current_state is BehaviorState.IDLE:
            return False
        if self.allowed_states is not None and current_state not in self.allowed_states:
            return False
        return True

    def _is_er_active(self) -> bool:
        return Routines.Checks.Effects.HasBuff(Player.GetAgentID(), self.er_skill.skill_id)

    def _is_er_ready(self) -> bool:
        if self.er_skill.skill_slot == 0:
            return False
        return Routines.Checks.Skills.IsSkillSlotReady(self.er_skill.skill_slot)

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        energy = Agent.GetEnergy(Player.GetAgentID())
        recovery_enter: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("recovery_enter"))
        recovery_exit: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("recovery_exit"))

        if self._recovery_active:
            if energy >= recovery_exit.option_value:
                self._recovery_active = False
                return None
            # ER is down and castable: outscore AoR (80) so it doesn't waste the
            # action slot; _execute returns ACTION_SKIPPED and pips accumulate for ER (81).
            if not self._is_er_active() and self._is_er_ready():
                return 80.5
            return self.score_definition.get_score()
        else:
            if energy <= recovery_enter.option_value:
                self._recovery_active = True
                return self.score_definition.get_score()
            return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        # If ER is down and recastable, don't spend energy — save for ER (score 81).
        # Score 79 still blocks all heals, so pips accumulate undisturbed.
        if not self._is_er_active() and self._is_er_ready():
            return BehaviorResult.ACTION_SKIPPED

        # Cast cheapest ready spell on any ally in range (triggers ER)
        player_id = Player.GetAgentID()
        for skill_utility in self.spam_skills:
            if skill_utility.custom_skill.skill_slot == 0:
                continue
            if not Routines.Checks.Skills.IsSkillSlotReady(skill_utility.custom_skill.skill_slot):
                continue
            energy_abs = custom_behavior_helpers.Resources.get_player_absolute_energy()
            cost = GLOBAL_CACHE.Skill.Data.GetEnergyCost(skill_utility.custom_skill.skill_id)
            if energy_abs < cost:
                continue

            # Find any ally in range (not just hurt — casting for ER trigger)
            target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast.value,
                condition=lambda agent_id: agent_id != player_id,
                sort_key=(TargetingOrder.HP_ASC,),
            )
            if target is None:
                continue

            result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(
                skill_utility.custom_skill, target_agent_id=target,
            )
            return result

        return BehaviorResult.ACTION_SKIPPED

    @override
    def customized_debug_ui(self, current_state: BehaviorState) -> None:
        PyImGui.text(f"Recovery active: {self._recovery_active}")
        PyImGui.text(f"ER active: {self._is_er_active()}")
