from typing import List, Any, Generator, Callable, Optional, override
from HeroAI.cache_data import CacheData
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.targeting_order import TargetingOrder
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE


class RitualistStProt(CustomBehaviorBase):
    """

    1) boon_of_creation recast before 1500ms it ends

    2) soul_twisting
         A) cast, if not has_effect
         B) if has effect & buff_time_remaining <= 5000ms, we force recast. but before let's exhaust charges (we could lose armor_of_unfeeling, but it seems fine) !
                x) try_cast_spirit_shelter [if has_soul_twisting - we don't care about spirit life]
                x) try_cast_spirit_union [if has_soul_twisting - we don't care about spirit life]
                x) try_cast_spirit_displacement [if has_soul_twisting - we don't care about spirit life]

    3) try_cast_spirit shelter / union / displacement
        A) if has_soul_twisting & effect_duration > 1200ms & spirit life < 30%

    4) armor_of_unfeeling
        should_refresh_armor_of_unfeeling is changed to True when we cast one of the spirit above
        A) if should_refresh_armor_of_unfeeling, then cast it

    """


    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)

        self.ebon_vanguard_assassin_support: CustomSkill = CustomSkill("Ebon_Vanguard_Assassin_Support")
        self.soul_twisting: CustomSkill = CustomSkill("Soul_Twisting")
        self.shelter: CustomSkill = CustomSkill("Shelter")
        self.union: CustomSkill = CustomSkill("Union")
        self.displacement: CustomSkill = CustomSkill("Displacement")  # replace by SummonSpirit once unlocked
        self.armor_of_unfeeling: CustomSkill = CustomSkill("Armor_of_Unfeeling")
        self.boon_of_creation: CustomSkill = CustomSkill("Boon_of_Creation")  # replace by Strength of honor once unlocked
        self.brutal_weapon: CustomSkill = CustomSkill("Brutal_Weapon")  # replace by Strength of honor once unlocked
        self.flesh_of_my_flesh: CustomSkill = CustomSkill("Flesh_of_My_Flesh")

        self.shelter_should_refresh_armor_of_unfeeling = False
        self.union_should_refresh_armor_of_unfeeling = False

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        result = [
            self.ebon_vanguard_assassin_support,
            self.soul_twisting,
            self.shelter,
            self.union,
            self.displacement,
            self.armor_of_unfeeling,
            self.boon_of_creation,
            self.brutal_weapon,
        ]

        return result

    @override
    def _handle_far_from_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield from custom_behavior_helpers.Actions.cast_skill_generic(self.flesh_of_my_flesh)
            yield

    @override
    def _handle_close_to_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:

            yield from custom_behavior_helpers.Actions.cast_effect_before_expiration(self.boon_of_creation, time_before_expire=1500)

            result = yield from self.__try_cast_soul_twisting()
            if result is BehaviorResult.ACTION_PERFORMED:
                continue

            result = yield from self.__try_cast_spirit(self.shelter, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.shelter_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_spirit(self.union, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_spirit(self.displacement, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_armor_of_unfeeling()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            yield from custom_behavior_helpers.Actions.cast_skill_generic(self.flesh_of_my_flesh)

            yield

    @override
    def _handle_in_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:

            yield from custom_behavior_helpers.Actions.cast_effect_before_expiration(self.boon_of_creation, time_before_expire=1500)

            result = yield from self.__try_cast_soul_twisting()
            if result is BehaviorResult.ACTION_PERFORMED:
                continue

            result = yield from self.__try_cast_spirit(self.shelter, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.shelter_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_spirit(self.union, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_spirit(self.displacement, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_armor_of_unfeeling()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            if custom_behavior_helpers.Resources.get_player_absolute_energy() > 13:
                result = yield from custom_behavior_helpers.Actions.cast_skill_generic(self.ebon_vanguard_assassin_support)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            result = yield from custom_behavior_helpers.Actions.cast_skill_generic(self.flesh_of_my_flesh)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            yield from custom_behavior_helpers.Actions.auto_attack()

            yield

    def __try_cast_armor_of_unfeeling(self) -> Generator[Any, Any, BehaviorResult]:

        should_refresh: bool = self.shelter_should_refresh_armor_of_unfeeling and self.union_should_refresh_armor_of_unfeeling

        if not should_refresh:
            return BehaviorResult.ACTION_SKIPPED

        result:BehaviorResult = yield from custom_behavior_helpers.Actions.cast_skill(self.armor_of_unfeeling)

        if result is BehaviorResult.ACTION_PERFORMED:
           self.shelter_should_refresh_armor_of_unfeeling = False
           self.union_should_refresh_armor_of_unfeeling = False

        return result

    def __try_cast_spirit(self, spirit_skill: CustomSkill, spirit_condition: Optional[Callable[[int], bool]]=None) -> Generator[Any, Any, BehaviorResult]:
       has_buff = Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.soul_twisting.skill_id)
       buff_time_remaining = GLOBAL_CACHE.Effects.GetEffectTimeRemaining(GLOBAL_CACHE.Player.GetAgentID(), self.soul_twisting.skill_id) if has_buff else 0
       if not has_buff:
           yield
           return BehaviorResult.ACTION_SKIPPED # we want to have soul twisting or nothing
       if buff_time_remaining <= 1200:
           yield
           return BehaviorResult.ACTION_SKIPPED  # about to expire

       if not custom_behavior_helpers.Resources.is_spirit_exist(within_range=Range.Spellcast, associated_to_skill=spirit_skill, condition=spirit_condition):
           result: BehaviorResult = yield from custom_behavior_helpers.Actions.cast_skill(spirit_skill)
           return result

       return BehaviorResult.ACTION_SKIPPED
    def __try_cast_soul_twisting(self) -> Generator[Any, Any, BehaviorResult]:
        has_buff = Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.soul_twisting.skill_id)

        if not has_buff:
            result: BehaviorResult = yield from custom_behavior_helpers.Actions.cast_skill(self.soul_twisting)
            return result

        buff_time_remaining = GLOBAL_CACHE.Effects.GetEffectTimeRemaining(GLOBAL_CACHE.Player.GetAgentID(), self.soul_twisting.skill_id) if has_buff else 0

        if buff_time_remaining <= 5000:
            # we want to force the re-load until no more soul_twisting
            # we could lose armor_of_unfeeling, but it seems fine

            result = yield from self.__try_cast_spirit(self.shelter, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 1) # we force
            if result is BehaviorResult.ACTION_PERFORMED:
                self.shelter_should_refresh_armor_of_unfeeling = True

            result = yield from self.__try_cast_spirit(self.union, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 1)  # we force
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True

            result = yield from self.__try_cast_spirit(self.displacement, lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 1)  # we force
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True

            return BehaviorResult.ACTION_PERFORMED

        return BehaviorResult.ACTION_SKIPPED
