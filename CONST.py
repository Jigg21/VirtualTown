from enum import Enum

class VillagerStates(Enum):
    '''enum of villager AI states'''
    IDLE = 1
    EATING = 2
    WORKING = 3
    HOSPITALIZED = 4
    READY = 5
    DEAD = 6

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

