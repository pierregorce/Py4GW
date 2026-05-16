import PyImGui

from Py4GWCoreLib import Agent, Player
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.py4gwcorelib_src.Color import Color
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.interrupt_potential_scoring import InterruptPotentialScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy

@staticmethod
def render():
    PyImGui.text("Debug Targets")
    PyImGui.text(f"Player Target ID: {Player.GetTargetID()}")

    enemies = TargetingEnemy \
                .create_with_custom_interrupt_potential_scoring(InterruptPotentialScoring(skill_activation_min_duration_in_ms=250)) \
                .get_enemies(
                    within_range=Range.Spellcast.value,
                    sort_asc_predicate=lambda enemy_data: (-enemy_data.melee_optimised_aoe_score, enemy_data.distance_from_player),
                    range_to_count_clustered_enemies=Range.Adjacent.value)
    
    for enemy in enemies:
        if PyImGui.button(f"Target##{id(enemy)}"):
            Player.ChangeTarget(enemy.agent_id)     
        PyImGui.same_line(0, -1)
        PyImGui.text(f"Enemy: {enemy.agent_id}")
        PyImGui.same_line(0, -1)
        PyImGui.text(f"Name: {Agent.GetNameByID(enemy.agent_id)}")
        PyImGui.same_line(0, -1)
        PyImGui.text(f"Distance: {enemy.distance_from_player}")
        PyImGui.same_line(0, -1)
        PyImGui.text(f"enemy_quantity_within_range: {enemy.enemy_quantity_within_range}")
        PyImGui.same_line(0, -1)
        PyImGui.text(f"melee_optimised_aoe_score: {enemy.melee_optimised_aoe_score}")
        PyImGui.same_line(0, -1)
        PyImGui.text(f"interrupt_potential_score: {enemy.interrupt_potential_score}")

    PyImGui.spacing()
    PyImGui.separator()
    PyImGui.spacing()
