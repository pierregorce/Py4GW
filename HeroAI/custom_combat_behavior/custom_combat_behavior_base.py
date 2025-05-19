from abc import abstractmethod
from typing import List, Generator, Any

from HeroAI.cache_data import CacheData
from Py4GWCoreLib import Player, Skill, Console, SkillBar

ConsoleDebug:bool = True

class CustomCombatBehaviorBase:
    """
    This class serves as a blueprint for creating custom combat behaviors that
    are compatible with specific game builds. Subclasses implementing this class
    should define the template and the combat behavior logic.
    """

    class CustomSkill:
        def __init__(self, skill_name: str):
            self.skill_name: str = skill_name
            self.skill_id: int = Skill.GetID(skill_name)

    def __init__(self, cached_data: CacheData):
        self._generator_handle_combat = self._handle_combat(cached_data)
        self._generator_handle_out_of_combat = self._handle_out_of_combat(cached_data)
        self.__cache_data = cached_data

    #build

    @staticmethod
    def get_in_game_build() -> dict[int, "CustomCombatBehaviorBase.CustomSkill"]:
        """
        return in-game build of the player as a dictionary.
        """
        ordered_skills_by_skill_id: dict[int, "CustomCombatBehaviorBase.CustomSkill"] = {}
        for i in range(8):
            skill_id = SkillBar.GetSkillIDBySlot(i + 1)
            skill_name =  Skill.GetName(skill_id)
            custom_skill = CustomCombatBehaviorBase.CustomSkill(skill_name)
            ordered_skills_by_skill_id[skill_id] = custom_skill

        return ordered_skills_by_skill_id

    @property
    @abstractmethod
    def custom_behavior_build(self) -> List[CustomSkill]:
        """
        set the custom behavior build we aim to customize in the child class.
        """
        pass

    def get_generic_behavior_build(self) -> List["CustomCombatBehaviorBase.CustomSkill"]:
        """
        get skills that are not customized, they'll use classic heroAI behavior.
        ordered by HeroAI.priority
        """

        def __get_custom_behavior_build() -> dict[int, "CustomCombatBehaviorBase.CustomSkill"]:
            custom_behavior_build = self.custom_behavior_build
            skills_by_skill_id: dict[int, "CustomCombatBehaviorBase.CustomSkill"] = {}
            for custom_behavior_build_skill in custom_behavior_build:
                skills_by_skill_id[custom_behavior_build_skill.skill_id] = custom_behavior_build_skill

            return skills_by_skill_id

        from Widgets import HeroAI
        self.__cache_data.combat_handler.PrioritizeSkills()
        generic_skills:List[HeroAI.CombatClass.SkillData] = self.__cache_data.combat_handler.skills

        custom_skills:dict[int, "CustomCombatBehaviorBase.CustomSkill"] = __get_custom_behavior_build()
        not_customized_skills: List["CustomCombatBehaviorBase.CustomSkill"] = []

        for skill in generic_skills:
            if custom_skills.get(skill.skill_id) is None:
                not_customized_skills.append(CustomCombatBehaviorBase.CustomSkill(Skill.GetName(skill.skill_id)))

        return not_customized_skills

    def is_custom_behavior_match_in_game_build(self) -> bool:
        """
        Check if this custom behavior class match the current in game build.
        """
        in_game_build:dict[int, "CustomCombatBehaviorBase.CustomSkill"] = self.get_in_game_build()
        custom_behavior_build:List["CustomCombatBehaviorBase.CustomSkill"] = self.custom_behavior_build

        for custom_skill in custom_behavior_build:
            if in_game_build.get(custom_skill.skill_id) is None:
                print(f"custom-behavior : {custom_skill.skill_name} not found in the in-game build.")
                return False

        generic_skills:List["CustomCombatBehaviorBase.CustomSkill"] = self.get_generic_behavior_build()
        print(f"Custom combat behavior detected : {self.__class__.__name__}.")
        print(f"Custom skills are : {[f'{skill.skill_name} (ID: {skill.skill_id})' for skill in custom_behavior_build]}.")
        print(f"Generic skills are : {[f'{skill.skill_name} (ID: {skill.skill_id})' for skill in generic_skills]}.")

        return True

    #combat

    def handle_combat(self, cached_data: CacheData) -> bool:
        if not cached_data.data.is_combat_enabled:
            return False

        if not cached_data.data.in_aggro:
            return False

        try:
            next(self._generator_handle_combat)
            return False
            # return False is equivalent to continue with other possible actions (LOOT, FOLLOW, ect)

        except StopIteration:
            print(f"CustomCombatBehaviorBase.act is not expected to StopIteration.")
        except Exception as e:
            print(f"CustomCombatBehaviorBase.act is not expected to exit : {e}")

        return False

    def handle_out_of_combat(self, cached_data: CacheData) -> bool:
        if not cached_data.data.is_combat_enabled:
            return False

        if cached_data.data.in_aggro:
            return False

        try:
            next(self._generator_handle_out_of_combat)
            return False
            # return False is equivalent to continue with other possible actions (LOOT, FOLLOW, ect)

        except StopIteration:
            print(f"CustomCombatBehaviorBase.act is not expected to StopIteration.")
        except Exception as e:
            print(f"CustomCombatBehaviorBase.act is not expected to exit : {e}")

        return False

    #abstract

    @abstractmethod
    def _handle_combat(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        pass

    @abstractmethod
    def _handle_out_of_combat(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        pass