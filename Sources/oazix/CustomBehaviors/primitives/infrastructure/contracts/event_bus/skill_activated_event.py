from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SkillOnTargetEvent:
    caster_id: int
    target_id: int
    timestamp: float
