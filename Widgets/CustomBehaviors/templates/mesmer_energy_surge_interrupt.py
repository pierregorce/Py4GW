from typing import List, Any, Generator, Callable
import time
from HeroAI.cache_data import CacheData
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Range, GLOBAL_CACHE, Routines


class MesmerEnergySurgeInterrupt(CustomBehaviorBase):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)


        #interrupt
        self.cry_of_pain: CustomSkill = CustomSkill("Cry_of_Pain")
        self.cry_of_frustration: CustomSkill = CustomSkill("Cry_of_Frustration")
        self.power_drain: CustomSkill = CustomSkill("Power_Drain")

        #combo
        self.mistrust: CustomSkill = CustomSkill("Mistrust")
        self.unnatural_signet: CustomSkill = CustomSkill("Unnatural_Signet")

        #shatter
        self.shatter_enchantment: CustomSkill = CustomSkill("Shatter_Enchantment")
        self.shatter_hex: CustomSkill = CustomSkill("Shatter_Hex")

        #others
        self.ebon_vanguard_assassin_support: CustomSkill = CustomSkill("Ebon_Vanguard_Assassin_Support")
        self.energy_surge: CustomSkill = CustomSkill("Energy_Surge")
        self.spiritual_pain: CustomSkill = CustomSkill("Spiritual_Pain")
        self.energy_tap: CustomSkill = CustomSkill("Energy_Tap")
        self.overload: CustomSkill = CustomSkill("Overload")
        self.arcane_echo: CustomSkill = CustomSkill("Arcane_Echo")

    @property
    def custom_behavior_build(self) -> List[CustomSkill]:
        result = [

            self.cry_of_pain,
            self.cry_of_frustration,
            self.power_drain,

            self.mistrust,
            self.unnatural_signet,

            self.energy_surge,
            self.ebon_vanguard_assassin_support,
            self.overload,
        ]

        return result

    def _handle_far_from_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield

    def _handle_close_to_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield

    def _handle_in_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:

            # power_drain
            if custom_behavior_helpers.get_player_absolute_energy() < 20:
                action: Callable[[], Generator[Any, Any, BehaviorResult]] = lambda: (yield from custom_behavior_helpers.cast_skill_to_lambda(
                        skill=self.power_drain,
                        select_target= lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                            within_range=Range.Spellcast,
                            condition= lambda agent_id: GLOBAL_CACHE.Agent.IsCasting(agent_id) and GLOBAL_CACHE.Skill.Flags.IsSpell(GLOBAL_CACHE.Agent.GetCastingSkill(agent_id)) and GLOBAL_CACHE.Skill.Data.GetActivation(GLOBAL_CACHE.Agent.GetCastingSkill(agent_id)) >= 0.250,
                            sort_key= (TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                            clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.power_drain.skill_id))
                        ))
                result = yield from custom_behavior_helpers.Helpers.wait_for_or_until_completion(500, action)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            # cry_of_pain
            condition = lambda agent_id: GLOBAL_CACHE.Agent.IsHexed(agent_id)
            if not Routines.Checks.Skills.IsSkillIDReady(self.cry_of_frustration.skill_id) :
                # it's better to interrupt even without hex-effect
                condition = lambda agent_id: True

            action: Callable[[], Generator[Any, Any, BehaviorResult]] = lambda: (yield from custom_behavior_helpers.cast_skill_to_lambda(
                    skill=self.cry_of_pain,
                    select_target= lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                        within_range=Range.Spellcast,
                        condition = lambda agent_id: condition(agent_id) and GLOBAL_CACHE.Agent.IsCasting(agent_id) and GLOBAL_CACHE.Skill.Data.GetActivation(GLOBAL_CACHE.Agent.GetCastingSkill(agent_id)) >= 0.250,
                        sort_key= (TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.CASTER_THEN_MELEE),
                        clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.cry_of_pain.skill_id))
                    ))
            result = yield from custom_behavior_helpers.Helpers.wait_for_or_until_completion(500, action)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # cry_of_frustration
            action: Callable[[], Generator[Any, Any, BehaviorResult]] = lambda: (yield from custom_behavior_helpers.cast_skill_to_lambda(
                    skill=self.cry_of_frustration,
                    select_target= lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                        within_range=Range.Spellcast,
                        condition= lambda agent_id: GLOBAL_CACHE.Agent.IsCasting(agent_id) and GLOBAL_CACHE.Skill.Data.GetActivation(GLOBAL_CACHE.Agent.GetCastingSkill(agent_id)) >= 0.250,
                        sort_key= (TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                        clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.cry_of_frustration.skill_id))
                    ))
            result = yield from custom_behavior_helpers.Helpers.wait_for_or_until_completion(500, action)
            if result is BehaviorResult.ACTION_PERFORMED: continue


            # energy_surge

            result = yield from custom_behavior_helpers.cast_skill_to_lambda(
                skill= self.energy_surge,
                select_target= lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.energy_surge.skill_id))
                )
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # other skills if mana above 10
            # we want to safeguard at least 10 mana to be able to interrupt anytime

            if custom_behavior_helpers.get_player_absolute_energy() < 10:
                continue

            # mistrust

            result = yield from custom_behavior_helpers.cast_skill_to_lambda(
                skill= self.mistrust,
                select_target= lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    condition=lambda agent_id: not GLOBAL_CACHE.Agent.IsHexed(agent_id) and GLOBAL_CACHE.Agent.IsCaster(agent_id),
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.mistrust.skill_id))
            )

            #overload

            result = yield from custom_behavior_helpers.cast_skill_to_lambda(
                skill=self.overload,
                select_target=lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    condition=lambda agent_id: not GLOBAL_CACHE.Agent.IsHexed(agent_id) and GLOBAL_CACHE.Agent.IsCaster(agent_id),
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.overload.skill_id))
            )

            # unnatural_signet

            result = yield from custom_behavior_helpers.cast_skill_to_lambda(
                skill=self.unnatural_signet,
                select_target=lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                    within_range=Range.Spellcast,
                    condition=lambda agent_id: GLOBAL_CACHE.Agent.IsHexed(agent_id) or GLOBAL_CACHE.Agent.IsEnchanted(agent_id),
                    sort_key=(TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC, TargetingOrder.HP_DESC),
                    clustered_foes_within_range=GLOBAL_CACHE.Skill.Data.GetAoERange(self.unnatural_signet.skill_id))
            )
            if result is BehaviorResult.ACTION_PERFORMED: continue

            if custom_behavior_helpers.get_player_absolute_energy() > 15:
                result = yield from custom_behavior_helpers.cast_skill_generic(self.ebon_vanguard_assassin_support)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            # for generic_skill in self.get_generic_behavior_build():
            #     result = yield from custom_behavior_helpers.cast_skill_generic(generic_skill)
            #     if result is BehaviorResult.ACTION_PERFORMED: continue

            yield from custom_behavior_helpers.auto_attack()
            yield