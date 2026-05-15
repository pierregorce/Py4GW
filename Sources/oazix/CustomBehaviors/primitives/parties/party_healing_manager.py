


# from collections import deque
# from dataclasses import dataclass
# import time


# from Py4GWCoreLib import Agent
# from Py4GWCoreLib.CombatEvents import CombatEvents


# class DamagePacket:
#     def __init__(self, damage_taken: int):
#         self.damage_taken = damage_taken
#         self.timestamp = time.time()


# class DamageTimeSeries:
#     #we need some kind of time for each. another class maybe

#     def __init__(self, window_ms: int):
#         self.window_ms = window_ms
#         self._damage_packets: deque[DamagePacket] = deque(2000)

#     def update(self, damage_taken: int):
#         """O(1) - just append, no pruning."""
#         current_timestamp = time.time()
#         self._damage_taken += damage_taken
#         self._number_of_damage_packets += 1

#         if current_timestamp - self._last_update_timestamp > self._timeframe:
#             self._last_update_timestamp = current_timestamp
#             self._damage_taken = 0
#             self._number_of_damage_packets = 0

#     def _prune_if_needed(self):
#         """Only prune when reading data."""
#         current_time = time.time()
#         cutoff_time = current_time - (self.window_ms / 1000.0)
        
#         while self._damage_packets and self._damage_packets[0].timestamp < cutoff_time:
#             packet = self._damage_packets.popleft()
#             self._cached_total -= packet.damage_taken

#     def get_total_damage(self) -> int:
#         self._prune_if_needed()
#         return self._cached_total

#     def get_packet_count(self) -> int:
#         self._prune_if_needed()
#         return len(self._damage_packets)

# class AgentDamageData:
#     agent_id: int
#     account_email: str
#     damage_time_series: DamageTimeSeries

#     def update(self, damage_taken: int):
#         self.damage_time_series.update(damage_taken)

#     def get_score_by_number_of_damage_packets(self) -> float:
#         return self.damage_time_series.get_packet_count()

#     def get_score_by_raw_damage_taken(self) -> float:
#         return self.damage_time_series.get_total_damage()


# class PartyHealingManager:

#     _instance = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(PartyHealingManager, cls).__new__(cls)
#             cls._instance._initialized = False 

#             CombatEvents.Enable()
#             print("PartyHealingManager: Enabled CombatEvents")
#             CombatEvents.OnDamage(cls.on_damage)
#             print("PartyHealingManager: Registered OnDamage callback")
#         return cls._instance

#     def __init__(self):
#         if not self._initialized:
#             self._damage_taken_by_agent_id: dict[int, float] = {}
#             self._last_damage_taken_timestamp_by_agent_id: dict[int, int] = {}
#             self._initialized = True

#     def act(self):
#         CombatEvents.Update()
#         pass

# # CombatEvents.Enable()
# # CombatEvents.Update()
# # CombatEvents.OnDamage(on_damage)

#     # we cant track degen.
#     # can be done by only one account then pushed to shared memory ?
#     # or has to be done per accoutn ?
    
#     @staticmethod
#     def on_damage(target_agent_id: int, source_agent_id: int, damage_fraction: float, skill_id: int):
#         # NOTE: Damage value is a FRACTION of max HP, not absolute damage!
#         # def on_damage(target_id, source_id, damage_fraction, skill_id):

#         actual_damage = damage_fraction * Agent.GetMaxHealth(target_agent_id)

#         print(f"Dealt {damage_fraction}")
#         print(f"Dealt {actual_damage:.0f} damage")

