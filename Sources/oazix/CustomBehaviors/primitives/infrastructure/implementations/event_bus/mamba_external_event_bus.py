from typing import Callable, override

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.damage_received_event import DamageReceivedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_activated_event import SkillOnTargetEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_interrupted_event import SkillInterruptedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.external_event_bus import ExternalEventBus

from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.logging.mamba_external_logger_factory import MambaExternalLoggerFactory
from mamba.bridge.events import DamageEvent, SkillOnTargetEvent as MambaSkillOnTargetEvent, SkillInterruptedEvent as MambaSkillInterruptedEvent, SkillOnTargetEvent
from mamba.runtime import context
from mamba.runtime.event_bus import EventBus

class MambaExternalEventBus(ExternalEventBus):

    def __init__(self):
        super().__init__()
        self.logger = MambaExternalLoggerFactory().get_logger(self.__class__.__name__)
        self.logger.error("MambaExternalEventBus (infrastructure/implementations) initialized")

    @override
    def subscribe_on_damage_received_event(self, callback:Callable[[DamageReceivedEvent], None]):
        bus: EventBus = context.event_bus()
        if bus is not None:
            def on_damage_received_event(e: DamageEvent) -> None:
                self.logger.information(f"Damage event received: {e}")
                if e.value < 0:
                    callback(DamageReceivedEvent(e.source_id, e.target_id, e.value, e.timestamp_ms))

            subscription = bus.subscribe(DamageEvent, on_damage_received_event)
            self.logger.information(f"Subscribed to DamageEvent with subscription: {subscription}")

    @override
    def subscribe_on_skill_on_target_event(self, callback:Callable[[SkillOnTargetEvent], None]):
        self.logger.error(f"subscribe_on_skill_on_target_event called")
        bus: EventBus = context.event_bus()
        self.logger.error(f"Event bus: {bus}")
        if bus is not None:
            def on_skill_on_target_event(e: MambaSkillOnTargetEvent) -> None:
                self.logger.error(f"Skill on target event received: {e}")
                callback(SkillOnTargetEvent(caster_id=e.caster_id, target_id=e.target_id, timestamp=e.timestamp_ms))

            subscription = bus.subscribe(MambaSkillOnTargetEvent, on_skill_on_target_event)
            self.logger.error(f"Subscribed to SkillOnTargetEvent with subscription: {subscription}")

    @override
    def subscribe_on_skill_interrupted_event(self, callback:Callable[[SkillInterruptedEvent], None]):
        bus: EventBus = context.event_bus()
        if bus is not None:
            def on_skill_interrupted_event(e: MambaSkillInterruptedEvent) -> None:
                self.logger.information(f"Skill interrupted event received: {e}")
                callback(SkillInterruptedEvent(e.agent_id, e.skill_id, e.timestamp_ms))

            subscription = bus.subscribe(MambaSkillInterruptedEvent, on_skill_interrupted_event)
            self.logger.information(f"Subscribed to SkillInterruptedEvent with subscription: {subscription}")




