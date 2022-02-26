from enum import Enum

#enum of villager AI states
class VillagerStates(Enum):
    IDLE = 1
    EATING = 2
    WORKING = 3
    HOSPITALIZED = 4
