
from Sources.oazix.CustomBehaviors.primitives.infrastructure.external_dependency_factory import ExternalDependencyFactory


class InterruptPotentialScoring:

    def __init__(self, skill_activation_min_duration_in_ms: float = 250):
        self.logger = ExternalDependencyFactory().external_logger_factory.get_logger(self.__class__.__name__)

        self.ping_ms = 70 
        self.margin_ms = 50
        self.skill_activation_min_duration_in_ms: float = skill_activation_min_duration_in_ms
        self.min_duration_for_interrupt_to_be_feasible_in_ms: float = self.skill_activation_min_duration_in_ms + self.ping_ms + self.margin_ms

    def get_score(self, agent_id: int) -> float:

        from Sources.oazix.CustomBehaviors.primitives.helpers.observers.casting.casting_observer import CastingObserver, EnemyCastingState
        casting_data: EnemyCastingState | None = CastingObserver().get_cast_data(agent_id)
        if casting_data is None: return 0.0

        if casting_data.activation_time_ms < self.skill_activation_min_duration_in_ms: return 0.0
        if casting_data.remaining_casting_time_ms < self.min_duration_for_interrupt_to_be_feasible_in_ms: return 0.0

        # 1) PRIORITY BASED ON SKILL DANGEROUSNESS
        # in near future we do want to prioritize some interruptions over others (dangerous skills for instance)

        # 2) LINAR SCORING BASED ON TIME REMAINING
        # we want to penalize skills that are almost done casting VS others where remaining time is higher.
        remaining_time_ms = casting_data.remaining_casting_time_ms
        max_remaining_time_ms = 5000
        min_remaining_time_ms = self.min_duration_for_interrupt_to_be_feasible_in_ms

        # linear function that gives 100 when the remaining time is max_remaining_time_ms and 0 when the remaining time is min_remaining_time_ms.
        score = (remaining_time_ms - min_remaining_time_ms) / (max_remaining_time_ms - min_remaining_time_ms) * 100

        return score