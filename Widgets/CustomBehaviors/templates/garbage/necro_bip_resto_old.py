from typing import List, Any, Generator, Callable, Optional, override
from HeroAI.cache_data import CacheData
from Py4GWCoreLib.GlobalCache.SkillbarCache import SkillbarCache
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE, Profession, UIManager, ActionQueueManager, SkillBar


class NecroBipRestoOld(CustomBehaviorBase):
    """
        necro bip/heal ;

    1) we heal first
    2) then we Blood_is_Power
    3) finally if enough mana => Great_Dwarf_Weapon

    healing logic :
    # 0) is group(3) damaged < 30% => `heal_group_emergency`
    # 1) is member damage < 30% => `heal_target_in_respect_of_skills` then `heal_target_emergency`
    # 2) is group(3) damaged < 60% => `heal_group`
    # 3) is member has a debuff => `mend_body_and_soul`
    # 4) is member damage < 90% => `heal_target_in_respect_of_skills`

    heal_group_emergency
    heal_target_in_respect_of_skills
    heal_target_emergency
    heal_group

    """

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)
        self.great_dwarf_weapon: CustomSkill = CustomSkill("Great_Dwarf_Weapon")

        self.blood_is_power: CustomSkill = CustomSkill("Blood_is_Power")
        self.blood_bond: CustomSkill = CustomSkill("Blood_Bond")

        self.spirit_light: CustomSkill = CustomSkill("Spirit_Light")
        self.soothing_memories: CustomSkill = CustomSkill("Soothing_Memories")
        self.mend_body_and_soul: CustomSkill = CustomSkill("Mend_Body_and_Soul")
        self.protective_was_kaolai: CustomSkill = CustomSkill("Protective_Was_Kaolai")
        self.breath_of_the_great_dwarf: CustomSkill = CustomSkill("Breath_of_the_Great_Dwarf")

        self.sacrifice_life_limit_percent: float = 0.55
        self.sacrifice_life_limit_absolute: float = 300

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        result = [
            self.great_dwarf_weapon,

            # self.blood_is_power,
            # self.blood_bond,

            # self.spirit_light,
            # self.soothing_memories,
            # self.mend_body_and_soul,
            # self.protective_was_kaolai,
            # self.breath_of_the_great_dwarf,
        ]

        return result

    @override
    def _handle_far_from_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield
            result = yield from self.__healing_logic()
            if result is BehaviorResult.ACTION_PERFORMED: continue
            yield

    @override
    def _handle_close_to_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield
            # simple logic
            # we heal first
            # then we Blood_is_Power
            # finally if enough mana => Great_Dwarf_Weapon

            result = yield from self.__healing_logic()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            result = yield from self.__try_great_blood_is_power()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            # we don't auto-attack b/c of ashes we hold.
            yield

    @override
    def _handle_in_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield
            # simple logic
            # we heal first
            # then we Blood_is_Power
            # finally if enough mana => Great_Dwarf_Weapon

            result = yield from self.__healing_logic()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            result = yield from self.__try_great_blood_is_power()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            if custom_behavior_helpers.Resources.get_player_absolute_energy() > 15: # we keep mana for healing first
                result = yield from self.__try_great_dwarf_weapon()
                if result is BehaviorResult.ACTION_PERFORMED: continue

                result = yield from custom_behavior_helpers.Actions.cast_skill_to_lambda(
                    skill= self.blood_bond,
                    select_target= lambda: custom_behavior_helpers.Targets.get_first_or_default_from_enemy_ordered_by_priority(
                        within_range=Range.Spellcast,
                        condition= lambda agent_id: agent_id != GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.4,
                        sort_key=(TargetingOrder.DISTANCE_ASC, TargetingOrder.HP_ASC)))

            # we don't auto-attack b/c of ashes we hold.
            #no generic skills in that build
            yield

    def __try_great_dwarf_weapon(self) -> Generator[Any, Any, BehaviorResult]:

        allowed_classes = [Profession.Assassin.value, Profession.Ranger.value]
        allowed_agent_names = ["to_be_implemented"]

        from HeroAI.utils import CheckForEffect

        result: BehaviorResult = yield from custom_behavior_helpers.Actions.cast_skill_to_lambda(
            skill=self.great_dwarf_weapon,
            select_target=lambda: custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id: agent_id != GLOBAL_CACHE.Player.GetAgentID() and GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and not CheckForEffect(agent_id, self.great_dwarf_weapon.skill_id),
                sort_key=(TargetingOrder.DISTANCE_DESC, TargetingOrder.CASTER_THEN_MELEE),
                range_to_count_enemies=None,
                range_to_count_allies=None),
        )

        return result

    def __try_great_blood_is_power(self) -> Generator[Any, Any, BehaviorResult]:

        if custom_behavior_helpers.Resources.get_player_absolute_health() < self.sacrifice_life_limit_absolute or GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) <= self.sacrifice_life_limit_percent:
            yield
            return BehaviorResult.ACTION_SKIPPED

        allowed_classes = [Profession.Mesmer.value, Profession.Ritualist.value]
        allowed_agent_names = ["to_be_implemented"]

        from HeroAI.utils import CheckForEffect

        result: BehaviorResult = yield from custom_behavior_helpers.Actions.cast_skill_to_lambda(
            skill=self.blood_is_power,
            select_target=lambda: custom_behavior_helpers.Targets.get_first_or_default_from_allies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id:
                    agent_id != GLOBAL_CACHE.Player.GetAgentID() and
                    custom_behavior_helpers.Resources.get_energy_percent_in_party(agent_id) < 0.40 and
                    GLOBAL_CACHE.Agent.GetProfessionIDs(agent_id)[0] in allowed_classes and
                    not CheckForEffect(agent_id, self.blood_is_power.skill_id),
                sort_key=(TargetingOrder.ENERGY_ASC, TargetingOrder.DISTANCE_ASC),
                range_to_count_enemies=None,
                range_to_count_allies=None),
        )

        yield
        return result

    # --- healing logic

    def __healing_logic(self) -> Generator[Any, Any, BehaviorResult]:

        # move close to spirit...

        # healing logic :
        # 0) is group(3) damaged < 30%
        # 1) is member damage < 30%
        # 2) is group(3) damaged < 60%
        # 3) is member has a debuff
        # 4) is member damage < 90%

        # how do we deal with BIP, that sacrifice life
        # we can heal him same i suppose, is it less prio ?

        # ------- 1) is group(3) damaged < 40% [with player]

        if custom_behavior_helpers.Heals.is_party_damaged(within_range=Range.Spirit, min_allies_count=3, less_health_than_percent=0.4):
            result = yield from self.heal_group_emergency()
            if result is BehaviorResult.ACTION_PERFORMED: return result

        # ------- 2) is member damage < 40% [with player]

        first_member_damaged: int | None = custom_behavior_helpers.Heals.get_first_member_damaged(within_range=Range.Spirit, less_health_than_percent=0.4, exclude_player=False)
        if first_member_damaged is not None:
            result = yield from self.heal_target_in_respect_of_skills(first_member_damaged)
            if result is BehaviorResult.ACTION_PERFORMED: return result

            result = yield from self.heal_target_emergency(first_member_damaged)
            if result is BehaviorResult.ACTION_PERFORMED: return result

        # ------- 3) is group(3) damaged < 60% [with player]

        if custom_behavior_helpers.Heals.is_party_damaged(within_range=Range.Spirit, min_allies_count=3, less_health_than_percent=0.6):
            # todo bip before a party-heal to optimize yield (if enough health)
            result = yield from self.heal_group()
            if result is BehaviorResult.ACTION_PERFORMED: return result

        # ------- 4) shatter debufs [with player]

        first_member_with_x: int | None = custom_behavior_helpers.Heals.get_first_member_damaged(
            within_range=Range.Spirit,
            less_health_than_percent=0.9,
            exclude_player=True,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.IsConditioned(agent_id) < 0.95)
        if first_member_with_x is not None and custom_behavior_helpers.Resources.is_spirit_exist(within_range=Range.Earshot):
            result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.mend_body_and_soul, target_agent_id=first_member_damaged)
            if result is BehaviorResult.ACTION_PERFORMED: return result

        # ------- 4) is member damage < 60% [with player]

        first_member_damaged: int | None = custom_behavior_helpers.Heals.get_first_member_damaged(within_range=Range.Spirit, less_health_than_percent=0.6, exclude_player=False)
        if first_member_damaged is not None:
            result = yield from self.heal_target_in_respect_of_skills(first_member_damaged)
            if result is BehaviorResult.ACTION_PERFORMED: return result

        return BehaviorResult.ACTION_SKIPPED

    def heal_target_in_respect_of_skills(self, target) -> Generator[Any, Any, BehaviorResult]:
        if GLOBAL_CACHE.Agent.IsConditioned(target) and custom_behavior_helpers.Resources.is_spirit_exist(within_range=Range.Earshot):
            result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.mend_body_and_soul, target_agent_id=target)
            if result is BehaviorResult.ACTION_PERFORMED: return result
        elif custom_behavior_helpers.Resources.is_spirit_exist(within_range=Range.Earshot):
            result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.spirit_light, target_agent_id=target)
            if result is BehaviorResult.ACTION_PERFORMED: return result
        elif custom_behavior_helpers.Resources.is_player_holding_an_item():
            result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.soothing_memories, target_agent_id=target)
            if result is BehaviorResult.ACTION_PERFORMED: return result
        elif not custom_behavior_helpers.Resources.is_player_holding_an_item():
            result = yield from custom_behavior_helpers.Actions.cast_skill(self.protective_was_kaolai)
            if result is BehaviorResult.ACTION_PERFORMED: return result

        return BehaviorResult.ACTION_SKIPPED

    def heal_target_emergency(self, target) -> Generator[Any, Any, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.mend_body_and_soul, target_agent_id=target)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.soothing_memories, target_agent_id=target)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.breath_of_the_great_dwarf, target_agent_id=target)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.protective_was_kaolai, target_agent_id=target)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        result = yield from custom_behavior_helpers.Actions.player_drop_item_if_possible()
        if result is BehaviorResult.ACTION_PERFORMED: return result

        return BehaviorResult.ACTION_SKIPPED

    def heal_group(self) -> Generator[Any, Any, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.protective_was_kaolai)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        result = yield from custom_behavior_helpers.Actions.cast_skill(self.breath_of_the_great_dwarf)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        return BehaviorResult.ACTION_SKIPPED

    def heal_group_emergency(self) -> Generator[Any, Any, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.protective_was_kaolai)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        result = yield from custom_behavior_helpers.Actions.cast_skill(self.breath_of_the_great_dwarf)
        if result is BehaviorResult.ACTION_PERFORMED: return result

        yield from custom_behavior_helpers.Actions.player_drop_item_if_possible()
        if result is BehaviorResult.ACTION_PERFORMED: return result

        return BehaviorResult.ACTION_SKIPPED