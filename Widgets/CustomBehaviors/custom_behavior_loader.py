import inspect
import importlib
import pkgutil
from typing import Generator, Any, List

from Py4GWCoreLib import GLOBAL_CACHE, Routines
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.constants import DEBUG, USE_GENERIC_IF_NO_TEMPLATE
from Widgets.CustomBehaviors.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.generic_utility import GenericUtility

class MatchResult:
    def __init__(self, build_size: int, matching_count: int, instance: CustomBehaviorBase, is_matched_with_current_build: bool):
        self.build_size = build_size
        self.matching_count: int = matching_count
        self.matching_result = build_size - matching_count
        self.is_matched_with_current_build: bool = is_matched_with_current_build
        self.instance: CustomBehaviorBase = instance

class CustomBehaviorLoader:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomBehaviorLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.custom_combat_behavior:CustomBehaviorBase | None = None
            self._has_loaded = False
            self.__behaviors_found:List[MatchResult] = []
            self._initialized = True

    # internal

    def __find_subclasses_in_folder(self, base_class, package_name: str) -> list[type]:
        """
        Finds all direct subclasses of `base_class` within the given package.
        Excludes utility classes and non-direct children.

        Args:
            base_class: The base class to search for.
            package_name: The package name where the search should happen.

        Returns:
            A list of direct subclasses of the base_class.
        """

        def __is_utility_class(cls: type) -> bool:
            """
            Determines if a class is a utility class based on its characteristics.
            
            Args:
                cls: The class to check
                
            Returns:
                bool: True if the class appears to be a utility class
            """
            # Check if class name contains 'Utility'
            is_named_utility = 'Utility' in cls.__name__
            
            # Check if class has a utility flag or attribute
            has_utility_flag = getattr(cls, '_is_utility', False)
            
            # A class is considered a utility if:
            # 1. It has 'Utility' in its name, or
            # 2. It's explicitly marked as a utility class
            return is_named_utility or has_utility_flag

        def __load_all_modules_in_folder(full_package_name: str):
            """
            Dynamically loads all modules in the given package.

            Args:
                full_package_name: The dot-separated name of the package (e.g., 'HeroAI.custom_combat_behavior').

            Returns:
                A list of `ModuleType` objects representing the loaded modules.
            """
            loaded_modules = []

            # Get the package object (to resolve its __path__)
            package = importlib.import_module(full_package_name)

            # Iterate over all modules in the package
            for module_info in pkgutil.iter_modules(package.__path__):
                module_name = f"{full_package_name}.{module_info.name}"  # Full dotted module name

                try:
                    # Dynamically import the module
                    module = importlib.import_module(module_name)
                    if DEBUG: print(f"Loaded module: {module.__name__}")
                    loaded_modules.append(module)
                except ImportError as e:
                    print(f"Failed to import module {module_name}: {e}")

            return loaded_modules

        subclasses = []
        modules = __load_all_modules_in_folder(package_name)

        if DEBUG:
            print(f"\nSearching for subclasses of {base_class.__name__}")
            for module in modules:
                print(f"Module: {module.__name__}")

        for module in modules:
            # Inspect module contents for subclasses
            for name, obj in inspect.getmembers(module):
                
                # Check if it's a class, is a subclass of base_class, is not the base_class itself,
                # and is a direct child (has base_class as its only direct parent)
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, base_class)
                    and obj != base_class
                    and not __is_utility_class(obj)
                ):
                    if DEBUG: print(f"Found subclass: {obj.__name__}")
                    subclasses.append(obj)

        if DEBUG:
            print(f"Total subclasses found: {len(subclasses)}")

        return subclasses

    def __find_and_order_custom_behaviors(self) -> List[MatchResult]:

        subclasses: list[type] = self.__find_subclasses_in_folder(CustomBehaviorBase, "Widgets.CustomBehaviors.templates")
        matches: List[MatchResult] = []

        for subclass in subclasses:
            if DEBUG: print(f"Checking subclass: {subclass.__name__} (defined in {subclass.__module__})")
            from HeroAI.cache_data import CacheData
            instance: CustomBehaviorBase = subclass(CacheData())

            build_size = len(instance.skills_required_in_behavior)
            matching_count = instance.count_matches_between_custom_behavior_match_in_game_build()
            
            if matching_count == build_size:
                if DEBUG: print(f"Found custom behavior: {subclass.__name__} (defined in {subclass.__module__})")
                # matches.append((matching_count,instance, True))
                is_matched_with_current_build = True if matching_count > 0 else False
                matches.append(MatchResult(build_size=build_size, matching_count=matching_count, instance=instance, is_matched_with_current_build=is_matched_with_current_build))
            else:
                if DEBUG: print(f"{subclass.__name__} (defined in {subclass.__module__} - Custom behavior does not match in-game build.")
                matches.append(MatchResult(build_size=build_size, matching_count=matching_count, instance=instance, is_matched_with_current_build=False))


        matches = sorted(matches, key=lambda x: (x.matching_result, -x.matching_count))

        return matches

    # public

    def initialize_custom_behavior_candidate(self):

        if self._has_loaded:
            return

        if not Routines.Checks.Map.MapValid():
            return

        self.__behaviors_found = self.__find_and_order_custom_behaviors()
        __behaviors_candidates = [behavior for behavior in self.__behaviors_found if behavior.is_matched_with_current_build]
        result: CustomBehaviorBase | None = __behaviors_candidates[0].instance if len(__behaviors_candidates) > 0 else None

        party_number = GLOBAL_CACHE.Party.GetOwnPartyNumber()
        if DEBUG: print(f"party_number: {party_number}")
        from HeroAI.cache_data import CacheData
        shared_memory_handler = CacheData().HeroAI_vars.shared_memory_handler

        if result is not None:
            if DEBUG: print(f"custom behavior instance affected")
            self.custom_combat_behavior = result
            self.custom_combat_behavior.enable()
        else:
            if DEBUG: print(f"no custom behavior found")
            self.custom_combat_behavior = None

            # if USE_GENERIC_IF_NO_TEMPLATE:
            #     if DEBUG: 
            #         print(f"=> fallback to generic utility system")
            #         from HeroAI.cache_data import CacheData
            #         self.custom_combat_behavior = FullyGenericBehavior(cached_data=CacheData())

        self._has_loaded = True

    def refresh_custom_behavior_candidate(self):
        #load all and refresh
        self._has_loaded = False
        pass

    def get_all_custom_behavior_candidates(self) -> list[MatchResult] | None:
        if self._has_loaded: return self.__behaviors_found
        return None

    def ensure_custom_behavior_match_in_game_build(self):
        if self._has_loaded and self.custom_combat_behavior is not None:
            if type(self.custom_combat_behavior).mro()[1].__name__ == CustomBehaviorBaseUtility.__name__:
                utility_build:list[CustomSkillUtilityBase] = self.custom_combat_behavior.get_skills_final_list(False)
                in_game_build:dict[int, CustomSkill] = self.custom_combat_behavior.get_in_game_build()

                skill_ids_in_custom_behavior:list[int] = [item.custom_skill.skill_id for item in utility_build]
                is_completed:bool = self.custom_combat_behavior.complete_build_with_generic_skills

                for skill_id in skill_ids_in_custom_behavior:
                    if skill_id not in in_game_build.keys():
                        print(f"{skill_id} doesn't exist, stop customing")
                        self._has_loaded = False
                        self.custom_combat_behavior = None
                        return

                if is_completed:
                    for skill_id in in_game_build.keys():
                        if skill_id not in skill_ids_in_custom_behavior:
                            print(f"{skill_id} doesn't exist, stop customing")
                            self._has_loaded = False
                            self.custom_combat_behavior = None
                            return
                return
        return "pas custom"