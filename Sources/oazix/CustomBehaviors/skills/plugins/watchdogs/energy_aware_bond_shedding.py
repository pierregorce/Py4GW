import time
from collections.abc import Generator
from typing import Any, override

import PyImGui

from Py4GWCoreLib import Agent, Player
from Py4GWCoreLib.Effect import Effects
from Sources.oazix.CustomBehaviors.primitives import constants
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.plugins.utility_skill_watchdog import UtilitySkillWatchdog

class EnergyAwareBondShedding(UtilitySkillWatchdog):
    """Progressively drops maintained bonds when player energy is under pressure.

    Iterates maintained buff instances for the parent skill, dropping the
    lowest-priority non-self target one at a time with a cooldown between
    drops to let energy stabilize.

    Priority: drops furthest-from-player targets first (backline before
    frontline).  Self is never dropped.
    """

    _DROP_COOLDOWN: float = 1.5  # seconds between drops

    def __init__(
        self,
        parent_skill: CustomSkill,
        energy_floor: float = 0.35,
    ) -> None:
        super().__init__(parent_skill, "energy_aware_bond_shedding")
        from_persistence = self.load_from_persistence(str(energy_floor))
        self.energy_floor: float = float(from_persistence)
        self._parent_skill_id: int = parent_skill.skill_id  # cache — never construct CustomSkill per tick
        self._last_drop_time: float = 0.0

    @property
    @override
    def data(self) -> str:
        return str(self.energy_floor)

    @override
    def render_debug_ui(self) -> None:
        self.energy_floor = PyImGui.input_float(
            f"Energy floor##energy_shedding_{self.parent_skill_name}",
            self.energy_floor,
        )
        PyImGui.text(f"Last drop: {time.time() - self._last_drop_time:.1f}s ago")

    @override
    def act(self) -> Generator[Any | None, Any | None, None]:
        player_id = Player.GetAgentID()
        energy = Agent.GetEnergy(player_id)

        if energy >= self.energy_floor:
            yield
            return

        now = time.time()
        if now - self._last_drop_time < self._DROP_COOLDOWN:
            if constants.DEBUG: print(f"COOLDOWN skill={self.parent_skill_name} energy={energy} floor={self.energy_floor}")
            yield
            return

        # Find a maintained instance of this skill to drop.
        # Drop furthest-from-player first (backline before frontline). Never self.
        player_x, player_y = Agent.GetXY(player_id)
        buffs = Effects.GetBuffs(player_id)
        if constants.DEBUG: print(f"SCANNING skill={self.parent_skill_name} skill_id={self._parent_skill_id} energy={energy} buffs={len(buffs)}")

        candidates: list[tuple[float, int]] = []  # (distance, buff_id)
        for buff in buffs:
            if buff.skill_id != self._parent_skill_id: continue

            target_agent_id = buff.target_agent_id
            
            if target_agent_id == 0 or target_agent_id == player_id:
                if constants.DEBUG: print(f"SKIP_SELF skill={self.parent_skill_name} tid={target_agent_id}")
                continue  # never drop self or non-targeted

            tx, ty = Agent.GetXY(target_agent_id)
            dist = (tx - player_x) ** 2 + (ty - player_y) ** 2
            candidates.append((dist, buff.buff_id))

        if candidates:
            # Drop the furthest target (highest distance²)
            candidates.sort(key=lambda c: c[0], reverse=True)
            if constants.DEBUG: print(f"DROPPING skill={self.parent_skill_name} buff_id={candidates[0][1]} candidates={len(candidates)}")
            Effects.DropBuff(candidates[0][1])
            self._last_drop_time = now
        else:
            if constants.DEBUG: print(f"NO_CANDIDATES skill={self.parent_skill_name} (only self-bonds remain)")

        yield