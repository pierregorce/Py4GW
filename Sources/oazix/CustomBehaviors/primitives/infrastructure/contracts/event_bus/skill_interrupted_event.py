from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SkillInterruptedEvent:
    agent_id: int
    skill_id: int
    timestamp: float
