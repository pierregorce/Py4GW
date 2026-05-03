from enum import IntFlag, auto

class TargetingAllyAllegiance(IntFlag):
    Ally  = auto()
    Spirit = auto()
    Pet = auto()
    Minion = auto()
    NpcInParty = auto() # npc joined in the party