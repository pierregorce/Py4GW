from typing import Callable

from Py4GWCoreLib import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.Player import Player
from Sources.oazix.CustomBehaviors.primitives.helpers.custom_behavior_helpers_party import CustomBehaviorHelperParty
from Sources.oazix.CustomBehaviors.primitives.helpers.target_overriding.enemy_blacklist_override import EnemyBlacklistOverride
from Sources.oazix.CustomBehaviors.primitives.helpers.target_overriding.party_leader_called_target_override import PartyLeaderCalledTargetOverride
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.enemies_within_range_scoring import AgentsWithinRangeScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.interrupt_potential_scoring import InterruptPotentialScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.target_scoring.melee_aoe_enemies_scoring import MeleeAoeEnemiesScoring
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_core import TargetingEnemyCore
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.tarteging_enemy_allegiance import TargetingEnemyAllegiance
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.targeting_core import TargetingCore
from Sources.oazix.CustomBehaviors.primitives.parties.memory_cache_manager import MemoryCacheManager


class TargetingEnemy:

    def __init__(
            self, 
            override_score_functions: list[Callable[[list[TargetingEnemyData]], list[TargetingEnemyData]]] | None = None,
            interrupt_potential_scoring: InterruptPotentialScoring | None = None,
            melee_aoe_enemies_scoring: MeleeAoeEnemiesScoring | None = None,
            agents_within_range_scoring: AgentsWithinRangeScoring | None = None,
            ):

        # default list of functions to override the score of the enemies
        # could be overriden by some botting features
        self._override_score_functions: list[Callable[[list[TargetingEnemyData]], list[TargetingEnemyData]]] = override_score_functions if override_score_functions is not None else []

        self.interrupt_potential_scoring = interrupt_potential_scoring if interrupt_potential_scoring is not None else InterruptPotentialScoring()
        self.melee_aoe_enemies_scoring = melee_aoe_enemies_scoring if melee_aoe_enemies_scoring is not None else MeleeAoeEnemiesScoring()
        self.agents_within_range_scoring = agents_within_range_scoring if agents_within_range_scoring is not None else AgentsWithinRangeScoring()

    @staticmethod
    def create() -> 'TargetingEnemy':
        return TargetingEnemy(override_score_functions=[PartyLeaderCalledTargetOverride.override, EnemyBlacklistOverride.override])

    @staticmethod
    def create_custom(
            self, 
            override_score_functions: list[Callable[[list[TargetingEnemyData]], list[TargetingEnemyData]]] | None = None,
            interrupt_potential_scoring: InterruptPotentialScoring | None = None,
            melee_aoe_enemies_scoring: MeleeAoeEnemiesScoring | None = None,
            agents_within_range_scoring: AgentsWithinRangeScoring | None = None,
        ) -> 'TargetingEnemy':
        
        return TargetingEnemy(
            override_score_functions=override_score_functions,
            interrupt_potential_scoring=interrupt_potential_scoring,
            melee_aoe_enemies_scoring=melee_aoe_enemies_scoring,
            agents_within_range_scoring=agents_within_range_scoring,
        )

    @staticmethod
    def create_with_custom_interrupt_potential_scoring(interrupt_potential_scoring: InterruptPotentialScoring) -> 'TargetingEnemy':
        return TargetingEnemy(
            override_score_functions=[EnemyBlacklistOverride.override],
            interrupt_potential_scoring=interrupt_potential_scoring)
        
    def get_enemies(
            self,

            # core
            within_range: float,
            source_agent_pos: tuple[float, float] | None = None, # if None, will use Player.GetXY()
            condition_predicate: Callable[[TargetingEnemyData], bool] | None = None,
            sort_asc_predicate: Callable[[TargetingEnemyData], tuple[float, float, float] | tuple[float, float] | float] | None = None,
            range_to_count_clustered_enemies: float | None = None,
            
            # optional extra data
            allegiance_to_include: TargetingEnemyAllegiance = TargetingEnemyAllegiance.Enemy | TargetingEnemyAllegiance.Spirit | TargetingEnemyAllegiance.Pet | TargetingEnemyAllegiance.Minion, # some skills should not be used on specific cohorts
            is_alive: bool = True, # will be false when used to corpse invocation
            is_aggressive_further_included: bool = True # will be false to interrupts for instance, when moving b4 cast is an issue

        ) -> list[TargetingEnemyData]:

        if sort_asc_predicate is None: sort_asc_predicate = lambda x: x.distance_from_player

        source_pos = source_agent_pos if source_agent_pos is not None else Player.GetXY()
        party_leader_id : int = TargetingCore().get_party_leader_id()

        agent_data_list : list[TargetingEnemyData] = TargetingEnemyCore().get_combined_enemy_targets(
            source_pos=source_pos,
            within_range=within_range,
            leader_agent_id=party_leader_id,
            allegiance_to_include=allegiance_to_include,
            include_aggressive_further=is_aggressive_further_included,
        )

        # filtering
        agent_data_list_filtered: list[TargetingEnemyData] = []

        for agent_data in agent_data_list:
            if Agent.IsAlive(agent_data.agent_id) != is_alive:
                continue

            if condition_predicate is not None and not condition_predicate(agent_data):
                continue

            agent_data_list_filtered.append(agent_data)
            
            if range_to_count_clustered_enemies is not None:
                all_enemies_ids: list[int] = AgentArray.GetEnemyArray()
                agent_data.enemy_quantity_within_range = self.agents_within_range_scoring.get_score(agent_data.agent_id, all_enemies_ids, range_to_count_clustered_enemies)
            agent_data.melee_optimised_aoe_score = self.melee_aoe_enemies_scoring.get_melee_optimised_aoe_score(agent_data.agent_id, agent_data.enemy_quantity_within_range)
            agent_data.interrupt_potential_score = self.interrupt_potential_scoring.get_score(agent_data.agent_id)

        # sorting
        agent_data_list_sorted: list[TargetingEnemyData] = agent_data_list_filtered
        agent_data_list_sorted.sort(key=sort_asc_predicate)
        
        # overriding
        agent_data_list_overriden: list[TargetingEnemyData] = agent_data_list_sorted
        for override_score_function in self._override_score_functions:
            agent_data_list_overriden = override_score_function(agent_data_list_overriden)

        # return
        return agent_data_list_overriden