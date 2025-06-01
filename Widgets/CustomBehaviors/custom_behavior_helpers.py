import time
from collections.abc import Generator
from typing import Any, Callable, Optional, Tuple

from HeroAI.cache_data import CacheData
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.targeting_order import TargetingOrder

cached_data = CacheData()

from Py4GWCoreLib import GLOBAL_CACHE, SkillBar, ActionQueueManager, Routines, ConsoleLog, Range, Utils, SPIRIT_BUFF_MAP, SpiritModelID, AgentArray

LOG_TO_CONSOLE:bool = True
MODULE_NAME = "Custom Combat Behavior Helpers"
DEBUG = True

class Helpers:

    @staticmethod
    def interleave_generators(*generators):
        """
        Alternate between generators in a round-robin manner.
        """
        iterators = [iter(gen) for gen in generators]
        while iterators:
            for it in iterators[:]:
                try:
                    yield next(it)
                except StopIteration:
                    iterators.remove(it)

    @staticmethod
    def wait_for(milliseconds) -> Generator[Any, Any, Any]:
        start_time = time.time()
        print(f"wait_for__{milliseconds}ms")

        while (time.time() - start_time) < milliseconds / 1000:
            yield 'wait'  # Pause and allow resumption while waiting
        return

    @staticmethod
    def delay_aftercast(skill_casted: CustomSkill) -> Generator[Any, Any, Any]:

        activation_time = GLOBAL_CACHE.Skill.Data.GetActivation(skill_casted.skill_id) * 1000
        aftercast = GLOBAL_CACHE.Skill.Data.GetAftercast(skill_casted.skill_id) * 1000
        delay = activation_time if activation_time > aftercast else aftercast
        print(f"{skill_casted.skill_name} let's wait for aftercast :{delay}ms | activation_time:{activation_time} | aftercast:{aftercast}")

        yield from Helpers.wait_for(delay + 200)  # 200ms more to really avoid double-cast

    @staticmethod
    def wait_for_or_until_completion(milliseconds, action: Callable[[], Generator[Any, Any, BehaviorResult]]) -> Generator[Any, Any, Any]:
        start_time = time.time()

        while (time.time() - start_time) < milliseconds / 1000:
            action_result: BehaviorResult = yield from action()
            if action_result == BehaviorResult.ACTION_PERFORMED:
                print(f"wait_for_or_until_completion has reached completion : {milliseconds}ms")
                return
            yield 'wait'  # Pause and allow resumption while waiting
        return

