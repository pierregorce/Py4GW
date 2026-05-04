from Sources.oazix.CustomBehaviors.primitives.skillbars.disabilities.condition_priority import ConditionPriority
from Sources.oazix.CustomBehaviors.primitives.skillbars.disabilities.hex_prioritiy import HexPriority

from dataclasses import dataclass

@dataclass
class AgentDisabilityStaticData:
    account_email: str # KEY
    skillbar_name: str
    hex_priorities: list[HexPriority]
    condition_priorities: list[ConditionPriority]