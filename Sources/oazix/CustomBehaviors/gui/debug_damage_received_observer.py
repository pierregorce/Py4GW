import time

import PyImGui

from Py4GWCoreLib import Agent, Player
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.shared_memory_src.AccountStruct import AccountStruct
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.casting.casting_observer import CastingObserver
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.damage_received.damage_received_observer import DamageReceivedObserver

@staticmethod
def render():
    PyImGui.text("Debug X")
    render_casting_observer()


def render_casting_observer():
    casting_observer = CastingObserver()
    PyImGui.text("Casting Observer")
    if PyImGui.button("Clear"):
        casting_observer.clear()

    PyImGui.text("Casting History")

    casting_history = casting_observer.get_all_cast_history(window_ms=None)
    for agent_id in casting_history:
        PyImGui.text(f"Agent: {agent_id}")
        for cast in casting_history[agent_id]:
            PyImGui.text(f"Cast: {cast.skill_id} - {cast.activation_time_ms} - {cast.cast_started_at_ms} - {cast.was_interrupted} - {cast.cast_ended_at_ms} - Was interrupted: {cast.was_interrupted}")
            PyImGui.same_line()
            PyImGui.text(f"Name: {GLOBAL_CACHE.Skill.GetName(cast.skill_id)}")
            PyImGui.separator()

    PyImGui.text("Current Casts")

    from Py4GWCoreLib import Map
    current_time = Map.GetInstanceUptime()

    dictionary = casting_observer._current_casts
    if len(dictionary) == 0:
        PyImGui.text("  (No active casts)")

    for agent_id in dictionary:
        cast_state = dictionary[agent_id]
        elapsed_ms = current_time - cast_state.cast_started_at_ms
        remaining_ms = cast_state.remaining_casting_time_ms
        progress = cast_state.cast_progress_percent

        # Show agent info
        PyImGui.text(f"Agent {agent_id}: {GLOBAL_CACHE.Skill.GetName(cast_state.skill_id)} (ID: {cast_state.skill_id})")

        # Show timing details
        if cast_state.activation_time_ms == 0:
            PyImGui.text(f"  Instant skill (0ms activation)")
        else:
            PyImGui.text(f"  Activation: {cast_state.activation_time_ms}ms | Elapsed: {elapsed_ms:.0f}ms | Remaining: {remaining_ms:.0f}ms")
            PyImGui.text(f"  Progress: {progress*100:.1f}% | Started at: {cast_state.cast_started_at_ms:.0f}ms")

        PyImGui.separator()
    

def render_damage_received_observer():
    PyImGui.text(f"Player Target ID: {Player.GetAgentID()}")
    if PyImGui.button("Clear"):
        DamageReceivedObserver().clear()

    damage_received_time_serie = DamageReceivedObserver().damage_received_time_serie
    accounts: list[AccountStruct] = GLOBAL_CACHE.ShMem.GetAllAccountData()
    accounts_by_agent_id: dict[int, AccountStruct] = {account.AgentData.AgentID: account for account in accounts}

    # per agent :
    window_ms = 1000
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

