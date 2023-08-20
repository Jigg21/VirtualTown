from enum import Enum

class VillagerStates(Enum):
    '''enum of villager AI states'''
    IDLE = 1
    EATING = 2
    WORKING = 3
    HOSPITALIZED = 4
    READY = 5
    SLEEPING = 6
    DEAD = 7

class EventSeverity(Enum):
    '''how severe is the event'''
    NEGLIGIBLE = 0
    TRIVIAL = 1
    MINOR = 2
    STANDARD = 3
    PRESSING = 4
    MAJOR = 5
    EMERGENCY = 6

class EventTypes(Enum):
    '''enums for how events behave '''
    NULL = 0
    TEMPORARY = 1
    CONDITIONAL = 2
    INSTANT = 3

class TaskStatus(Enum):
    '''Enum of task states'''
    WAITING = 1
    STARTED = 2
    INPROGRESS = 3
    COMPLETED = 4
    FAILED = 5

class buildingClass(Enum):
    TOWNHALL = 0
    RESTAURANT = 1
    MINE = 2
    TAVERN = 3
    MISC = 4
    FARM = 5
    TRADE = 6
    GAMEHALL = 7

class season(Enum):
    EARLYSPRING = 0
    SPRING = 1
    LATESPRING = 2
    EARLYSUMMER = 3
    SUMMER = 4
    LATESUMMER = 5
    EARLYFALL = 6
    FALL = 7
    LATEFALL = 8
    EARLYWINTER = 9
    WINTER = 10
    LATEWINTER = 11

class VillageTypes(Enum):
    AGRICULTURAL = 0,
    CULTURE = 1,
    ENERGISTIC = 2,
    INDUSTRIOUS = 3,
    MILITANT = 4

class cultures(Enum):
    LIBERTARIAD = 0
    NOMAD = 1
    ROMAN = 2

class Biomes(Enum):
    LAKE = 0
    DESERT = 1
    FORREST = 2
    PLAINS = 3
    MOUNTAINS = 4


def getPythagoreanDistance(pos1,pos2):
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**.5