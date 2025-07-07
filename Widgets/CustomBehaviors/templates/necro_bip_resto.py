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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.blood_is_power_utility import BloodIsPowerUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.great_dwarf_weapon_utility import GreatDwarfWeaponUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.blood_bond_utility import BloodBondUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.spirit_light_utility import SpiritLightUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.soothing_memories_utility import SoothingMemoriesUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.mend_body_and_soul_utility import MendBodyAndSoulUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.protective_was_kaolai_utility import ProtectiveWasKaolaiUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.breath_of_the_great_dwarf_utility import BreathOfTheGreatDwarfUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class NecroBipResto(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.blood_is_power_utility: CustomSkillUtilityBase = BloodIsPowerUtility(skill=CustomSkill("Blood_is_Power"), current_build=in_game_build, score_definition=ScoreStaticDefinition(33))
        self.great_dwarf_weapon_utility: CustomSkillUtilityBase = GreatDwarfWeaponUtility(skill=CustomSkill("Great_Dwarf_Weapon"), current_build=in_game_build, score_definition=ScoreStaticDefinition(30), mana_required_to_cast=10)

        self.blood_bond_utility: CustomSkillUtilityBase = BloodBondUtility(skill=CustomSkill("Blood_Bond"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 25 if enemy_qte >= 2 else 0), mana_required_to_cast=15)

        self.breath_of_the_great_dwarf_utility: CustomSkillUtilityBase = BreathOfTheGreatDwarfUtility(skill=CustomSkill("Breath_of_the_Great_Dwarf"), current_build=in_game_build, score_definition=ScorePerHealthGravityDefinition(9))
        self.spirit_light_utility: CustomSkillUtilityBase = SpiritLightUtility(skill=CustomSkill("Spirit_Light"), current_build=in_game_build, score_definition=ScorePerHealthGravityDefinition(8))
        self.mend_body_and_soul_utility: CustomSkillUtilityBase = MendBodyAndSoulUtility(skill=CustomSkill("Mend_Body_and_Soul"), current_build=in_game_build, score_definition=ScorePerHealthGravityDefinition(7))
        self.soothing_memories_utility: CustomSkillUtilityBase = SoothingMemoriesUtility(skill=CustomSkill("Soothing_Memories"), current_build=in_game_build, score_definition=ScorePerHealthGravityDefinition(6))
        self.protective_was_kaolai_utility: CustomSkillUtilityBase = ProtectiveWasKaolaiUtility(skill=CustomSkill("Protective_Was_Kaolai"), current_build=in_game_build, score_definition=ScorePerHealthGravityDefinition(5))

        self.auto_attack: CustomSkillUtilityBase = AutoAttackUtility(current_build=in_game_build)

    @property
    @override
    def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
        return [self.auto_attack]

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return True

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.blood_is_power_utility,
            self.great_dwarf_weapon_utility,
            self.blood_bond_utility,
            self.spirit_light_utility,
            self.soothing_memories_utility,
            self.mend_body_and_soul_utility,
            self.protective_was_kaolai_utility,
            self.breath_of_the_great_dwarf_utility,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            # self.blood_is_power_utility.custom_skill,
            self.great_dwarf_weapon_utility.custom_skill,
            self.spirit_light_utility.custom_skill,
            self.soothing_memories_utility.custom_skill,
            self.mend_body_and_soul_utility.custom_skill,
            self.protective_was_kaolai_utility.custom_skill,
            self.breath_of_the_great_dwarf_utility.custom_skill,
        ]