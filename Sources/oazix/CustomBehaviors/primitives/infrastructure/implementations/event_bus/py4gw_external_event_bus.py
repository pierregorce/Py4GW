from typing import Callable, override

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.damage_received_event import DamageReceivedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_activated_event import SkillOnTargetEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_interrupted_event import SkillInterruptedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.external_event_bus import ExternalEventBus

class Py4GwExternalEventBus(ExternalEventBus):

    @override
    def subscribe_on_damage_received_event(self, callback:Callable[[DamageReceivedEvent], None]):
        # not implemented yet
        pass

    @override
    def subscribe_on_skill_on_target_event(self, callback:Callable[[SkillOnTargetEvent], None]):
        # not implemented yet
        pass

    @override
    def subscribe_on_skill_interrupted_event(self, callback:Callable[[SkillInterruptedEvent], None]):
        # not implemented yet
        pass



