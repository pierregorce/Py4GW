from typing import override

import PyImGui

from Py4GWCoreLib import Range
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.plugins.utility_skill_precondition import UtilitySkillPrecondition


class ShouldReserveEnergyForRez(UtilitySkillPrecondition):
    """Block energy-spending skills when dead allies exist and energy is low.

    Reserves enough energy for a resurrection skill (e.g., We Shall Return
    at 25e). Adrenaline skills and auto-attack cost 0 energy and pass
    automatically.
    """

    def __init__(self, parent_skill: CustomSkill, rez_energy_cost: int = 25):
        super().__init__(parent_skill, "reserve_energy_for_rez")
        from_persistence = self.load_from_persistence(str(rez_energy_cost))
        self.rez_energy_cost: int = int(from_persistence)

    @property
    @override
    def data(self) -> str:
        return str(self.rez_energy_cost)

    @override
    def is_satisfied(self) -> bool:
        # No dead allies → no reservation needed
        dead = custom_behavior_helpers.Targets.get_all_possible_allies_ordered_by_priority_raw(
            within_range=Range.Spellcast.value * 1.5,
            sort_key=(TargetingOrder.DISTANCE_ASC,),
            is_alive=False,
        )
        if not dead:
            return True

        # Check if we have enough energy for both this skill and the rez
        energy = custom_behavior_helpers.Resources.get_player_absolute_energy()
        skill_cost = GLOBAL_CACHE.Skill.Data.GetEnergyCost(
            CustomSkill(self.parent_skill_name).skill_id
        )
        return energy >= self.rez_energy_cost + skill_cost

    @override
    def render_debug_ui(self) -> None:
        self.rez_energy_cost = PyImGui.input_int(
            f"Rez energy reserve##{self.parent_skill_name}", self.rez_energy_cost
        )
