from typing import Callable

from Py4GWCoreLib import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.agents_within_range_scoring import AgentsWithinRangeScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_allegiance import TargetingAllyAllegiance
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_data import TargetingAllyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.allies.targeting_ally_core import TargetingAllyCore

class TargetingAlly:

    _instance = None
    
    def __init__(
            self,
            override_score_functions: list[Callable[[list[TargetingAllyData]], list[TargetingAllyData]]] | None = None,
        ):
        self._override_score_functions: list[Callable[[list[TargetingAllyData]], list[TargetingAllyData]]] = override_score_functions if override_score_functions is not None else []

    @staticmethod
    def create(
            override_score_functions: list[Callable[[list[TargetingAllyData]], list[TargetingAllyData]]] | None = None,
        ) -> 'TargetingAlly':
        return TargetingAlly(override_score_functions=override_score_functions)

    def get_allies(
        self,

        # core
        within_range: float,
        source_agent_pos: tuple[float, float] | None = None, # if None, will use Player.GetXY()
        condition_predicate: Callable[[int], bool] | None = None,
        sort_asc_predicate: Callable[[TargetingAllyData], tuple[float, float] | float] | None = None,

        range_to_count_clustered_enemies: float | None = None,
        range_to_count_clustered_allies: float | None = None,
        range_to_count_clustered_anemies_and_allies: float | None = None,

        # optional extra data
        allegiance_to_include: TargetingAllyAllegiance = TargetingAllyAllegiance.Ally, # TargetingAllyAllegiance.Spirit | TargetingAllyAllegiance.Pet | TargetingAllyAllegiance.Minion # some skills should not be used on specific cohorts
        is_alive: bool = True, # will be used for resurrection skills
    ) -> list[TargetingAllyData]:
        
        if sort_asc_predicate is None: sort_asc_predicate = lambda x: x.distance_from_player

        agent_data_list : list[TargetingAllyData] = TargetingAllyCore().get_combined_ally_targets(
            source_pos=source_agent_pos,
            within_range=within_range,
            allegiance_to_include=allegiance_to_include,
        )

        # filtering
        agent_data_list_filtered: list[TargetingAllyData] = []

        for agent_data in agent_data_list:

            if Agent.IsAlive(agent_data.agent_id) != is_alive:
                continue

            if condition_predicate is not None and not condition_predicate(agent_data.agent_id):
                continue

            agent_data_list_filtered.append(agent_data)
            
            if range_to_count_clustered_enemies is not None:
                all_enemies_ids: list[int] = AgentArray.GetEnemyArray()
                agent_data.enemy_quantity_within_range = AgentsWithinRangeScoring().get_score(agent_data.agent_id, all_enemies_ids, range_to_count_clustered_enemies)
            if range_to_count_clustered_allies is not None:
                all_allies_ids: list[int] = AgentArray.GetAllyArray()
                agent_data.ally_quantity_within_range = AgentsWithinRangeScoring().get_score(agent_data.agent_id, all_allies_ids, range_to_count_clustered_allies)
            if range_to_count_clustered_anemies_and_allies is not None:
                all_agent_ids: list[int] = AgentArray.GetAgentArray()
                agent_data.anemy_and_ally_quantity_within_range = AgentsWithinRangeScoring().get_score(agent_data.agent_id, all_agent_ids, range_to_count_clustered_anemies_and_allies)
                
        # sorting
        agent_data_list_sorted: list[TargetingAllyData] = agent_data_list_filtered
        agent_data_list_sorted.sort(key=sort_asc_predicate)

        # overriding
        agent_data_list_overriden: list[TargetingAllyData] = agent_data_list_sorted
        for override_score_function in self._override_score_functions:
            agent_data_list_overriden = override_score_function(agent_data_list_overriden)

        return agent_data_list_overriden