import sys
import CONST
import math
import random
from ConfigReader import ConfigData as config


class WeatherAcre():
    def __init__(self,pos,temp=0,humidity=0,pressure=0) -> None:
        self.pos = pos
        self.temp = 0
        self.humidity = 0
        self.pressure = 0
    
    def getWeatherColor(self):
        if self.temp > .5:
            return "#30e351"
        else:
            return "#30b9e3"
import random

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
        for x in range(0,int(config["WORLDGEN"]["WORLDSIZE"])):
            for y in range(0,int(config["WORLDGEN"]["WORLDSIZE"])):
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



