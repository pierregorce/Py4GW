import inspect
import importlib
import pkgutil
from types import ModuleType
from typing import Generator, Any

from HeroAI.custom_combat_behavior.custom_combat_behavior_base import CustomCombatBehaviorBase
from Py4GWCoreLib import Routines, Map

DEBUG=True

class CustomBehaviorLoader:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomBehaviorLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.custom_combat_behavior:CustomCombatBehaviorBase = None
            self.__throttle_timer_milliseconds = 5000
            self._initialized = True
            self.generator = self.__update()

    def __load_all_modules_in_folder(self, package_name: str):
        """
        Dynamically loads all modules in the given package.

        Args:
            package_name: The dot-separated name of the package (e.g., 'HeroAI.custom_combat_behavior').

        Returns:
            A list of `ModuleType` objects representing the loaded modules.
        """
        loaded_modules = []

        # Get the package object (to resolve its __path__)
        package = importlib.import_module(package_name)

        # Iterate over all modules in the package
        for module_info in pkgutil.iter_modules(package.__path__):
            module_name = f"{package_name}.{module_info.name}"  # Full dotted module name

            try:
                # Dynamically import the module
                module = importlib.import_module(module_name)
                if DEBUG: print(f"Loaded module: {module_name}")

                loaded_modules.append(module)
            except ImportError as e:
                print(f"Failed to import module {module_name}: {e}")

        return loaded_modules

    def __find_subclasses_in_folder(self, base_class, package_name: str) -> list[type]:
        """
        Finds all subclasses of `base_class` within the given package.

        Args:
            base_class: The base class to search for.
            package_name: The package name where the search should happen.

        Returns:
            A list of subclasses of the base_class.
        """
        subclasses = []
        modules = self.__load_all_modules_in_folder(package_name)

        for module in modules:
            # Inspect module contents for subclasses
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, base_class) and obj != base_class:
                    if DEBUG: print(f"Found subclass: {obj.__name__} (defined in {obj.__module__})")
                    subclasses.append(obj)

        return subclasses

    def __find_custom_behavior_type(self) -> type | None:

        subclasses: list[type] = self.__find_subclasses_in_folder(CustomCombatBehaviorBase, "HeroAI.custom_combat_behavior.templates")

        for subclass in subclasses:
            if DEBUG: print(f"Checking subclass: {subclass.__name__} (defined in {subclass.__module__})")
            from HeroAI.cache_data import CacheData
            instance: CustomCombatBehaviorBase = subclass(CacheData())
            if instance.is_custom_behavior_match_in_game_build():
                if DEBUG: print(f"Found custom behavior: {subclass.__name__} (defined in {subclass.__module__})")
                return subclass
            else:
                if DEBUG: print(f"{subclass.__name__} (defined in {subclass.__module__} - Custom behavior does not match in-game build.")

        if DEBUG: print("No class matches the criteria.")
        return None

    def __create_custom_behavior_instance_if_exists(self) -> CustomCombatBehaviorBase | None:
        custom_behavior_type:type | None = self.__find_custom_behavior_type()
        from HeroAI.cache_data import CacheData

        if custom_behavior_type is None:
            # if DEBUG: print(f"no custom behavior found")
            return None

        custom_behavior_instance: CustomCombatBehaviorBase = custom_behavior_type(CacheData())
        if DEBUG: print(f"custom behavior instance created ={custom_behavior_type} {custom_behavior_instance}")
        return custom_behavior_instance

    def __update(self) -> Generator[Any | None, Any | None, None]:
        while True:
            if not Routines.Checks.Map.MapValid():
                yield
                continue

            if Map.IsOutpost():
                if DEBUG: print(f"custom behavior instance affected")

                result = self.__create_custom_behavior_instance_if_exists()
                if result is not None:
                    if DEBUG: print(f"custom behavior instance affected")
                    self.custom_combat_behavior = result
                yield from Routines.Yield.wait(self.__throttle_timer_milliseconds)
                continue

            yield

    def update(self):
        try:
            next(self.generator)
        except StopIteration:
            print(f"CustomBehaviorLoader.create_or_update_custom_behavior_if_exists is not expected to StopIteration.")
        except Exception as e:
            print(f"CustomBehaviorLoader.create_or_update_custom_behavior_if_exists is not expected to exit : {e}")


