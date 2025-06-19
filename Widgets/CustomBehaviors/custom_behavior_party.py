import inspect
import importlib
import pkgutil
from typing import Generator, Any, List

from Py4GWCoreLib import GLOBAL_CACHE, Routines
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_behavior_shared_memory import CustomBehaviorWidgetData, CustomBehaviorWidgetMemoryManager

DEBUG=True

class CustomBehaviorParty:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomBehaviorParty, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

    def get_party_is_enable(self) -> bool:
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        shared_data:CustomBehaviorWidgetData = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData(account_email)
        return shared_data.is_enabled

    def set_party_is_enable(self, is_enabled: bool):
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        shared_data:CustomBehaviorWidgetData = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData(account_email)
        CustomBehaviorWidgetMemoryManager().SetCustomBehaviorWidgetData(is_enabled, shared_data.party_target_id, shared_data.party_forced_state)

    def get_party_forced_state(self) -> BehaviorState|None:
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        shared_data:CustomBehaviorWidgetData = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData(account_email)
        result = BehaviorState(shared_data.party_forced_state) if shared_data.party_forced_state is not None else None
        return result

    def set_party_forced_state(self, state: BehaviorState | None):
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        shared_data:CustomBehaviorWidgetData = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData(account_email)
        CustomBehaviorWidgetMemoryManager().SetCustomBehaviorWidgetData(shared_data.is_enabled, shared_data.party_target_id, state.value if state is not None else None)

    def get_party_custom_target(self) -> int | None:
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        shared_data:CustomBehaviorWidgetData = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData(account_email)
        return shared_data.party_target_id

    def set_party_custom_target(self, target: int | None):
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        shared_data:CustomBehaviorWidgetData = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData(account_email)
        CustomBehaviorWidgetMemoryManager().SetCustomBehaviorWidgetData(shared_data.is_enabled, target, shared_data.party_forced_state)
