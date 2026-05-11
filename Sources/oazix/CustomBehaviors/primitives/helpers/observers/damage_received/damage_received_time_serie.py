from collections import deque
from dataclasses import dataclass

from Py4GWCoreLib import Map


@dataclass(frozen=True, slots=True)
class DamagePacket:
    damage_taken: int
    timestamp: float

class DamageReceivedTimeSerie:

    def __init__(self):
        self._damage_packets: dict[int, deque[DamagePacket]] = {}

    def get_number_of_damage_packets(self, agent_id: int, window_ms: int) -> int:
        now_ms = Map.GetInstanceUptime()
        cutoff_time = now_ms - window_ms
        damage_packets = self._damage_packets.get(agent_id, [])
        return sum(1 for packet in damage_packets if packet.timestamp > cutoff_time)

    def get_total_damage(self, agent_id: int, window_ms: int) -> int:
        now_ms = Map.GetInstanceUptime()
        cutoff_time = now_ms - window_ms
        damage_packets = self._damage_packets.get(agent_id, [])
        return sum(packet.damage_taken for packet in damage_packets if packet.timestamp > cutoff_time)
    
    def get_damage_packets(self, agent_id: int, window_ms: int) -> list[DamagePacket]:
        now_ms = Map.GetInstanceUptime()
        cutoff_time = now_ms - window_ms
        damage_packets = self._damage_packets.get(agent_id, [])
        filtered_packets = [packet for packet in damage_packets if packet.timestamp > cutoff_time]
        return filtered_packets
    
    def add_damage_packet(self, agent_id: int, damage_taken: int, timestamp: float):
        if agent_id not in self._damage_packets:
            self._damage_packets[agent_id] = deque(maxlen=2000)
        
        self._damage_packets[agent_id].append(DamagePacket(damage_taken, timestamp))
