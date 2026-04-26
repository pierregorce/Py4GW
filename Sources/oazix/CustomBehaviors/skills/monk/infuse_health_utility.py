from typing import Any, Generator, cast, override

from Py4GWCoreLib import Range, Routines, Agent, Player
from Sources.oazix.CustomBehaviors.primitives.infrastructure.persistence_locator import PersistenceLocator
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.scores.healing_score import HealingScore
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Sources.oazix.CustomBehaviors.skills.plugins.options.raw_boolean_option import RawBooleanOption
from Sources.oazix.CustomBehaviors.skills.plugins.options.raw_number_option import RawNumberOption


class InfuseHealthUtility(CustomSkillUtilityBase):
    """
    Infuse_Health utility.

    Targets lowest-health injured ally (excluding the player) within spellcast range.
    Will only consider casting if the player currently has BOTH:
      - Aura of Restoration (configurable)
      - Life Attunement (configurable)

    The buff checks use Routines.Checks.Effects.HasBuff(...) as requested: if either check
    returns False, evaluation returns None and casting is skipped.

    Safety: Uses player_can_sacrifice_health to prevent killing yourself.
    """

    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        score_definition: ScorePerHealthGravityDefinition = ScorePerHealthGravityDefinition(10),
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO],
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Infuse_Health"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )

        self.score_definition: ScorePerHealthGravityDefinition = score_definition

        # CustomSkill instances for the enchantments so we can reference their skill_id
        self._aura_skill = CustomSkill("Aura_of_Restoration")
        self._life_skill = CustomSkill("Life_Attunement")

        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "require_hp_higher_than_percent", default_value=0.40))
        self.add_plugin_option(lambda x: RawBooleanOption(x.custom_skill, "require_aura_of_restoration", default_value=True))
        self.add_plugin_option(lambda x: RawBooleanOption(x.custom_skill, "require_life_attunement", default_value=True))
        self.add_plugin_option(lambda x: RawBooleanOption(x.custom_skill, "should_cast_when_mana_low", default_value=False))
        self.add_plugin_option(lambda x: RawNumberOption(x.custom_skill, "mana_low_threshold", default_value=0.40))

    def _get_targets(self) -> list[custom_behavior_helpers.SortableAgentData]:
        player_agent = Player.GetAgentID()

        targets: list[custom_behavior_helpers.SortableAgentData] = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spellcast.value,
            condition=lambda agent_id: agent_id != player_agent, # we accept healing full life allies
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC),
        )
        return targets

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        """
        Evaluate Infuse_Health:

        - First check if we can safely sacrifice health (don't kill ourselves!)
        - Then check player buffs using Routines.Checks.Effects.HasBuff for Aura_of_Restoration
          and Life_Attunement (configurable requirements).
        - Optionally check if mana is low (if should_cast_when_mana_low is enabled).
        - If all checks pass, pick top injured ally and return emergency/damaged score.
        """
        require_hp_higher_than_percent_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("require_hp_higher_than_percent"))
        require_hp_higher_than_percent: float = require_hp_higher_than_percent_option.option_value
        should_cast_when_mana_low_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("should_cast_when_mana_low"))
        should_cast_when_mana_low: bool = should_cast_when_mana_low_option.option_value
        mana_low_threshold_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("mana_low_threshold"))
        mana_low_threshold: float = mana_low_threshold_option.option_value
        require_aura_of_restoration_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("require_aura_of_restoration"))
        require_aura_of_restoration: bool = require_aura_of_restoration_option.option_value
        require_life_attunement_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("require_life_attunement"))
        require_life_attunement: bool = require_life_attunement_option.option_value

        # 1 / Safety check: don't kill ourselves!
        # Don't Infuse when HP% is too low. With ER pre-heal, Infuse converges
        # to ~50% at normal HP. Under pressure or with inflated max HP, this floor
        # prevents sitting at dangerously low HP%.
        player_agent_id = Player.GetAgentID()
        if Agent.GetHealth(player_agent_id) < require_hp_higher_than_percent: return None


        # 2/ Check if mana is low (if enabled)
        if should_cast_when_mana_low:
            player_energy_percent = Agent.GetEnergy(player_agent_id)
            if player_energy_percent <= mana_low_threshold:
                return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY) # force cast when mana low (to regain energy)

        # 3/ Configurable buff checks using Routines.Checks.Effects.HasBuff
        try:
            has_aura = bool(custom_behavior_helpers.Resources.is_ally_under_specific_effect(player_agent_id, self._aura_skill.skill_id))
            has_life = bool(custom_behavior_helpers.Resources.is_ally_under_specific_effect(player_agent_id, self._life_skill.skill_id))
        except Exception:
            # If the buff-check call itself fails, be conservative and skip
            return None

        # Check if required buffs are present (based on configuration)
        if require_aura_of_restoration and not has_aura:
            return None
        if require_life_attunement and not has_life:
            return None

        targets = self._get_targets()
        if len(targets) == 0:
            return None

        top = targets[0]
        if top.hp < 0.40:
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED_EMERGENCY)
        if top.hp < 0.70: # reserve Infuse for truly damaged; should_cast_when_mana_low widens under energy pressure
            return self.score_definition.get_score(HealingScore.MEMBER_DAMAGED)

        return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        """
        Execution path re-checks safety, mana, and buffs defensively and then casts on the top target.
        """
        require_hp_higher_than_percent_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("require_hp_higher_than_percent"))
        require_hp_higher_than_percent: float = require_hp_higher_than_percent_option.option_value
        should_cast_when_mana_low_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("should_cast_when_mana_low"))
        should_cast_when_mana_low: bool = should_cast_when_mana_low_option.option_value
        mana_low_threshold_option: RawNumberOption = cast(RawNumberOption, self.get_plugin_option("mana_low_threshold"))
        mana_low_threshold: float = mana_low_threshold_option.option_value
        require_aura_of_restoration_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("require_aura_of_restoration"))
        require_aura_of_restoration: bool = require_aura_of_restoration_option.option_value
        require_life_attunement_option: RawBooleanOption = cast(RawBooleanOption, self.get_plugin_option("require_life_attunement"))
        require_life_attunement: bool = require_life_attunement_option.option_value

        # 1/ Safety check: don't kill ourselves!

        player_agent_id = Player.GetAgentID()
        if Agent.GetHealth(player_agent_id) < require_hp_higher_than_percent: return BehaviorResult.ACTION_SKIPPED

        # 2/ Check if mana is low (if enabled)
        if should_cast_when_mana_low:
            player_energy_percent = Agent.GetEnergy(player_agent_id)
            if player_energy_percent <= mana_low_threshold:
                # force cast on lowest-HP ally to regain energy
                target = custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                    within_range=Range.Spellcast.value * 1.5,
                    condition=lambda agent_id: agent_id != player_agent_id,
                    sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC))
                if target is None: return BehaviorResult.ACTION_SKIPPED
                result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target)
                return result

        try:
            has_aura = bool(Routines.Checks.Effects.HasBuff(player_agent_id, self._aura_skill.skill_id))
            has_life = bool(Routines.Checks.Effects.HasBuff(player_agent_id, self._life_skill.skill_id))
        except Exception:
            return BehaviorResult.ACTION_SKIPPED

        # Check if required buffs are present (based on configuration)
        if require_aura_of_restoration and not has_aura:
            return BehaviorResult.ACTION_SKIPPED
        if require_life_attunement and not has_life:
            return BehaviorResult.ACTION_SKIPPED

        targets = self._get_targets()
        if len(targets) == 0:
            return BehaviorResult.ACTION_SKIPPED

        target = targets[0]
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target.agent_id)
        return result