import PyImGui

from Py4GWCoreLib import Agent, Player
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.shared_memory_src.AccountStruct import AccountStruct
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.casting.casting_observer import CastingObserver
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.damage_received.damage_received_observer import DamageReceivedObserver

@staticmethod
def render():
    PyImGui.text("Debug Damage Received Observer")
    render_damage_received_observer()
 
def render_damage_received_observer():
    PyImGui.text(f"Player Target ID: {Player.GetAgentID()}")
    if PyImGui.button("Clear"):
        DamageReceivedObserver().clear()

    damage_received_time_serie = DamageReceivedObserver().damage_received_time_serie
    accounts: list[AccountStruct] = GLOBAL_CACHE.ShMem.GetAllAccountData()
    accounts_by_agent_id: dict[int, AccountStruct] = {account.AgentData.AgentID: account for account in accounts}

    # per agent :
    window_ms = 5000
    PyImGui.text(f"Window: {window_ms}ms")
    for agent_id in damage_received_time_serie._damage_packets:
        account = accounts_by_agent_id.get(agent_id, None)
        PyImGui.text(f"Agent: {agent_id} ({account.AgentData.CharacterName if account else Agent.GetNameByID(agent_id)})")
        PyImGui.text(f"Number of damage packets: {damage_received_time_serie.get_number_of_damage_packets(agent_id, window_ms)}")

        # windowed
        PyImGui.text(f"                 Total damage: {damage_received_time_serie.get_total_damage(agent_id, window_ms)}")
        PyImGui.text(f"                 Number of damage packets: {damage_received_time_serie.get_number_of_damage_packets(agent_id, window_ms)}")

        # raw list, order by time desc, limit to 10, within the window
        data = damage_received_time_serie.get_damage_packets(agent_id, window_ms)
        data.sort(key=lambda damage_packet: damage_packet.timestamp, reverse=True)

        for damage_packet in data[:20]:
            PyImGui.text(f"                 Damage:{damage_packet.damage_taken} at {damage_packet.timestamp}")
    
    PyImGui.spacing()
    PyImGui.separator()
    PyImGui.spacing()

