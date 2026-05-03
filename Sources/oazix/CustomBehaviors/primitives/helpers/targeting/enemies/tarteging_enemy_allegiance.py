from enum import IntFlag, auto

class TargetingEnemyAllegiance(IntFlag):
    Enemy  = auto()
    Spirit = auto()
    Pet = auto()
    Minion = auto()