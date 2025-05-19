from typing import List, Any, Generator, Callable, Optional
from HeroAI.cache_data import CacheData
from HeroAI.custom_combat_behavior import custom_combat_behavior_helpers, behavior_result
from HeroAI.custom_combat_behavior.behavior_result import BehaviorResult
from HeroAI.custom_combat_behavior.custom_combat_behavior_base import CustomCombatBehaviorBase
from Py4GWCoreLib import Agent, Routines, Range, Effects, Player, SkillBar

class RitualistStProt(CustomCombatBehaviorBase):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)

        self.ebon_vanguard_assassin_support: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Ebon_Vanguard_Assassin_Support")
        self.soul_twisting: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Soul_Twisting")
        self.shelter: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Shelter")
        self.union: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Union")
        self.displacement: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Displacement")  # replace by SummonSpirit once unlocked
        self.armor_of_unfeeling: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Armor_of_Unfeeling")
        self.boon_of_creation: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Boon_of_Creation")  # replace by Strength of honor once unlocked
        # self.brutal_weapon: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Brutal_Weapon", )  # replace by Great_Dwarf_Weapon once unlocked
        self.flesh_of_my_flesh: CustomCombatBehaviorBase.CustomSkill = CustomCombatBehaviorBase.CustomSkill("Flesh_of_My_Flesh")

        self.shelter_should_refresh_armor_of_unfeeling = False
        self.union_should_refresh_armor_of_unfeeling = False

    @property
    def custom_behavior_build(self) -> List[CustomCombatBehaviorBase.CustomSkill]:
        result = [
            self.ebon_vanguard_assassin_support,
            self.soul_twisting,
            self.shelter,
            self.union,
            self.displacement,
            self.armor_of_unfeeling,
            self.boon_of_creation,
            self.flesh_of_my_flesh,
        ]

        return result

    def _handle_out_of_combat(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield from custom_combat_behavior_helpers.cast_skill_generic(self.flesh_of_my_flesh)

            if Routines.Agents.GetNearestEnemy(Range.Spirit.value) is not None:
                yield from custom_combat_behavior_helpers.cast_effect_before_expiration(self.boon_of_creation, time_before_expire=1500)
            yield

    def _handle_combat(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:

            if Routines.Agents.GetNearestEnemy(Range.Spirit.value) is not None:
                yield from custom_combat_behavior_helpers.cast_effect_before_expiration(self.boon_of_creation, time_before_expire=1500)

            result = yield from self.__try_cast_soul_twisting()
            if result is BehaviorResult.ACTION_PERFORMED:
                continue

            result = yield from self.__try_cast_spirit(self.shelter, lambda agent_id: Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.shelter_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_spirit(self.union, lambda agent_id: Agent.GetHealth(agent_id) > 0.3)
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True
                continue

            result = yield from self.__try_cast_armor_of_unfeeling()
            if result is BehaviorResult.ACTION_PERFORMED: continue

            if custom_combat_behavior_helpers.get_player_absolute_energy() > 13:
                result = yield from custom_combat_behavior_helpers.cast_skill_generic(self.ebon_vanguard_assassin_support)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            result = yield from custom_combat_behavior_helpers.cast_skill_generic(self.flesh_of_my_flesh)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            yield from custom_combat_behavior_helpers.auto_attack()

            yield

    def __try_cast_armor_of_unfeeling(self) -> Generator[Any, Any, BehaviorResult]:

        should_refresh: bool = self.shelter_should_refresh_armor_of_unfeeling and self.union_should_refresh_armor_of_unfeeling

        if not should_refresh:
            return BehaviorResult.ACTION_SKIPPED

        result:BehaviorResult = yield from custom_combat_behavior_helpers.cast_skill(self.armor_of_unfeeling)

        if result is BehaviorResult.ACTION_PERFORMED:
           self.shelter_should_refresh_armor_of_unfeeling = False
           self.union_should_refresh_armor_of_unfeeling = False

        return result

    def __try_cast_spirit(self, spirit_skill: CustomCombatBehaviorBase.CustomSkill, spirit_condition: Optional[Callable[[int], bool]]=None) -> Generator[Any, Any, BehaviorResult]:
       has_buff = Routines.Checks.Effects.HasBuff(Player.GetAgentID(), self.soul_twisting.skill_id)
       buff_time_remaining = Effects.GetEffectTimeRemaining(Player.GetAgentID(), self.soul_twisting.skill_id) if has_buff else 0
       if not has_buff:
           yield
           return BehaviorResult.ACTION_SKIPPED # we want to have soul twisting or nothing
       if buff_time_remaining <= 1200:
           yield
           return BehaviorResult.ACTION_SKIPPED  # about to expire

       if not custom_combat_behavior_helpers.is_spirit_exist(spirit_skill, spirit_condition):
           result: BehaviorResult = yield from custom_combat_behavior_helpers.cast_skill(spirit_skill)
           return result

       return BehaviorResult.ACTION_SKIPPED

    def __try_cast_soul_twisting(self) -> Generator[Any, Any, BehaviorResult]:
        has_buff = Routines.Checks.Effects.HasBuff(Player.GetAgentID(), self.soul_twisting.skill_id)

        if not has_buff:
            result: BehaviorResult = yield from custom_combat_behavior_helpers.cast_skill(self.soul_twisting)
            return result

        buff_time_remaining = Effects.GetEffectTimeRemaining(Player.GetAgentID(), self.soul_twisting.skill_id) if has_buff else 0

        if buff_time_remaining <= 5000:
            # we want to force the re-load until no more soul_twisting
            # we could lose armor_of_unfeeling, but it seems fine

            result = yield from self.__try_cast_spirit(self.shelter, lambda agent_id: Agent.GetHealth(agent_id) > 1) # we force
            if result is BehaviorResult.ACTION_PERFORMED:
                self.shelter_should_refresh_armor_of_unfeeling = True

            result = yield from self.__try_cast_spirit(self.union, lambda agent_id: Agent.GetHealth(agent_id) > 1)  # we force
            if result is BehaviorResult.ACTION_PERFORMED:
                self.union_should_refresh_armor_of_unfeeling = True

            return BehaviorResult.ACTION_PERFORMED

        return BehaviorResult.ACTION_SKIPPED