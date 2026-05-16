import PyImGui

from Py4GWCoreLib import ImGui
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.casting.casting_observer import CastingObserver
from Sources.oazix.CustomBehaviors.primitives.infrastructure.external_dependency_factory import ExternalDependencyFactory

@staticmethod
def render():
    PyImGui.text("Debug Casting Observer")
    render_casting_observer()

def render_casting_observer():
    casting_observer = CastingObserver()
    PyImGui.text("Casting Observer")
    if PyImGui.button("Clear"):
        casting_observer.clear()

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

        texture_file = ExternalDependencyFactory().path_locator.get_project_root_directory() + "\\" + GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(cast_state.skill_id)
        ImGui.DrawTexture(texture_file, 30, 30)
        PyImGui.text(f"Agent {agent_id}: {GLOBAL_CACHE.Skill.GetName(cast_state.skill_id)} (ID: {cast_state.skill_id})")

        # Show timing details
        if cast_state.activation_time_ms == 0:
            PyImGui.text(f"  Instant skill (0ms activation)")
        else:
            PyImGui.text(f"  Activation: {cast_state.activation_time_ms}ms | Elapsed: {elapsed_ms:.0f}ms | Remaining: {remaining_ms:.0f}ms")
            PyImGui.text(f"  Progress: {progress*100:.1f}% | Started at: {cast_state.cast_started_at_ms:.0f}ms")

        PyImGui.separator()

    PyImGui.separator()

    PyImGui.text("Casting History")

    casting_history = casting_observer.get_all_cast_history(window_ms=None)
    for agent_id in casting_history:

        for cast in casting_history[agent_id]:
            texture_file = ExternalDependencyFactory().path_locator.get_project_root_directory() + "\\" + GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(cast.skill_id)
            ImGui.DrawTexture(texture_file, 30, 30)
            PyImGui.same_line()
            PyImGui.text(f"Agent: {agent_id} Cast: {cast.skill_id} - {cast.activation_time_ms} - {cast.cast_started_at_ms} - {cast.was_interrupted} - {cast.cast_ended_at_ms} - Was interrupted: {cast.was_interrupted}")
            PyImGui.same_line()
            PyImGui.text(f"Name: {GLOBAL_CACHE.Skill.GetName(cast.skill_id)}")

        PyImGui.separator()
