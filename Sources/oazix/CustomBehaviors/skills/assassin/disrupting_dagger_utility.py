from typing import Any, Callable, Generator, override

from Py4GWCoreLib import GLOBAL_CACHE, Agent, Range, Player
from Py4GWCoreLib.Py4GWcorelib import Utils
from Sources.oazix.CustomBehaviors.primitives.behavior_state import BehaviorState
from Sources.oazix.CustomBehaviors.primitives.bus.event_bus import EventBus
from Sources.oazix.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Sources.oazix.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy_data import TargetingEnemyData
from Sources.oazix.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class DisruptingDaggerUtility(CustomSkillUtilityBase):
    def __init__(self,
    event_bus: EventBus,
    current_build: list[CustomSkill],
    score_definition: ScoreStaticDefinition = ScoreStaticDefinition(90),
    mana_required_to_cast: int = 0,
    allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
    ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Disrupting_Dagger"),
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
        
        self.score_definition: ScoreStaticDefinition = score_definition

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        if self.nature_has_been_attempted_last(previously_attempted_skills):
            return None
        else: 
            return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:

        player_position: tuple[float, float] = Player.GetXY()

        def select_target() -> int | None:
            targets = TargetingEnemy.create().get_enemies(
                within_range=Range.Spellcast.value,
                condition_predicate=lambda enemy_data:
                    Agent.IsCasting(enemy_data.agent_id) and
                    Utils.Distance(Agent.GetXY(enemy_data.agent_id), player_position) < Range.Spellcast.value * 0.4 and
                    GLOBAL_CACHE.Skill.Data.GetActivation(Agent.GetCastingSkillID(enemy_data.agent_id)) >= 0.51,
                sort_asc_predicate=lambda enemy_data: (-enemy_data.agent_count_within_range, 0 if enemy_data.is_caster else 1))
            return targets[0].agent_id if len(targets) > 0 else None

        action: Callable[[], Generator[Any, Any, BehaviorResult]] = lambda: (yield from custom_behavior_helpers.Actions.cast_skill_to_lambda(
            skill=self.custom_skill,
            select_target=select_target
        ))

        result: BehaviorResult = yield from custom_behavior_helpers.Helpers.wait_for_or_until_completion(500, action)
        return result