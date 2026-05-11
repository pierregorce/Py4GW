from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class DamageReceivedEvent:
    target_id: int
    source_id: int
    damage_taken: int
    timestamp: float