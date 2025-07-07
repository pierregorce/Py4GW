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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.ebon_battle_standard_of_honor_utility import EbonBattleStandardOfHonorUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.raw_aoe_attack_utility import RawAoeAttackUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.distracting_shot_utility import DistractingShotUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.savage_shot_utility import SavageShotUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.sundering_attack_utility import SunderingAttackUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.together_as_one_utility import TogetherAsOneUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class RangerTaoVolley(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.together_as_one_utility: CustomSkillUtilityBase = TogetherAsOneUtility(skill=CustomSkill("Together_as_one"), current_build=in_game_build, score_definition=ScoreStaticDefinition(95))
        self.never_rampage_alone_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Never_Rampage_Alone"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])

        self.savage_shot_utility: CustomSkillUtilityBase = SavageShotUtility(skill=CustomSkill("Savage_Shot"), current_build=in_game_build, score_definition=ScoreStaticDefinition(91))
        self.distracting_shot_utility: CustomSkillUtilityBase = DistractingShotUtility(skill=CustomSkill("Distracting_Shot"), current_build=in_game_build, score_definition=ScoreStaticDefinition(92))

        self.ebon_battle_standard_of_honor_utility: CustomSkillUtilityBase = EbonBattleStandardOfHonorUtility(skill=CustomSkill("Ebon_Battle_Standard_of_Honor"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 68 if enemy_qte >= 3 else 50 if enemy_qte <= 2 else 25))
    
        self.volley_utility: CustomSkillUtilityBase = RawAoeAttackUtility(skill=CustomSkill("Volley"), current_build=in_game_build, 
            score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 67 if enemy_qte >= 3 else 49 if enemy_qte <= 2 else 25))

        self.sundering_attack_utility: CustomSkillUtilityBase = SunderingAttackUtility(skill=CustomSkill("Sundering_Attack"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90))
        self.ebon_vanguard_assassin_support: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Ebon_Vanguard_Assassin_Support"), current_build=in_game_build, mana_required_to_cast=15)

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
            self.together_as_one_utility,
            self.sundering_attack_utility,
            self.never_rampage_alone_utility,
            self.ebon_battle_standard_of_honor_utility,
            self.volley_utility,
            self.savage_shot_utility,
            self.distracting_shot_utility,      
            self.ebon_vanguard_assassin_support,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.together_as_one_utility.custom_skill,
            self.volley_utility.custom_skill,
        ]