import logging
from typing import Callable, override

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.damage_received_event import DamageReceivedEvent as CB_DamageReceivedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_activated_event import SkillActivatedEvent as CB_SkillActivatedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_interrupted_event import SkillInterruptedEvent as CB_SkillInterruptedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.external_event_bus import ExternalEventBus

from mamba.bridge.events import DamageEvent as MambaDamageEvent, SkillActivatedEvent as MambaSkillActivatedEvent, SkillInterruptedEvent as MambaSkillInterruptedEvent
from mamba.runtime import context
from mamba.runtime.event_bus import EventBus

class MambaExternalEventBus(ExternalEventBus):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.error("MambaExternalEventBus initialized")

    @override
    def subscribe_on_damage_received_event(self, callback:Callable[[CB_DamageReceivedEvent], None]):
        bus: EventBus = context.event_bus()
        if bus is not None:
            def on_damage_received_event(e: MambaDamageEvent) -> None:
                self.logger.info(f"Damage event received: {e}")
                if e.value < 0:
                    callback(CB_DamageReceivedEvent(e.source_id, e.target_id, e.value, e.timestamp_ms))

            subscription = bus.subscribe(MambaDamageEvent, on_damage_received_event)
            self.logger.info(f"Subscribed to DamageReceivedEvent with subscription: {subscription}")

    @override
    def subscribe_on_skill_activated_event(self, callback:Callable[[CB_SkillActivatedEvent], None]):
        self.logger.error(f"subscribe_on_skill_activated_event: {bus}")
        bus: EventBus = context.event_bus()
        if bus is not None:
            def on_skill_activated_event(e: MambaSkillActivatedEvent) -> None:
                self.logger.error(f"Skill activated event received: {e}")
                if e.skill_id == 0:
                    self.logger.error(f"Skill id is 0, skipping")
                    return
                callback(CB_SkillActivatedEvent(e.agent_id, e.skill_id, e.timestamp_ms))

            subscription = bus.subscribe(MambaSkillActivatedEvent, on_skill_activated_event)
            self.logger.error(f"Subscribed to SkillActivatedEvent with subscription: {subscription}")

    @override
    def subscribe_on_skill_interrupted_event(self, callback:Callable[[CB_SkillInterruptedEvent], None]):
        bus: EventBus = context.event_bus()
        if bus is not None:
            def on_skill_interrupted_event(e: MambaSkillInterruptedEvent) -> None:
                self.logger.info(f"Skill interrupted event received: {e}")
                if e.skill_id == 0:
                    self.logger.error(f"Skill id is 0, skipping")
                    return
                callback(CB_SkillInterruptedEvent(e.agent_id, e.skill_id, e.timestamp_ms))

            subscription = bus.subscribe(MambaSkillInterruptedEvent, on_skill_interrupted_event)
            self.logger.info(f"Subscribed to SkillInterruptedEvent with subscription: {subscription}")





