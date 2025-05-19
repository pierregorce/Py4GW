from typing import List, Any, Generator, Callable
import time
from HeroAI.cache_data import CacheData
from HeroAI.custom_combat_behavior import custom_combat_behavior_helpers, behavior_result
from HeroAI.custom_combat_behavior.behavior_result import BehaviorResult
from HeroAI.custom_combat_behavior.custom_combat_behavior_base import CustomCombatBehaviorBase
from HeroAI.custom_combat_behavior.targeting_order import TargetingOrder
from Py4GWCoreLib import Agent, Routines, Range, Effects, Skill, SkillBar

class MesmerEnergySurge(CustomCombatBehaviorBase):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)

        self.ebon_vanguard_assassin_support: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Ebon_Vanguard_Assassin_Support")
        self.cry_of_pain: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Cry_of_Pain")
        self.cry_of_frustration: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Cry_of_Frustration")
        self.unnatural_signet: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Unnatural_Signet")
        self.spiritual_pain: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Spiritual_Pain")
        self.mistrust: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Mistrust")
        self.energy_surge: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Energy_Surge")
        self.energy_tap: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Energy_Tap") # to replace by Great_Dwarf_Weapon/Air_of_Superiority/Smite_Condition
        self.overload: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Overload")
        self.arcane_echo: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Arcane_Echo")

    @property
    def custom_behavior_build(self) -> List[CustomCombatBehaviorBase.CustomSkill]:
        result = [
            self.energy_surge,
            self.cry_of_pain,
            self.cry_of_frustration,
            self.mistrust,
            self.unnatural_signet,
            # self.ebon_vanguard_assassin_support,
            self.energy_tap,
        ]

        return result

    def _handle_out_of_combat(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield

    def _handle_combat(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:

            if custom_combat_behavior_helpers.get_player_absolute_energy() < 20:

                # energy_tap

                result = yield from custom_combat_behavior_helpers.cast_skill_to_lambda(
                    skill=self.energy_tap,
                    select_target = lambda: custom_combat_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                        within_range=Range.Spellcast,
                        sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_ASC, TargetingOrder.HP_DESC, TargetingOrder.CASTER_THEN_MELEE), # isolated foe, with man health so more chance to have more mana
                        clustered_foes_within_range=Range.Adjacent.value
                    ))
                if result is BehaviorResult.ACTION_PERFORMED: continue

            # cry_of_pain
            action: Callable[[], Generator[Any, Any, BehaviorResult]] = lambda: (yield from custom_combat_behavior_helpers.cast_skill_to_lambda(
                    skill=self.cry_of_pain,
                    select_target= lambda: custom_combat_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                        within_range=Range.Spellcast,
                        condition = lambda agent_id: Agent.IsHexed(agent_id) and Agent.IsCasting(agent_id) and Skill.Data.GetActivation(Agent.GetCastingSkill(agent_id)) >= 0.250,
                        sort_key= (TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.CASTER_THEN_MELEE),
                        clustered_foes_within_range=Skill.Data.GetAoERange(self.cry_of_pain.skill_id))
                    ))
            result = yield from custom_combat_behavior_helpers.wait_for_or_until_completion(500, action)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # cry_of_frustration
            action: Callable[[], Generator[Any, Any, BehaviorResult]] = lambda: (yield from custom_combat_behavior_helpers.cast_skill_to_lambda(
                    skill=self.cry_of_frustration,
                    select_target= lambda: custom_combat_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                        within_range=Range.Spellcast,
                        condition= lambda agent_id: Agent.IsCasting(agent_id) and Skill.Data.GetActivation(Agent.GetCastingSkill(agent_id)) >= 0.250,
                        sort_key= (TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                        clustered_foes_within_range=Skill.Data.GetAoERange(self.cry_of_frustration.skill_id))
                    ))
            result = yield from custom_combat_behavior_helpers.wait_for_or_until_completion(500, action)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # energy_surge

            result = yield from custom_combat_behavior_helpers.cast_skill_to_lambda(
                skill= self.energy_surge,
                select_target= lambda: custom_combat_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=Skill.Data.GetAoERange(self.energy_surge.skill_id))
                )
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # other skills if mana above 10
            # we want to safeguard at least 10 mana to be able to interrupt anytime

            if custom_combat_behavior_helpers.get_player_absolute_energy() < 10:
                continue

            # mistrust

            result = yield from custom_combat_behavior_helpers.cast_skill_to_lambda(
                skill= self.mistrust,
                select_target= lambda: custom_combat_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    condition=lambda agent_id: not Agent.IsHexed(agent_id) and Agent.IsCaster(agent_id),
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=Skill.Data.GetAoERange(self.mistrust.skill_id))
            )

            # unnatural_signet

            result = yield from custom_combat_behavior_helpers.cast_skill_to_lambda(
                skill=self.unnatural_signet,
                select_target=lambda: custom_combat_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    condition=lambda agent_id: Agent.IsHexed(agent_id) or Agent.IsEnchanted(agent_id),
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=Skill.Data.GetAoERange(self.unnatural_signet.skill_id))
            )
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # if custom_combat_behavior_helpers.get_player_absolute_energy() > 13:
            #
            #     result = yield from custom_combat_behavior_helpers.cast_skill_to_lambda(self.spiritual_pain, select_target=
            #     lambda: custom_combat_behavior_helpers.get_best_enemy_target_for_condition(Range.Spellcast, lambda agent_id: Agent.GetHealth(agent_id) > 0.05))
            #     if result is BehaviorResult.ACTION_PERFORMED: continue

            # if custom_combat_behavior_helpers.get_player_absolute_energy() > 15:
                # result = yield from custom_combat_behavior_helpers.cast_skill_generic(self.ebon_vanguard_assassin_support)
                # if result is BehaviorResult.ACTION_PERFORMED: continue

            for generic_skill in self.get_generic_behavior_build():
                result = yield from custom_combat_behavior_helpers.cast_skill_generic(generic_skill)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            yield from custom_combat_behavior_helpers.auto_attack()
            yield