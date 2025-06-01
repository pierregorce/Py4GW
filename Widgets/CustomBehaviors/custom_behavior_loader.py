import inspect
import importlib
import pkgutil
from typing import Generator, Any, List

from Py4GWCoreLib import GLOBAL_CACHE, Routines
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase

DEBUG=True

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
        Finds all subclasses of `base_class` within the given package.

        Args:
            base_class: The base class to search for.
            package_name: The package name where the search should happen.

        Returns:
            A list of subclasses of the base_class.
        """

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
                    # importlib.reload(module)
                    if DEBUG: print(f"Loaded module: {module.__name__}")

                    loaded_modules.append(module)
                except ImportError as e:
                    print(f"Failed to import module {module_name}: {e}")

            return loaded_modules

        subclasses = []
        modules = __load_all_modules_in_folder(package_name)

        for module in modules:
            # Inspect module contents for subclasses
            for name, obj in inspect.getmembers(module):

                if inspect.isclass(obj) and issubclass(obj, base_class) and obj != base_class:
                    if DEBUG: print(f"Found subclass: {obj.__name__} (defined in {obj.__module__})")
                    subclasses.append(obj)

        return subclasses

    def __find_and_order_custom_behaviors(self) -> List[MatchResult]:

        subclasses: list[type] = self.__find_subclasses_in_folder(CustomBehaviorBase, "Widgets.CustomBehaviors.templates")
        matches: List[MatchResult] = []

        for subclass in subclasses:
            if DEBUG: print(f"Checking subclass: {subclass.__name__} (defined in {subclass.__module__})")
            from HeroAI.cache_data import CacheData
            instance: CustomBehaviorBase = subclass(CacheData())

            build_size = len(instance.custom_behavior_build)
            matching_count = instance.count_matches_between_custom_behavior_match_in_game_build()

            if matching_count == build_size:
                if DEBUG: print(f"Found custom behavior: {subclass.__name__} (defined in {subclass.__module__})")
                # matches.append((matching_count,instance, True))
                matches.append(MatchResult(build_size, matching_count, instance, True))
            else:
                if DEBUG: print(f"{subclass.__name__} (defined in {subclass.__module__} - Custom behavior does not match in-game build.")
                matches.append(MatchResult(build_size, 0, instance, False))

        matches.sort(key=lambda x: x.matching_result, reverse=False)
        matches.sort(key=lambda x: x.matching_count, reverse=True)

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
            shared_memory_handler.set_game_option_property(party_number, "Combat", False)
        else:
            if DEBUG: print(f"no custom behavior found")
            self.custom_combat_behavior = None
            shared_memory_handler.set_game_option_property(party_number, "Combat", True)

        self._has_loaded = True

    def refresh_custom_behavior_candidate(self):
        #load all and refresh
        self._has_loaded = False
        pass

    def get_all_custom_behavior_candidates(self) -> List[MatchResult] | None:
        if self._has_loaded: return self.__behaviors_found
        return None