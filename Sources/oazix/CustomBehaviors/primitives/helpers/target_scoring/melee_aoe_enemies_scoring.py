from dataclasses import dataclass

from Py4GWCoreLib import Agent, Player
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils

 # algorithm :
        # - either close target
        # - either clustered

        # possibilities

        # - 1 moving close == 1 moving far
        # - 1 close is always better than 1 far => YES

        # - 2 close is better than 3 far => YES
        #    - 2 close [moving] is better than 3 far => NO
        #    - 2 close [moving] is better than 3 far [moving] => YES
        #    - 2 close [not moving] is better than 3 far => YES
        #    - 2 close [not moving] is better than 3 far [not moving] => YES

        # - 2 close is better than 4 far => NO
        #    - 2 close [moving] is better than 4 far => NO
        #    - 2 close [moving] is better than 4 far [moving] => YES
        

        # - 2 close is better than 5 far => NO

        # - 3 close is better than 4 far => YES 
        # - 3 close is better than 5 far => NO
        # - 3 close is better than 6 far => NO

        # - >=4 close is better than everything far

        # if one enemy super close => can be body blocked
        #    if this one is moving ?
        

        # if moving, what to do

class MeleeAoeEnemiesScoring:

    DISTANCE_THRESHOLDS = {
            'super_close': Range.Touch.value,
            'close': Range.Adjacent.value,
            'far': Range.Spellcast.value * 1.2,
    }

    # Score matrix: [enemy_count][distance_category][is_moving]
    SCORE_MATRIX = {
        0: {
            'close': 30, 
            'mid': 20, 
            'far': 10
            },
        1: {
            'close': 120, 
            'mid': 70, 
            'far': {'moving': 40, 'stationary': 50}
            },
        2: {
            'close': {'moving': 140, 'stationary': 160}, 
            'mid': 90, 
            'far': 60
            },
        3: {
            'close': 180, 
            'mid': 120, 
            'far': 80
            },
        4: {  # 4+ range
            'close': 200, 
            'mid': 150, 
            'far': 100
            },
    }

    def __init__(self):
        pass

    def __categorize_distance(self, distance: float) -> str:
        if distance <= MeleeAoeEnemiesScoring.DISTANCE_THRESHOLDS['super_close']:
            return 'super_close'
        elif distance <= MeleeAoeEnemiesScoring.DISTANCE_THRESHOLDS['close']:
            return 'close'
        elif distance > MeleeAoeEnemiesScoring.DISTANCE_THRESHOLDS['far']:
            return 'far'
        return 'mid'
    
    def get_melee_optimised_aoe_score(self, agent_id: int, enemies_quantity_within_range: int) -> int:
        distance = Utils.Distance(Agent.GetXY(agent_id), Player.GetXY())
        is_moving = Agent.IsMoving(agent_id)
        
        distance_cat = self.__categorize_distance(distance)
        count_key = min(enemies_quantity_within_range, 4)  # 4+ treated the same
        
        # Lookup base score from matrix
        score_entry = MeleeAoeEnemiesScoring.SCORE_MATRIX[count_key][distance_cat]
        base_score = score_entry['stationary' if not is_moving else 'moving'] if isinstance(score_entry, dict) else score_entry

        return base_score