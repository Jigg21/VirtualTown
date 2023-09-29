import sys
from Utilities import CONST
import math
import random
from Utilities.ConfigReader import ConfigData as config

class WeatherAcre():
    def __init__(self,pos,temp=0,humidity=0,pressure=0) -> None:
        self.pos = pos
        self.temp = temp
        self.humidity = humidity
        self.pressure = pressure
    
    def getWeatherColor(self):
        tempColor = int((self.temp/1) * 255)
        humidColor = int((self.humidity/1) * 255)
        pressureColor = int((self.pressure/1) * 255)
        return (tempColor,pressureColor,humidColor)


class weatherManager():
    def __init__(self,startingSeason = CONST.season.EARLYSPRING) -> None:
        self.map = dict()
        #create random weather patterns
        #TODO: Make the weather be influenced by the landscape
        for x in range(0,int(config["WORLDGEN"]["WORLDSIZEX"])):
            for y in range(0,int(config["WORLDGEN"]["WORLDSIZEY"])):
                self.map[(x,y)] = WeatherAcre((x,y),temp=random.random())
        
    def getDayLightHours(self):
        day = 59
        declination = -23.45 * math.cos(360/365*(day+10))
        return declination

    def getAcre(self,x,y):
        self.map[x][y]
    
    def getAcreList(self):
        acreList = list()
        for row in self.map:
            for acre in row:
                acreList.append(acre)
        return acreList



