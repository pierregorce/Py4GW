from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_shared_memory import CustomBehaviorWidgetMemoryManager

class TargetingCore:
    def __init__(self):
        pass

    def is_lock_key_available(self, lock_key: str) -> bool:
        return not CustomBehaviorWidgetMemoryManager().GetSharedLockManager().is_lock_taken(lock_key)
    
    @staticmethod
    def is_player_close_to_combat() -> bool:
        return False
    
    @staticmethod
    def is_player_in_aggro() -> bool:
        return False

    def is_party_in_aggro() -> bool:
        return False

    @staticmethod
    def is_party_leader_in_aggro() -> bool:
        return False

    @staticmethod
    def is_party_member_in_aggro(agent_id: int) -> bool:
        return False