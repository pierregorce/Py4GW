from typing import Any, Generator, override, Optional, Callable

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Py4GWCoreLib.enums import SpiritModelID
from Widgets.CustomBehaviors import custom_behavior_helpers
from Widgets.CustomBehaviors.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.behavior_state import BehaviorState
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.templates.Common_UtilitySkills.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.templates.RitualistSoulTwistingSkills.spirit_refresh_state import SpiritRefreshState

class ProtectiveSpiritUtility(CustomSkillUtilityBase):
    def __init__(self, skill: CustomSkill, current_build: list[CustomSkill], score_definition: ScoreStaticDefinition, owned_spirit_model_id: SpiritModelID, spirit_refreshed: Callable[[], None]) -> None:
        super().__init__(skill=skill, in_game_build=current_build, score_definition=score_definition, allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.soul_twisting_skill = CustomSkill("Soul_Twisting")
        self.spirit_refreshed = spirit_refreshed
        self.score_definition: ScoreStaticDefinition = score_definition
        self.owned_spirit_model_id: SpiritModelID = owned_spirit_model_id

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
       
        # Check if we have Soul Twisting active
        has_soul_twisting = Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.soul_twisting_skill.skill_id)
        if not has_soul_twisting:
            return None  # Don't cast without Soul Twisting

        buff_time_remaining = GLOBAL_CACHE.Effects.GetEffectTimeRemaining(GLOBAL_CACHE.Player.GetAgentID(), self.soul_twisting_skill.skill_id)

        if buff_time_remaining <= 1200:  # Don't cast if Soul Twisting is about to expire
            return None

        if buff_time_remaining <= 5000:  # if less than 5 seconds, let's try to exhaust charges by force casting spirits

            if custom_behavior_helpers.Resources.is_spirit_exist(
            within_range=Range.Spellcast,
            associated_to_skill=self.custom_skill,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) < 0.80): # we only refresh low life spirits
                return self.score_definition.get_score()

        # Check if we need to cast the spirit
        if not custom_behavior_helpers.Resources.is_spirit_exist(
            within_range=Range.Spellcast,
            associated_to_skill=self.custom_skill,
            condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3):
            return self.score_definition.get_score()  # High priority if spirit doesn't exist or is low health
            
        return None  # No need to cast if spirit exists and is healthy

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        if result is BehaviorResult.ACTION_PERFORMED:
            self.spirit_refreshed()
        return result