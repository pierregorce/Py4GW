from typing import List, Any, Generator, Callable, override
import time
from HeroAI.cache_data import CacheData
from Py4GWCoreLib import Range, GLOBAL_CACHE, Routines
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.custom_behavior_helpers import Targets
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.generic_utility import GenericUtility
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.auto_attack_utility import AutoAttackUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.ebon_battle_standard_of_wisdom_utility import EbonBattleStandardOfWisdom
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.cry_of_frustration_utility import CryOfFrustrationUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.cry_of_pain_utility import CryOfPainUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.mistrust_utility import MistrustUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.shatter_hex_utility import ShatterHexUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.unnatural_signet_utility import UnnaturalSignetUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.fall_back_utility import FallBackUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.power_drain_utility import PowerDrainUtility
from Widgets.CustomBehaviors.templates.MesmerEnergySurge_UtilitySkills.drain_enchantment_utility import DrainEnchantmentUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.raw_aoe_attack_utility import RawAoeAttackUtility

class MesmerESurgery(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.cry_of_pain_utility: CustomSkillUtilityBase = CryOfPainUtility(skill=CustomSkill("Cry_of_Pain"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90))
        self.cry_of_frustration_utility: CustomSkillUtilityBase = CryOfFrustrationUtility(skill=CustomSkill("Cry_of_Frustration"), current_build=in_game_build, score_definition=ScoreStaticDefinition(91))
        self.power_drain_utility: CustomSkillUtilityBase = PowerDrainUtility(skill=CustomSkill("Power_Drain"), current_build=in_game_build, score_definition=ScoreStaticDefinition(92))

        self.mistrust_utility: CustomSkillUtilityBase = MistrustUtility(skill=CustomSkill("Mistrust"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 70 if enemy_qte >= 3 else 40 if enemy_qte <= 2 else 0), mana_required_to_cast=10)
        self.unnatural_signet_utility: CustomSkillUtilityBase = UnnaturalSignetUtility(skill=CustomSkill("Unnatural_Signet"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 90 if enemy_qte >= 2 else 40 if enemy_qte <= 2 else 0))

        self.shatter_hex_utility: CustomSkillUtilityBase = ShatterHexUtility(skill=CustomSkill("Shatter_Hex"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 95 if enemy_qte >= 2 else 20))
        self.shatter_enchantment_utility: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Shatter_Enchantment"), current_build=in_game_build)
        self.drain_enchantment_utility: CustomSkillUtilityBase = DrainEnchantmentUtility(skill=CustomSkill("Drain_Enchantment"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 95 if enemy_qte >= 2 else 20))

        self.energy_tap_utility: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Energy_Tap"), current_build=in_game_build)

        #simple AoE based
        self.energy_surge_utility: CustomSkillUtilityBase = RawAoeAttackUtility(skill=CustomSkill("Energy_Surge"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 80 if enemy_qte >= 3 else 50 if enemy_qte <= 2 else 0), mana_required_to_cast=12)
        self.overload_utility: CustomSkillUtilityBase = RawAoeAttackUtility(skill=CustomSkill("Overload"), current_build=in_game_build, mana_required_to_cast=15)
        self.chaos_storm_utility: CustomSkillUtilityBase = RawAoeAttackUtility(skill=CustomSkill("Chaos_Storm"), current_build=in_game_build, mana_required_to_cast=15) 
        self.wastrels_demise_utility: CustomSkillUtilityBase = RawAoeAttackUtility(skill=CustomSkill("Wastrels_Demise"), current_build=in_game_build, mana_required_to_cast=15) 

        # self.spiritual_pain_utility: CustomSkillUtilityBase = SpiritualPainUtility(skill=CustomSkill("Spiritual_Pain"), current_build=in_game_build, mana_required_to_cast=15)

        self.fall_back_utility: CustomSkillUtilityBase = FallBackUtility(skill=CustomSkill("Fall_Back"), current_build=in_game_build)

        self.ebon_vanguard_assassin_support: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Ebon_Vanguard_Assassin_Support"), score_definition=ScoreStaticDefinition(71), current_build=in_game_build, mana_required_to_cast=15)
        self.ebon_battle_standard_of_wisdom: CustomSkillUtilityBase = EbonBattleStandardOfWisdom(skill=CustomSkill("Ebon_Battle_Standard_of_Wisdom"),score_definition= ScorePerAgentQuantityDefinition(lambda enemy_qte: 70 if enemy_qte >= 3 else 30 if enemy_qte <= 2 else 0), current_build=in_game_build, mana_required_to_cast=18)

        self.auto_attack: CustomSkillUtilityBase = AutoAttackUtility(current_build=in_game_build)
    
    @property
    @override
    def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
        return [self.auto_attack]
    
    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.cry_of_pain_utility,
            self.cry_of_frustration_utility,

            self.shatter_hex_utility,
            self.shatter_enchantment_utility,
            self.drain_enchantment_utility,

            self.mistrust_utility,
            self.unnatural_signet_utility,

            self.energy_surge_utility,

            self.power_drain_utility,

            self.energy_tap_utility,
            self.overload_utility,

            self.fall_back_utility,

            self.ebon_vanguard_assassin_support,
            self.ebon_battle_standard_of_wisdom
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.cry_of_pain_utility.custom_skill,
            self.cry_of_frustration_utility.custom_skill,
            self.energy_surge_utility.custom_skill,
        ]