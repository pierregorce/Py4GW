from typing import List, Any, Generator, Callable, Optional
from HeroAI.cache_data import CacheData
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE

class HelloWorld(CustomBehaviorBase):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)

        self.resurrection_signet: CustomSkill = CustomSkill("Resurrection_Signet")

    @property
    def custom_behavior_build(self) -> List[CustomSkill]:
        result = [
            self.resurrection_signet
        ]

        return result

    def _handle_far_from_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield

    def _handle_close_to_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield

    def _handle_in_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield