import CONST
import math

class weatherManager():
    def __init__(self,startingSeason = CONST.season.EARLYSPRING) -> None:
        pass

    def getDayLightHours(self):
        day = 59
        declination = -23.45 * math.cos(360/365*(day+10))
        return declination

