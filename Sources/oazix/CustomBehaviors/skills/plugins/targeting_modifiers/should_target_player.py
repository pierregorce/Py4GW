from typing import Callable, override
import PyImGui
from Py4GWCoreLib import Player
from Sources.oazix.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Sources.oazix.CustomBehaviors.primitives.skills.plugins.utility_skill_targeting_modifier import UtilitySkillTargetingModifier

class ShouldTargetPlayer(UtilitySkillTargetingModifier):
    """
    A targeting modifier that allows targeting current player or not
    """

    def __init__(self, parent_skill: CustomSkill, default_value: bool = True):
        super().__init__(parent_skill, "should_target_pets")
        
        self.parent_skill = parent_skill
        from_persistence = self.load_from_persistence(str(int(default_value)))
        self.should_target_player: bool = bool(int(from_persistence))

    @property
    @override
    def data(self) -> str:
        return str(int(self.should_target_player))
    
    @override
    def get_agent_id_filtering_predicate(self) -> Callable[[int], bool]:
        if self.should_target_player:
            return lambda agent_id: agent_id == Player.GetAgentID()
        else:
            return lambda agent_id: agent_id != Player.GetAgentID()

    @override
    def get_agent_id_ordering_predicate(self) -> Callable[[int], int]:
        return lambda agent_id: -99

    @override
    def render_debug_ui(self):
        hash_value = f"{self.plugin_name}##{self.parent_skill_name}"
        self.should_target_player = PyImGui.checkbox(f"Should Target Pets##{hash_value}", self.should_target_player)
