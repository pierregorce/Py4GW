class SpiritRefreshState:
    def __init__(self):
        self._shelter_should_refresh_armor_of_unfeeling: bool = False
        self._union_should_refresh_armor_of_unfeeling: bool = False
        
    def spirits_have_been_recreated(self) -> bool:
        return self._shelter_should_refresh_armor_of_unfeeling and self._union_should_refresh_armor_of_unfeeling 

    def armor_of_unfeeling_refreshed(self):
        self._shelter_should_refresh_armor_of_unfeeling = False
        self._union_should_refresh_armor_of_unfeeling = False
        

