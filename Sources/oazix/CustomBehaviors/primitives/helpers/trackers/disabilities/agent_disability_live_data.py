from Sources.oazix.CustomBehaviors.primitives.skillbars.disabilities.condition_priority import ConditionPriority
from Sources.oazix.CustomBehaviors.primitives.skillbars.disabilities.hex_prioritiy import HexPriority


from dataclasses import dataclass


@dataclass
class AgentDisabilityLiveData:
    agent_id: int | None # KEY
    account_email: str
    skillbar_name: str

    hex_priorities: list[HexPriority]
    hex_score: int # RESULT

    condition_priorities: list[ConditionPriority]
    condition_score: int # RESULT