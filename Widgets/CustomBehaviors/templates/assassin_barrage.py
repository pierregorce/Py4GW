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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.raw_aoe_attack_utility import RawAoeAttackUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.blood_is_power_utility import BloodIsPowerUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.great_dwarf_weapon_utility import GreatDwarfWeaponUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.blood_bond_utility import BloodBondUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.spirit_light_utility import SpiritLightUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.soothing_memories_utility import SoothingMemoriesUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.mend_body_and_soul_utility import MendBodyAndSoulUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.protective_was_kaolai_utility import ProtectiveWasKaolaiUtility
from Widgets.CustomBehaviors.templates.NecroBipResto_UtilitySkills.breath_of_the_great_dwarf_utility import BreathOfTheGreatDwarfUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.distracting_shot_utility import DistractingShotUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.savage_shot_utility import SavageShotUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class AssassinBarrage(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.critical_eye_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Critical_Eye"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), mana_required_to_cast=10)
        self.way_of_the_master_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Way_of_the_Master"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), mana_required_to_cast=10)
        self.barrage_utility: CustomSkillUtilityBase = RawAoeAttackUtility( skill=CustomSkill("Barrage"), score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 67), mana_required_to_cast=10,current_build=in_game_build)
        self.savage_shot_utility: CustomSkillUtilityBase = SavageShotUtility(skill=CustomSkill("Savage_Shot"), current_build=in_game_build, score_definition=ScoreStaticDefinition(91))
        self.distracting_shot_utility: CustomSkillUtilityBase = DistractingShotUtility(skill=CustomSkill("Distracting_Shot"), current_build=in_game_build, score_definition=ScoreStaticDefinition(92))
            
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
            self.critical_eye_utility,
            self.way_of_the_master_utility,
            self.barrage_utility,
            self.savage_shot_utility,
            self.distracting_shot_utility,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.barrage_utility.custom_skill,
            self.critical_eye_utility.custom_skill,
            self.way_of_the_master_utility.custom_skill,

        ]