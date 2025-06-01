from enum import Enum

# Create an enumeration
class TargetingOrder(Enum):
    CLUSTERED_FOES_QUANTITY_ASC = 1
    CLUSTERED_FOES_QUANTITY_DESC = 2
    HP_ASC = 10
    HP_DESC = 11
    ENERGY_ASC = 15
    ENERGY_DESC = 16
    DISTANCE_ASC = 20
    DISTANCE_DESC = 21
    CASTER_THEN_MELEE = 30
    MELEE_THEN_CASTER = 31


