
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.event_bus.damage_received_event import DamageReceivedEvent
from Sources.oazix.CustomBehaviors.primitives.helpers.observers.damage_received.damage_received_time_serie import DamageReceivedTimeSerie

class DamageReceivedObserver:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DamageReceivedObserver, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.damage_received_time_serie = DamageReceivedTimeSerie()
            self.self_damage_received_time_serie = DamageReceivedTimeSerie()
            self._initialized = True

    def clear(self):
        self.damage_received_time_serie = DamageReceivedTimeSerie()
        self.self_damage_received_time_serie = DamageReceivedTimeSerie()

    def on_damage_received_event(self, damage_received_event: DamageReceivedEvent):

        if damage_received_event.damage_taken > 0: raise Exception("Damage received event with positive damage") # it's a heal
        is_self_damage = damage_received_event.target_id == damage_received_event.source_id

        # todo what about environnement dmg ?
        # check if party member.

        if is_self_damage:
            self.self_damage_received_time_serie.add_damage_packet(damage_received_event.target_id, damage_received_event.damage_taken, damage_received_event.timestamp)
        else:
            self.damage_received_time_serie.add_damage_packet(damage_received_event.target_id, damage_received_event.damage_taken, damage_received_event.timestamp)