class Resources:

    @staticmethod
    def is_player_holding_an_item() -> bool:
        weapon_type, _ = GLOBAL_CACHE.Agent.GetWeaponType(GLOBAL_CACHE.Player.GetAgentID())
        if weapon_type == 0:
            return True
        return False

    @staticmethod
    def has_enough_resources(skill_casted: CustomSkill):
        player_agent_id = GLOBAL_CACHE.Player.GetAgentID()
        has_enough_adrenaline = Routines.Checks.Skills.HasEnoughAdrenaline(player_agent_id, skill_casted.skill_id)

        player_life = Resources.get_player_absolute_health()
        skill_life = GLOBAL_CACHE.Skill.Data.GetHealthCost(skill_casted.skill_id)
        has_enough_life = True if player_life * 0.95 >= skill_life else False

        energy_cost_with_effect = Resources.__get_true_cost(skill_casted)
        player_energy = get_player_absolute_energy()
        has_enough_energy = True if player_energy >= energy_cost_with_effect else False

        return has_enough_adrenaline and has_enough_life and has_enough_energy

    @staticmethod
    def __get_true_cost(skill: CustomSkill):
        '''
        should be part of core libs (fix GetEnergyCostWithEffects)
        '''

        player_agent_id = GLOBAL_CACHE.Player.GetAgentID()

        def get_attribute_level(attribute_name):
            attributes = GLOBAL_CACHE.Agent.GetAttributes(player_agent_id)
            for attr in attributes:
                if attr.GetName() == attribute_name:
                    return attr.level
            return 0

        energy_cost = Routines.Checks.Skills.GetEnergyCostWithEffects(skill.skill_id, player_agent_id)
        profession = GLOBAL_CACHE.Agent.GetProfessionNames(player_agent_id)[0]
        skill_profession = GLOBAL_CACHE.Skill.GetProfession(skill.skill_id)[1]
        skill_type = GLOBAL_CACHE.Skill.GetType(skill.skill_id)[1]

        if profession == "Dervish" and skill_type == "Enchantment":
            mysticism_level = get_attribute_level("Mysticism")
            energy_cost = round((1 - (mysticism_level * 0.04)) * energy_cost)
            return energy_cost

        if profession == "Ranger":
            expertise_level = get_attribute_level("Expertise")
            if skill_profession != "Ranger":
                if skill_type == "Attack" or skill_type == "Rituals" or GLOBAL_CACHE.Skill.skill_instance(skill.skill_id).is_touch_range:
                    energy_cost = round((1 - (expertise_level * 0.04)) * energy_cost)
                    return energy_cost

            if skill_profession == "Ranger":
                energy_cost = round((1 - (expertise_level * 0.04)) * energy_cost)
                return energy_cost

        return energy_cost

    @staticmethod
    def get_energy_percent_in_party(agent_id):
        import HeroAI.shared_memory_manager as shared_memory_manager
        shared_memory_handler = shared_memory_manager.SharedMemoryManager()

        from HeroAI.constants import MAX_NUM_PLAYERS
        for i in range(MAX_NUM_PLAYERS):
            player_data = shared_memory_handler.get_player(i)
            if player_data and player_data["IsActive"] and player_data["PlayerID"] == agent_id:
                return player_data["Energy"]
        return 1.0  # default return full energy to prevent issues

    @staticmethod
    def get_player_absolute_health() -> float:
        player_agent_id = GLOBAL_CACHE.Player.GetAgentID()
        current_heath_percent = GLOBAL_CACHE.Agent.GetHealth(player_agent_id)
        heath_max = GLOBAL_CACHE.Agent.GetMaxHealth(player_agent_id)
        current_heath = current_heath_percent * heath_max
        return current_heath

    @staticmethod
    def is_spirit_exist(
            within_range: Range,
            associated_to_skill: Optional[CustomSkill] = None,
            condition: Optional[Callable[[int], bool]] = None) -> bool:
        spirit_array = GLOBAL_CACHE.AgentArray.GetSpiritPetArray()
        spirit_array = AgentArray.Filter.ByDistance(spirit_array, GLOBAL_CACHE.Player.GetXY(), within_range.value)
        spirit_array = AgentArray.Filter.ByCondition(spirit_array, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id))
        if condition is not None:
            spirit_array = AgentArray.Filter.ByCondition(spirit_array, condition)

        if associated_to_skill is not None:
            for spirit_id in spirit_array:
                model_value = GLOBAL_CACHE.Agent.GetPlayerNumber(spirit_id)

                # Check if model_value is valid for SpiritModelID Enum
                if model_value in SpiritModelID._value2member_map_:
                    spirit_model_id = SpiritModelID(model_value)
                    if SPIRIT_BUFF_MAP.get(spirit_model_id) == associated_to_skill.skill_id:
                        return True
            return False

        return len(spirit_array) > 0

class Actions:

    @staticmethod
    def player_drop_item_if_possible() -> Generator[Any, Any, Any]:
        if not Resources.is_player_holding_an_item():
            yield
            return BehaviorResult.ACTION_SKIPPED

        from Py4GWCoreLib import UIManager
        all_ids = UIManager.GetAllChildFrameIDs(5040781, [0, 0])
        exist = UIManager.FrameExists(all_ids[0])
        if exist:
            UIManager.FrameClick(all_ids[0])
            yield from Helpers.wait_for(100)
            return BehaviorResult.ACTION_PERFORMED

        return BehaviorResult.ACTION_SKIPPED

