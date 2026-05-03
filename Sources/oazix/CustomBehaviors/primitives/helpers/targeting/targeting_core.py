from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_shared_memory import CustomBehaviorWidgetMemoryManager

class TargetingCore:
    def __init__(self):
        pass

    def is_lock_key_available(self, lock_key: str) -> bool:
        return not CustomBehaviorWidgetMemoryManager().GetSharedLockManager().is_lock_taken(lock_key)