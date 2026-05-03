from Sources.oazix.CustomBehaviors.primitives.helpers.trackers.disabilities.agent_disability_live_data import AgentDisabilityLiveData

class DisabilitiesAlliesScoring:

    def __init__(self):
        pass

    @staticmethod
    def get_hex_score(agent_id: int) -> int:
        from Sources.oazix.CustomBehaviors.primitives.helpers.trackers.disabilities.disabilities_tracker import PartyDisabilityTracker
        live_data: AgentDisabilityLiveData | None = PartyDisabilityTracker().get_live_data_for_agent(agent_id)
        if live_data is None: return 0
        return live_data.hex_score

    @staticmethod
    def get_condition_score(agent_id: int) -> int:
        from Sources.oazix.CustomBehaviors.primitives.helpers.trackers.disabilities.disabilities_tracker import PartyDisabilityTracker
        live_data: AgentDisabilityLiveData | None = PartyDisabilityTracker().get_live_data_for_agent(agent_id)
        if live_data is None: return 0
        return live_data.condition_score