class Targets:

    @staticmethod
    def is_player_close_to_combat() -> bool:
        enemy_id = Routines.Agents.GetNearestEnemy(Range.Spellcast.value + 250, aggressive_only=False)
        if enemy_id is not None and enemy_id > 0 and GLOBAL_CACHE.Agent.IsValid(enemy_id): return True
        return False

    @staticmethod
    def is_player_in_aggro() -> bool:
        enemy_aggressive_id = Routines.Agents.GetNearestEnemy(Range.Spellcast.value + 250, aggressive_only=True)
        if enemy_aggressive_id is not None and enemy_aggressive_id > 0 and GLOBAL_CACHE.Agent.IsValid(enemy_aggressive_id): return True

        enemy_id = Routines.Agents.GetNearestEnemy(Range.Spellcast.value, aggressive_only=False)
        if enemy_id is not None and enemy_id > 0 and GLOBAL_CACHE.Agent.IsValid(enemy_id): return True

        return False

    @staticmethod
    def is_party_in_combat() -> bool:
        # todo to implement through shared_memory
        return False

    @staticmethod
    def get_all_possible_allies_ordered_by_priority(
            within_range: Range,
            condition: Optional[Callable[[int], bool]] = None,
            sort_key: Optional[Tuple[TargetingOrder, ...]] = None,
            clustered_allies_within_range: Optional[float] = None) -> Tuple[int]:

        player_pos = GLOBAL_CACHE.Player.GetXY()
        agent_ids: list = GLOBAL_CACHE.AgentArray.GetAllyArray()

        agent_ids = AgentArray.Filter.ByCondition(agent_ids, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id))
        agent_ids = AgentArray.Filter.ByDistance(agent_ids, player_pos, within_range.value)
        if condition is not None: agent_ids = AgentArray.Filter.ByCondition(agent_ids, condition)

        def build_sortable_array(agent_id):
            agent_pos = GLOBAL_CACHE.Agent.GetXY(agent_id)
            enemy_quantity_within_aoe_range = 0

            if clustered_allies_within_range is not None:
                for other_agent_id in agent_ids:  # complexity O(n^2) !
                    if other_agent_id != agent_id and Utils.Distance(GLOBAL_CACHE.Agent.GetXY(other_agent_id), agent_pos) <= clustered_allies_within_range:
                        enemy_quantity_within_aoe_range += 1

            return {
                "agent_id": agent_id,
                "distance_from_player": Utils.Distance(agent_pos, player_pos),
                "hp": GLOBAL_CACHE.Agent.GetHealth(agent_id),
                "is_caster": GLOBAL_CACHE.Agent.IsCaster(agent_id),
                "is_melee": GLOBAL_CACHE.Agent.IsMelee(agent_id),
                "is_martial": GLOBAL_CACHE.Agent.IsMartial(agent_id),
                "clustered_foes_quantity": enemy_quantity_within_aoe_range,
                "energy": Resources.get_energy_percent_in_party(agent_id),
            }

        data_to_sort = list(map(lambda agent_id: build_sortable_array(agent_id), agent_ids))

        if not sort_key:  # If no sort_key is provided
            agent_ids_column = map(lambda entry: entry["agent_id"], data_to_sort)
            return tuple(agent_ids_column)

        # Iterate over sort_key in reverse order (apply less important sort criteria first)
        for criterion in reversed(sort_key):
            if criterion == TargetingOrder.DISTANCE_ASC:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["distance_from_player"])
            elif criterion == TargetingOrder.DISTANCE_DESC:
                data_to_sort = sorted(data_to_sort, key=lambda x: -x["distance_from_player"])
            elif criterion == TargetingOrder.HP_ASC:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["hp"])
            elif criterion == TargetingOrder.HP_DESC:
                data_to_sort = sorted(data_to_sort, key=lambda x: -x["hp"])
            elif criterion == TargetingOrder.ENERGY_ASC:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["energy"])
            elif criterion == TargetingOrder.ENERGY_DESC:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["energy"])
            elif criterion == TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC:
                data_to_sort = sorted(data_to_sort, key=lambda x: -x["clustered_foes_quantity"])
            elif criterion == TargetingOrder.CLUSTERED_FOES_QUANTITY_ASC:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["clustered_foes_quantity"])
            elif criterion == TargetingOrder.CASTER_THEN_MELEE:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["is_caster"])
            elif criterion == TargetingOrder.MELEE_THEN_CASTER:
                data_to_sort = sorted(data_to_sort, key=lambda x: x["is_melee"])
            else:
                raise ValueError(f"Invalid sorting criterion: {criterion}")

        return tuple(map(lambda entry: entry["agent_id"], data_to_sort))

    @staticmethod
    def get_first_or_default_from_allies_ordered_by_priority(
            within_range: Range,
            condition: Optional[Callable[[int], bool]] = None,
            sort_key: Optional[Tuple[TargetingOrder, ...]] = None,
            clustered_allies_within_range: Optional[float] = None) -> Optional[int]:

        allies = Targets.get_all_possible_allies_ordered_by_priority(within_range, condition, sort_key, clustered_allies_within_range)
        if len(allies) == 0: return None
        return allies[0]

