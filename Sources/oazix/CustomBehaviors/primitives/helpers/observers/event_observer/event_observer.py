
from dataclasses import dataclass

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.damage_received_event import DamageReceivedEvent
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.skill_interrupted_event import SkillInterruptedEvent
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.damage_received.damage_received_observer import DamageReceivedObserver
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.casting.casting_observer import CastingObserver
from Sources.oazix.CustomBehaviors.primitives.infrastructure.external_dependency_factory import ExternalDependencyFactory

class EventObserver:

    _instance = None
    _initialized = False

    def __new__(cls):
        # Prevent direct instantiation
        raise TypeError("Cannot instantiate directly. Use Singleton.get_instance()")
    
    @classmethod
    def setup_registrations(cls):
        """Static factory method to get the singleton instance"""
        if cls._instance is None:
            # Bypass __new__ by calling object.__new__
            cls._instance = object.__new__(cls)
            cls._instance.__init()
        return cls._instance
    
    def __init(self):
        """Private initialization method (called only once)"""
        if not EventObserver._initialized:
            # initialization code here
            ExternalDependencyFactory().external_event_bus.subscribe_on_damage_received_event(self.__on_damage_received_event)
            ExternalDependencyFactory().external_event_bus.subscribe_on_skill_interrupted_event(self.__on_skill_interrupted_event)
            EventObserver._initialized = True

    def __on_damage_received_event(self, damage_packet: DamageReceivedEvent):
        damage_received_event = DamageReceivedEvent(damage_packet.source_id, damage_packet.target_id, damage_packet.damage_taken, damage_packet.timestamp)
        DamageReceivedObserver().on_damage_received_event(damage_received_event)

    def __on_skill_interrupted_event(self, skill_packet: SkillInterruptedEvent):
        """Forward skill interrupt event to CastingObserver for accurate interrupt tracking."""
        CastingObserver().on_skill_interrupted_event(
            agent_id=skill_packet.agent_id,
            skill_id=skill_packet.skill_id,
            timestamp_ms=skill_packet.timestamp
        )


# EVT_DAMAGE_DEALT 
#     only for dps meter

# EVT_DAMAGE_RECEIVED
#     good for seed of life / shield of absorption

# EVT_SKILL_COMPLETED/EVT_SKILL_INTERRUPTED/EVT_SKILL_CANCELLED
#     good for the aftercast, 
#     or should we use AftercastLockEvent ??

# EVT_SKILL_ACTIVATED 
#     good for interrupt

    