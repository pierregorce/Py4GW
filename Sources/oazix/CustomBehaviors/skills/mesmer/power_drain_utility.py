from typing import Any, Generator, Callable, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.sortable_agent_data import SortableAgentData
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Sources.oazix.CustomBehaviors.primitives.scores.score_per_energy_definition import ScorePerEnergyDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase

class PowerDrainUtility(CustomSkillUtilityBase):

    def __init__(self,
                    event_bus: EventBus,
                    current_build: list[CustomSkill],
                    score_definition: ScorePerEnergyDefinition = ScorePerEnergyDefinition(score_nominal=40,score_boosted=99,only_cast_if_energy_below=0.85, low_mana_threshold=0.30),
                    mana_required_to_cast: int = 5,
            ) -> None:

            super().__init__(
                event_bus=event_bus,
                skill=CustomSkill("Power_Drain"),
                in_game_build=current_build,
                score_definition=score_definition, 
                mana_required_to_cast=mana_required_to_cast)
            
            self.score_definition: ScorePerEnergyDefinition = score_definition

    def detect_casting_enemies(self) -> list[SortableAgentData]:
        targets = custom_behavior_helpers.Targets.get_all_possible_enemies_ordered_by_priority_raw(
            within_range=Range.Spellcast,
            condition=lambda agent_id: 
                Agent.IsCasting(agent_id)
                and (GLOBAL_CACHE.Skill.Flags.IsSpell(Agent.GetCastingSkillID(agent_id)) or GLOBAL_CACHE.Skill.Flags.IsChant(Agent.GetCastingSkillID(agent_id))) 
                and GLOBAL_CACHE.Skill.Data.GetActivation(Agent.GetCastingSkillID(agent_id)) >= 1.00, # only skills that are longer than 1s. too much changes to fail otherwise
            sort_key=(TargetingOrder.CASTER_THEN_MELEE, ),
            range_to_count_enemies=GLOBAL_CACHE.Skill.Data.GetAoERange(self.custom_skill.skill_id)
        )
        return targets
    
    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        targets = self.detect_casting_enemies()
        if len(targets) == 0: return None
        return self.score_definition.get_score()
    
    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        targets = self.detect_casting_enemies()
        if len(targets) == 0: return BehaviorResult.ACTION_SKIPPED
        target_id = targets[0].agent_id
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=target_id)
        return result