class Heals:

    @staticmethod
    def is_party_damaged(within_range:Range, min_allies_count:int, less_health_than_percent:float) -> bool:

        allies = Targets.get_all_possible_allies_ordered_by_priority(
            within_range=within_range,
            condition= lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < less_health_than_percent,
            sort_key= (TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC),
            clustered_allies_within_range=None)

        if len(allies) < min_allies_count: return False
        return True

    @staticmethod
    def get_first_member_damaged(within_range: Range, less_health_than_percent: float, exclude_player:bool, condition: Optional[Callable[[int], bool]] = None) -> int | None:

        allies = Targets.get_all_possible_allies_ordered_by_priority(
            within_range=within_range,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < less_health_than_percent,
            sort_key=(TargetingOrder.HP_ASC, TargetingOrder.DISTANCE_ASC),
            clustered_allies_within_range=None)

        if exclude_player:
            allies = AgentArray.Filter.ByCondition(allies, lambda agent_id: agent_id != GLOBAL_CACHE.Player.GetAgentID())

        if condition is not None:
            allies = AgentArray.Filter.ByCondition(allies, condition)

        if len(allies) == 0: return None
        return allies[0]

#resources

@staticmethod
def get_player_absolute_energy() -> float:
    player_agent_id = GLOBAL_CACHE.Player.GetAgentID()
    current_energy_percent = GLOBAL_CACHE.Agent.GetEnergy(player_agent_id)
    energy_max = GLOBAL_CACHE.Agent.GetMaxEnergy(player_agent_id)
    current_energy = current_energy_percent * energy_max
    return current_energy

#interact

@staticmethod
def auto_attack(target_id:Optional[int]=None) -> Generator[Any, Any, Any]:

    if GLOBAL_CACHE.Agent.IsAttacking(GLOBAL_CACHE.Player.GetAgentID()):
        yield
        return

    if target_id is None:
        target_id = Routines.Agents.GetNearestEnemy(Range.Spellcast.value)

    if GLOBAL_CACHE.Agent.IsValid(target_id):
        ActionQueueManager().AddAction("ACTION", GLOBAL_CACHE.Player.ChangeTarget, target_id)
        ActionQueueManager().AddAction("ACTION", GLOBAL_CACHE.Player.Interact, target_id, False)
        GLOBAL_CACHE.Player.ChangeTarget(target_id)


        yield Helpers.wait_for(100)
    # else:
        # print(f"auto_attack target is not valid {target_id}")

#casting

@staticmethod
def cast_skill_to_lambda(skill: CustomSkill, select_target:Optional[Callable[[], int]]) -> Generator[Any, Any, BehaviorResult]:
    if not Routines.Checks.Skills.IsSkillIDReady(skill.skill_id):
        yield
        return BehaviorResult.ACTION_SKIPPED

    if not Resources.has_enough_resources(skill):
        yield
        return BehaviorResult.ACTION_SKIPPED

    target_agent_id:int|None = None

    if select_target is not None:
        selected_target = select_target()
        if selected_target is None:
            yield
            return BehaviorResult.ACTION_SKIPPED
        target_agent_id = selected_target

    if target_agent_id is not None: Routines.Sequential.Agents.ChangeTarget(target_agent_id)
    Routines.Sequential.Skills.CastSkillID(skill.skill_id)
    if DEBUG: print(f"cast_skill_to_target {skill.skill_name} to {target_agent_id}")
    yield from Helpers.delay_aftercast(skill)
    return BehaviorResult.ACTION_PERFORMED

@staticmethod
def cast_skill_to_target(skill: CustomSkill, target_agent_id: int) -> Generator[Any, Any, BehaviorResult]:
    return (yield from cast_skill_to_lambda(skill, select_target= lambda : target_agent_id))

@staticmethod
def cast_skill(skill: CustomSkill) -> Generator[Any, Any, BehaviorResult]:
    return (yield from cast_skill_to_lambda(skill, select_target=None))

