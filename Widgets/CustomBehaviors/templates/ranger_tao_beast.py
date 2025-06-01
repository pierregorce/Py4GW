from typing import List, Any, Generator, Optional

from HeroAI.cache_data import CacheData
from Py4GWCoreLib import Routines, Range, GLOBAL_CACHE

from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.custom_behavior_base import CustomBehaviorBase
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.targeting_order import TargetingOrder

class RangerTaoBeast(CustomBehaviorBase):

    def __init__(self, cached_data: CacheData):
        super().__init__(cached_data)

        #pve
        self.together_as_one: CustomSkill = CustomSkill("Together_as_one")
        self.ebon_vanguard_assassin_support: CustomSkill = CustomSkill("Ebon_Vanguard_Assassin_Support")

        #marksmanship
        self.expert_focus: CustomSkill = CustomSkill("Expert_Focus")
        self.sundering_attack: CustomSkill = CustomSkill("Sundering_Attack")
        self.needling_shot: CustomSkill = CustomSkill("Needling_Shot")

        #beast
        self.never_rampage_alone: CustomSkill = CustomSkill("Never_Rampage_Alone")
        self.scavenger_strike: CustomSkill = CustomSkill("Scavenger_Strike")
        self.comfort_animal: CustomSkill = CustomSkill("Comfort_Animal")

    @property
    def custom_behavior_build(self) -> List[CustomSkill]:
        result = [
            self.together_as_one,
            self.expert_focus,
            self.sundering_attack,
            self.needling_shot,
            self.never_rampage_alone,
            self.scavenger_strike,
            self.comfort_animal,
            # can add one more
        ]

        return result

    def _handle_far_from_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield from custom_behavior_helpers.cast_effect_before_expiration(self.together_as_one, time_before_expire=100)
            yield

    def _handle_close_to_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:
            yield from custom_behavior_helpers.cast_effect_before_expiration(self.together_as_one, time_before_expire=100)
            yield from custom_behavior_helpers.cast_effect_before_expiration(self.never_rampage_alone, time_before_expire=100)
            yield from custom_behavior_helpers.cast_effect_before_expiration(self.expert_focus, time_before_expire=2300)
            yield

    def _handle_in_aggro(self, cached_data: CacheData) -> Generator[Any | None, Any | None, None]:
        while True:

            result = yield from custom_behavior_helpers.cast_effect_before_expiration(self.together_as_one, time_before_expire=100)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            result = yield from custom_behavior_helpers.cast_effect_before_expiration(self.never_rampage_alone, time_before_expire=100)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            result = yield from custom_behavior_helpers.cast_effect_before_expiration(self.expert_focus, time_before_expire=2300)
            if result is BehaviorResult.ACTION_PERFORMED: continue

            if custom_behavior_helpers.get_player_absolute_energy() < 8: #never_rampage_alone cost 7 for 14 expertise
                # we keep mana for buffs
                yield
                continue

            current_target:Optional[int]

            targets = custom_behavior_helpers.get_all_possible_enemies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < 0.50,
                sort_key=(TargetingOrder.HP_ASC, TargetingOrder.CASTER_THEN_MELEE, TargetingOrder.CLUSTERED_FOES_QUANTITY_ASC),
                clustered_foes_within_range=Range.Adjacent.value)
            target_half_life = next(iter(targets), None)

            if target_half_life is not None:
                current_target = target_half_life
                result = yield from custom_behavior_helpers.cast_skill_to_target(self.needling_shot, target_agent_id=target_half_life)
                if result is BehaviorResult.ACTION_PERFORMED: continue # we loop to that skill

            result = yield from custom_behavior_helpers.cast_skill_to_lambda(self.scavenger_strike, select_target=
            lambda: custom_behavior_helpers.get_first_or_default_from_enemy_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id: GLOBAL_CACHE.Agent.IsConditioned(agent_id) and GLOBAL_CACHE.Agent.GetHealth(agent_id) >= 0.50,  # if < 50% we want only needling shoot
                sort_key=(TargetingOrder.DISTANCE_ASC, TargetingOrder.HP_ASC)))
            if result is BehaviorResult.ACTION_PERFORMED: continue

            alternative_targets = custom_behavior_helpers.get_all_possible_enemies_ordered_by_priority(
                within_range=Range.Spellcast,
                condition=lambda agent_id: True,
                sort_key=(TargetingOrder.HP_ASC, TargetingOrder.CLUSTERED_FOES_QUANTITY_ASC),
                clustered_foes_within_range=Range.Adjacent.value)

            current_target = next(iter(alternative_targets), None)

            if current_target is not None:
                result = yield from custom_behavior_helpers.cast_skill_to_target(self.sundering_attack, target_agent_id=current_target)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            # generic

            for generic_skill in self.get_generic_behavior_build():
                result = yield from custom_behavior_helpers.cast_skill_generic(generic_skill)
                if result is BehaviorResult.ACTION_PERFORMED: continue

            # auto-attack

            yield from custom_behavior_helpers.auto_attack(current_target)

            yield
            continue
