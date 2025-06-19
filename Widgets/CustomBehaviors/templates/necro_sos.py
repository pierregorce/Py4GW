from typing import List, Any, Generator, Callable, override
import time
from HeroAI.cache_data import CacheData
from Py4GWCoreLib import Range, GLOBAL_CACHE, Routines
from Py4GWCoreLib.enums import SpiritModelID
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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.blood_is_power_utility import BloodIsPowerUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.great_dwarf_weapon_utility import GreatDwarfWeaponUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.blood_bond_utility import BloodBondUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.spirit_light_utility import SpiritLightUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.soothing_memories_utility import SoothingMemoriesUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.mend_body_and_soul_utility import MendBodyAndSoulUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.protective_was_kaolai_utility import ProtectiveWasKaolaiUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.breath_of_the_great_dwarf_utility import BreathOfTheGreatDwarfUtility
from Widgets.CustomBehaviors.templates.RitualistSos_UtilitySkills.gaze_of_fury_utility import GazeOfFuryUtility
from Widgets.CustomBehaviors.templates.RitualistSos_UtilitySkills.painful_bond import PainfulBondUtility
from Widgets.CustomBehaviors.templates.RitualistSos_UtilitySkills.raw_spirit_utility import RawSpiritUtility
from Widgets.CustomBehaviors.templates.RitualistSos_UtilitySkills.signet_of_spirits import SignetOfSpiritsUtility
from Widgets.CustomBehaviors.templates.RitualistSos_UtilitySkills.summon_spirit_utility import SummonSpiritUtility

class NecroSos(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.great_dwarf_weapon_utility: CustomSkillUtilityBase = GreatDwarfWeaponUtility(skill=CustomSkill("Great_Dwarf_Weapon"), current_build=in_game_build, score_definition=ScoreStaticDefinition(30))

        self.signet_of_spirits_utility: CustomSkillUtilityBase = SignetOfSpiritsUtility(skill=CustomSkill("Signet_of_Spirits"), current_build=in_game_build, score_definition=ScoreStaticDefinition(92))
        self.vampirism_utility: CustomSkillUtilityBase = RawSpiritUtility(skill=CustomSkill("Vampirism"), current_build=in_game_build, score_definition=ScoreStaticDefinition(91), owned_spirit_model_id=SpiritModelID.VAMPIRISM)
        self.bloodsong_utility: CustomSkillUtilityBase = RawSpiritUtility(skill=CustomSkill("Bloodsong"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90), owned_spirit_model_id=SpiritModelID.BLOODSONG)
        self.gaze_of_fury_utility: CustomSkillUtilityBase = GazeOfFuryUtility(skill=CustomSkill("Gaze_of_Fury"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80))

        self.summon_spirit_utility: CustomSkillUtilityBase = SummonSpiritUtility(skill=CustomSkill("Summon_Spirits_kurzick"), current_build=in_game_build, score_definition=ScoreStaticDefinition(95), 
            owned_spirits= self.signet_of_spirits_utility.owned_spirit_model_ids + [self.vampirism_utility.owned_spirit_model_id, self.bloodsong_utility.owned_spirit_model_id, self.gaze_of_fury_utility.owned_spirit_model_id])

        self.painful_bond_utility: CustomSkillUtilityBase = PainfulBondUtility(skill=CustomSkill("Painful_Bond"), current_build=in_game_build, mana_required_to_cast=25, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 40 if enemy_qte >= 3 else 0 if enemy_qte <= 2 else 0))
        self.armor_of_unfeeling_utility: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Armor_of_Unfeeling"), current_build=in_game_build, score_definition=ScoreStaticDefinition(35))

        self.auto_attack: CustomSkillUtilityBase = AutoAttackUtility(current_build=in_game_build)

    @property
    @override
    def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
        return [self.auto_attack]

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return False

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.great_dwarf_weapon_utility,
            self.signet_of_spirits_utility,
            self.vampirism_utility,
            self.bloodsong_utility,
            self.gaze_of_fury_utility,
            self.summon_spirit_utility,
            self.painful_bond_utility,
            self.armor_of_unfeeling_utility,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.great_dwarf_weapon_utility.custom_skill,
            self.signet_of_spirits_utility.custom_skill,
            self.vampirism_utility.custom_skill,
            self.bloodsong_utility.custom_skill,
            self.gaze_of_fury_utility.custom_skill,
            self.summon_spirit_utility.custom_skill,
            self.painful_bond_utility.custom_skill,
        ]