@staticmethod
def cast_skill_generic(skill: CustomSkill) -> Generator[Any, Any, BehaviorResult]:

    if cached_data.combat_handler is None: print("combat_handler is None")
    if cached_data.combat_handler.skills is None:
        try:
            cached_data.combat_handler.PrioritizeSkills()
        except Exception as e:
            print(f"echec {e}")
    if cached_data.combat_handler.skills is None:
        print("combat_handler.skills is None")
        yield
        return

    def find_order():
        for index, generic_skill in enumerate(cached_data.combat_handler.skills):
            if generic_skill.skill_id == skill.skill_id:
                return index  # Returning order (1-based index)
        return -1  # Return -1 if skill_id not found
    order = find_order()

    is_ready_to_cast, target_agent_id = cached_data.combat_handler.IsReadyToCast(order)

    if not is_ready_to_cast:
        yield
        return BehaviorResult.ACTION_SKIPPED

    #option1
    if target_agent_id is not None: Routines.Sequential.Agents.ChangeTarget(target_agent_id)
    Routines.Sequential.Skills.CastSkillID(skill.skill_id)
    #option2
    # ActionQueueManager().AddAction("ACTION", SkillBar.UseSkill, skill_slot, target_agent_id)
    if DEBUG: print(f"cast_skill_to_target {skill.skill_name} to {target_agent_id}")
    yield from Helpers.delay_aftercast(skill)
    return BehaviorResult.ACTION_PERFORMED

@staticmethod
def cast_effect_before_expiration(skill: CustomSkill, time_before_expire: int) -> Generator[Any, Any, BehaviorResult]:
    if not Routines.Checks.Skills.IsSkillIDReady(skill.skill_id):
        yield
        return BehaviorResult.ACTION_SKIPPED

    if not Resources.has_enough_resources(skill):
        yield
        return BehaviorResult.ACTION_SKIPPED

    has_buff = Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), skill.skill_id)
    buff_time_remaining = GLOBAL_CACHE.Effects.GetEffectTimeRemaining(GLOBAL_CACHE.Player.GetAgentID(), skill.skill_id) if has_buff else 0
    if not has_buff or buff_time_remaining <= time_before_expire:
        skill_slot = SkillBar.GetSlotBySkillID(skill.skill_id)
        ActionQueueManager().AddAction("ACTION", SkillBar.UseSkill, skill_slot, 0)
        if DEBUG: print(f"cast_effect_before_expiration {skill.skill_name}")
        yield from Helpers.delay_aftercast(skill)
        return BehaviorResult.ACTION_PERFORMED

    yield
    return BehaviorResult.ACTION_SKIPPED

#targeting

@staticmethod
def get_first_or_default_from_enemy_ordered_by_priority(
        within_range:Range,
        condition: Optional[Callable[[int], bool]]=None,
        sort_key: Optional[Tuple[TargetingOrder, ...]]=None,
        clustered_foes_within_range: Optional[float]=None) -> Optional[int]:
        """
        Determines and retrieves a tuple of all possible enemy agents within a specified range,
        filtered by conditions, and ordered by priority based on given sorting keys.
        Ordering handles multiple criteria like distance from the player, health points, and the number of enemies within the area-of-effect (AoE) range.

        :param within_range: The maximum distance from the player to consider agents as valid targets.
        :param condition: An optional callable, taking an agent's identifier as input, that must
            return a boolean indicating whether the agent meets additional filtering criteria.
        :param sort_key: An optional tuple specifying the priority order for sorting the filtered
            enemies. Each criterion defines a sorting strategy applied sequentially.
        :param clustered_foes_within_range: A range representing the area-of-effect radius, which is used to determine
            how densely packed enemies are in the proximity of each other.

        :return: Optionally returns the identifier of the first enemy that satisfies the
        specified criteria, ordered by priority. Returns None if no enemies satisfy the criteria.
        """

        enemies = get_all_possible_enemies_ordered_by_priority(within_range, condition, sort_key, clustered_foes_within_range)
        if len(enemies) == 0: return None
        return enemies[0]

