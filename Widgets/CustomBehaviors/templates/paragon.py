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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.i_am_unstoppable_utility import IAmUnstoppableUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.protective_shout_utility import ProtectiveShoutUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.templates.Paragon_UtilitySkills.heroic_refrain_utility import HeroicRefrainUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.distracting_shot_utility import DistractingShotUtility
from Widgets.CustomBehaviors.templates.RangerTao_UtilitySkills.savage_shot_utility import SavageShotUtility
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition

class ParagonBehavior(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        self.auto_attack: CustomSkillUtilityBase = AutoAttackUtility(current_build=in_game_build)

        self.heroic_refrain_utility: CustomSkillUtilityBase = HeroicRefrainUtility(current_build=in_game_build, score_definition=ScoreStaticDefinition(50))
        self.theyre_on_fire_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(skill=CustomSkill("Theyre_on_Fire"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO])
        
        self.theres_nothing_to_fear: CustomSkillUtilityBase = ProtectiveShoutUtility(skill=CustomSkill("Theres_Nothing_to_Fear"), current_build=in_game_build, 
                                                                                     allies_health_less_than_percent=0.9, 
                                                                                     allies_quantity_required=1,
                                                                                     score_definition= ScoreStaticDefinition(90), allowed_states=[BehaviorState.IN_AGGRO])
        
        self.save_yourselves_luxon: CustomSkillUtilityBase = ProtectiveShoutUtility(skill=CustomSkill("Save_Yourselves_luxon"), current_build=in_game_build, 
                                                                                    allies_health_less_than_percent=0.7, 
                                                                                    allies_quantity_required=1,
                                                                                    score_definition=ScoreStaticDefinition(89), allowed_states=[BehaviorState.IN_AGGRO])

        self.never_surrender: CustomSkillUtilityBase = ProtectiveShoutUtility(skill=CustomSkill("Never_Surrender"), current_build=in_game_build, 
                                                                              allies_health_less_than_percent=0.7,
                                                                              allies_quantity_required=2,
                                                                              score_definition=ScoreStaticDefinition(88), allowed_states=[BehaviorState.IN_AGGRO])
        
        #gravity center could be interesting

    @property
    @override
    def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
        return [
            self.auto_attack,
        ]

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return True
    
    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.heroic_refrain_utility,
            self.theyre_on_fire_utility,
            self.theres_nothing_to_fear,
            self.save_yourselves_luxon,
            self.never_surrender,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.heroic_refrain_utility.custom_skill,
        ]