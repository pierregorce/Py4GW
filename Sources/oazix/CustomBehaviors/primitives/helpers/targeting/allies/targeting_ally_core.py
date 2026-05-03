from typing import cast
from Py4GWCoreLib import AgentArray, Agent, Player, Utils
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_allegiance import TargetingAllyAllegiance
from Sources.oazix.CustomBehaviors.primitives.parties.memory_cache_manager import MemoryCacheManager


class TargetingAllyCore:

    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TargetingAllyCore, cls).__new__(cls)
        return cls._instance

    # ----------------------------- Cache Key Builder -----------------------------

    @staticmethod
    def __round_pos(pos: tuple[float, float]) -> tuple[int, int]:
        """Round position to reduce cache key variations (positions within ~10 units share cache)."""
        return (int(pos[0] / 10) * 10, int(pos[1] / 10) * 10)

    @classmethod
    def __build_combined_ally_targets_key(
        cls,
        source_pos: tuple[float, float],
        within_range: float,
        allegiance_to_include: TargetingAllyAllegiance,
    ) -> str:
        rounded = cls.__round_pos(source_pos)
        allegiance_part = f"allegiance:{allegiance_to_include.value}"
        return f"combined|pos:{rounded[0]},{rounded[1]}|range:{within_range:.0f}|{allegiance_part}"

    # ----------------------------- Agent Data Builder -----------------------------

    @staticmethod
    def __build_sortable_agent_data(agent_id: int, source_pos: tuple[float, float]) -> TargetingAllyData:
        """Build a TargetingAllyData object for the given agent."""
        agent_pos = Agent.GetXY(agent_id)
        
        return TargetingAllyData(
            agent_id=agent_id,
            distance_from_player=Utils.Distance(agent_pos, source_pos),
            hp=Agent.GetHealth(agent_id),
            energy=Agent.GetEnergy(agent_id),

            enemy_quantity_within_range=0,  # Computed separately if needed
            anemy_and_ally_quantity_within_range=0,  # Computed separately if needed
            ally_quantity_within_range=0,  # Computed separately if needed
            
            hex_priority_score=0,  # Computed separately if needed
            condition_priority_score=0,  # Computed separately if needed

            overidden_score=None,  # Computed separately if needed
        )

    def refresh(self):
        """Clear all cached data. Call this at the start of each frame/tick."""
        MemoryCacheManager().refresh()

    # ----------------------------- Private Helper Methods -----------------------------

    def __get_allies_by_distance(
            self,
            source_pos: tuple[float, float],
            within_range: float,
            allegiance_to_include: TargetingAllyAllegiance
    ) -> list[TargetingAllyData]:
        """
        Get allies within range of a position based on allegiance flags.

        :param source_pos: Source position to measure distance from
        :param within_range: Maximum distance
        :param allegiance_to_include: Flags indicating which allegiances to include
        :return: List of TargetingAllyData for allies within range
        """
        all_ally_ids: list[int] = []

        # Collect allies based on allegiance flags
        if allegiance_to_include & TargetingAllyAllegiance.Ally:
            all_ally_ids.extend(AgentArray.GetAllyArray())

        if allegiance_to_include & TargetingAllyAllegiance.Spirit:
            spirit_pet_array = AgentArray.GetSpiritPetArray()
            # Filter to only spirits (IsSpawned means it's a spirit)
            spirits = [agent_id for agent_id in spirit_pet_array if Agent.IsSpawned(agent_id)]
            all_ally_ids.extend(spirits)

        if allegiance_to_include & TargetingAllyAllegiance.Pet:
            spirit_pet_array = AgentArray.GetSpiritPetArray()
            # Filter to only pets (not spawned means it's a pet)
            pets = [agent_id for agent_id in spirit_pet_array if not Agent.IsSpawned(agent_id)]
            all_ally_ids.extend(pets)

        if allegiance_to_include & TargetingAllyAllegiance.Minion:
            all_ally_ids.extend(AgentArray.GetMinionArray())

        if allegiance_to_include & TargetingAllyAllegiance.NpcInParty:
            all_ally_ids.extend(AgentArray.GetNPCMinipetArray())

        # Deduplicate
        unique_ally_ids = list(set(all_ally_ids))

        # Filter by distance
        ally_ids_in_range = AgentArray.Filter.ByDistance(unique_ally_ids, source_pos, within_range)

        return [self.__build_sortable_agent_data(agent_id, source_pos) for agent_id in ally_ids_in_range]

    # ----------------------------- Combined Helpers -----------------------------

    def get_combined_ally_targets(
            self,
            source_pos: tuple[float, float] | None,
            within_range: float,
            allegiance_to_include: TargetingAllyAllegiance = TargetingAllyAllegiance.Ally | TargetingAllyAllegiance.Pet | TargetingAllyAllegiance.Minion,
    ) -> list[TargetingAllyData]:
        """
        Get combined list of allies from multiple sources (cached).

        :param source_pos: Source position (if None, uses Player.GetXY())
        :param within_range: Base range to search for allies
        :param allegiance_to_include: Flags indicating which allegiances to include
        :param is_alive: Whether to filter for alive agents only (default: True)
        :return: List of TargetingAllyData
        """
        # Use player position if source_pos is None
        if source_pos is None:
            source_pos = Player.GetXY()

        cache_key = self.__build_combined_ally_targets_key(source_pos, within_range, allegiance_to_include)

        # Check cache first
        cached = MemoryCacheManager().get(cache_key)
        if cached is not None:
            return cast(list[TargetingAllyData], cached)

        # Compute the result
        agents: list[TargetingAllyData] = self.__get_allies_by_distance(
            source_pos, within_range, allegiance_to_include
        )

        # Store in cache
        MemoryCacheManager().set(cache_key, agents)

        return agents