@staticmethod
def get_all_possible_enemies_ordered_by_priority(
        within_range:Range,
        condition: Optional[Callable[[int], bool]]=None,
        sort_key: Optional[Tuple[TargetingOrder, ...]]=None,
        clustered_foes_within_range: Optional[float]=None) -> Tuple[int]:
    """
    Determines and retrieves a tuple of all possible enemy agents within a specified range,
    filtered by conditions, and ordered by priority based on given sorting keys.
    Ordering handles multiple criteria like distance from the player, health points, and the number of enemies within the area-of-effect (AoE) range.

    :param within_range: The maximum distance from the player to consider agents as valid targets.
    :param condition: An optional callable, taking an agent's identifier as input, that must
        return a boolean indicating whether the agent meets additional filtering criteria.
    :param sort_key: An optional tuple specifying the priority order for sorting the filtered
        enemies. Each criterion defines a sorting strategy applied sequentially.
    :param clustered_foes_within_range: A range representing the area-of-effect radius, which is used to determine
        how densely packed enemies are in the proximity of each other.

    :return: A tuple containing the identifiers of enemy agents, ordered by the specified
        priority logic and constrained by the input conditions and ranges.
    """

    player_pos = GLOBAL_CACHE.Player.GetXY()
    agent_ids:list = GLOBAL_CACHE.AgentArray.GetEnemyArray()
    agent_ids = AgentArray.Filter.ByCondition(agent_ids, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id))
    agent_ids = AgentArray.Filter.ByDistance(agent_ids, player_pos, within_range.value)
    if condition is not None: agent_ids = AgentArray.Filter.ByCondition(agent_ids, condition)

    def build_sortable_array(agent_id):
        agent_pos = GLOBAL_CACHE.Agent.GetXY(agent_id)
        enemy_quantity_within_aoe_range = 0

        if clustered_foes_within_range is not None:
            for other_agent_id in agent_ids: # complexity O(n^2) !
                if other_agent_id != agent_id and Utils.Distance(GLOBAL_CACHE.Agent.GetXY(other_agent_id), agent_pos) <= clustered_foes_within_range:
                    enemy_quantity_within_aoe_range += 1

        return {
            "agent_id": agent_id,
            "distance_from_player": Utils.Distance(agent_pos, player_pos),
            "hp": GLOBAL_CACHE.Agent.GetHealth(agent_id),
            "is_caster": GLOBAL_CACHE.Agent.IsCaster(agent_id),
            "is_melee": GLOBAL_CACHE.Agent.IsMelee(agent_id),
            "is_martial": GLOBAL_CACHE.Agent.IsMartial(agent_id),
            "clustered_foes_quantity": enemy_quantity_within_aoe_range,
        }

    data_to_sort = list(map(lambda agent_id: build_sortable_array(agent_id), agent_ids))

    if not sort_key:  # If no sort_key is provided
        agent_ids_column = map(lambda entry: entry["agent_id"], data_to_sort)
        return tuple(agent_ids_column)

    # Iterate over sort_key in reverse order (apply less important sort criteria first)
    for criterion in reversed(sort_key):
        if criterion == TargetingOrder.DISTANCE_ASC:
            data_to_sort = sorted(data_to_sort, key=lambda x: x["distance_from_player"])
        elif criterion == TargetingOrder.DISTANCE_ASC:
            data_to_sort = sorted(data_to_sort, key=lambda x: -x["distance_from_player"])
        elif criterion == TargetingOrder.HP_ASC:
            data_to_sort = sorted(data_to_sort, key=lambda x: x["hp"])
        elif criterion == TargetingOrder.HP_DESC:
            data_to_sort = sorted(data_to_sort, key=lambda x: -x["hp"])
        elif criterion == TargetingOrder.CLUSTERED_FOES_QUANTITY_DESC:
            data_to_sort = sorted(data_to_sort, key=lambda x: -x["clustered_foes_quantity"])
        elif criterion == TargetingOrder.CLUSTERED_FOES_QUANTITY_ASC:
            data_to_sort = sorted(data_to_sort, key=lambda x: x["clustered_foes_quantity"])
        elif criterion == TargetingOrder.CASTER_THEN_MELEE:
            data_to_sort = sorted(data_to_sort, key=lambda x: x["is_caster"])
        elif criterion == TargetingOrder.MELEE_THEN_CASTER:
            data_to_sort = sorted(data_to_sort, key=lambda x: x["is_melee"])
        else:
            raise ValueError(f"Invalid sorting criterion: {criterion}")

    return tuple(map(lambda entry: entry["agent_id"], data_to_sort))