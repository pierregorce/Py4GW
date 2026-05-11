from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.damage_received_event import DamageReceivedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_activated_event import SkillOnTargetEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_interrupted_event import SkillInterruptedEvent


from abc import abstractmethod
from typing import Callable


class ExternalEventBus:

    @abstractmethod
    def subscribe_on_damage_received_event(self, callback:Callable[[DamageReceivedEvent], None]):
        pass

    @abstractmethod
    def subscribe_on_skill_on_target_event(self, callback:Callable[[SkillOnTargetEvent], None]):
        pass

    @abstractmethod
    def subscribe_on_skill_interrupted_event(self, callback:Callable[[SkillInterruptedEvent], None]):
        pass

