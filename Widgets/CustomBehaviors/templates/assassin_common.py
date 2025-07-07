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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.ebon_battle_standard_of_honor_utility import EbonBattleStandardOfHonorUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.i_am_unstoppable_utility import IAmUnstoppableUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.distracting_shot_utility import DistractingShotUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.savage_shot_utility import SavageShotUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class AssassinCommon(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.critical_eye_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Critical_Eye"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.critical_agility_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Critical_Agility"), current_build=in_game_build, score_definition=ScoreStaticDefinition(70), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.way_of_the_master_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Way_of_the_Master"), current_build=in_game_build, score_definition=ScoreStaticDefinition(60), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])

        self.ebon_battle_standard_of_honor_utility: CustomSkillUtilityBase = EbonBattleStandardOfHonorUtility(skill=CustomSkill("Ebon_Battle_Standard_of_Honor"), current_build=in_game_build,  mana_required_to_cast=15)
        self.ebon_vanguard_assassin_support: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Ebon_Vanguard_Assassin_Support"), current_build=in_game_build, mana_required_to_cast=15)

        self.savage_shot_utility: CustomSkillUtilityBase = SavageShotUtility(skill=CustomSkill("Savage_Shot"), current_build=in_game_build, score_definition=ScoreStaticDefinition(91))
        self.distracting_shot_utility: CustomSkillUtilityBase = DistractingShotUtility(skill=CustomSkill("Distracting_Shot"), current_build=in_game_build, score_definition=ScoreStaticDefinition(92))
        self.i_am_unstopabble: CustomSkillUtilityBase = IAmUnstoppableUtility(current_build=in_game_build, score_definition=ScoreStaticDefinition(99))

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return False

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.critical_eye_utility,
            self.critical_agility_utility,
            self.ebon_vanguard_assassin_support,
            self.savage_shot_utility,
            self.distracting_shot_utility,
            # self.ebon_battle_standard_of_honor_utility,
            self.way_of_the_master_utility,
            self.i_am_unstopabble,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.critical_eye_utility.custom_skill,
            self.critical_agility_utility.custom_skill,
        ]