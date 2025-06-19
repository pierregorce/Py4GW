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
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.soul_twisting_utility import SoulTwistingUtility
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.armor_of_unfeeling_utility import ArmorOfUnfeelingUtility
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.boon_of_creation_utility import BoonOfCreationUtility
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.protective_spirit_utility import ProtectiveSpiritUtility
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.spirit_refresh_state import SpiritRefreshState
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.strength_of_honor_utility import StrengthOfHonorUtility

class RitualistSoulTwisting(CustomBehaviorBaseUtility):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        in_game_build = list(CustomBehaviorBase.get_in_game_build().values())
        
        self.soul_twisting_utility: CustomSkillUtilityBase = SoulTwistingUtility(skill=CustomSkill("Soul_Twisting"), current_build=in_game_build, score_definition=ScoreStaticDefinition(95))
        self.boon_of_creation_utility: CustomSkillUtilityBase = BoonOfCreationUtility(skill=CustomSkill("Boon_of_Creation"), current_build=in_game_build, score_definition=ScoreStaticDefinition(85))
        self.flesh_of_my_flesh_utility: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Flesh_of_My_Flesh"), current_build=in_game_build)
        self.ebon_vanguard_assassin_support: CustomSkillUtilityBase = GenericUtility(skill=CustomSkill("Ebon_Vanguard_Assassin_Support"), current_build=in_game_build, mana_required_to_cast=15)
        self.strength_of_honor_utility: CustomSkillUtilityBase = StrengthOfHonorUtility(skill=CustomSkill("Strength_of_Honor"), current_build=in_game_build, score_definition=ScoreStaticDefinition(20))
        
        # Protective spirits
        self.spirit_refresh_state = SpiritRefreshState()
        def refresh_shelter(): self.spirit_refresh_state._shelter_should_refresh_armor_of_unfeeling = True
        def refresh_union(): self.spirit_refresh_state._union_should_refresh_armor_of_unfeeling = True

        self.shelter_utility: CustomSkillUtilityBase = ProtectiveSpiritUtility(skill=CustomSkill("Shelter"), current_build=in_game_build, score_definition=ScoreStaticDefinition(66), spirit_refreshed=refresh_shelter)
        self.union_utility: CustomSkillUtilityBase = ProtectiveSpiritUtility(skill=CustomSkill("Union"), current_build=in_game_build, score_definition=ScoreStaticDefinition(65), spirit_refreshed=refresh_union)
        self.displacement_utility: CustomSkillUtilityBase = ProtectiveSpiritUtility(skill=CustomSkill("Displacement"), current_build=in_game_build, score_definition=ScoreStaticDefinition(64), spirit_refreshed=lambda: None)
        
        self.armor_of_unfeeling_utility: CustomSkillUtilityBase = ArmorOfUnfeelingUtility(skill=CustomSkill("Armor_of_Unfeeling"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), spirit_refresh_state=self.spirit_refresh_state)
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
            self.soul_twisting_utility,
            self.armor_of_unfeeling_utility,
            self.boon_of_creation_utility,
            self.flesh_of_my_flesh_utility,
            self.shelter_utility,
            self.union_utility,
            self.displacement_utility,
            self.ebon_vanguard_assassin_support,
            self.strength_of_honor_utility,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.soul_twisting_utility.custom_skill,
            self.armor_of_unfeeling_utility.custom_skill,
            self.boon_of_creation_utility.custom_skill,
            self.shelter_utility.custom_skill,
            self.union_utility.custom_skill,
        ]