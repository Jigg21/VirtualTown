import numbers
from ConfigReader import ConfigData as config
from Crops import Crop
from enum import Enum
from OverseerClass import TownOverseer
import CaptainsLog
import time
import math
import Utilities
import interface as UI
import traceback
import Buildings
import Villagers
import io
import nameGenerator

#contains all ship-wide events and variables
class Ship:
    townName = ""
    townAge = -1
    townAgeReadable = ""
    villagers = []
    buildings = []
    townHall = None
    overseer = None
    bulletin = None
    def __init__(self,name):
        self.townName = name
        self.bulletin = Villagers.bulletinBoard()

    #get and set townhall
    def setTownHall(self,townHall):
        self.townHall = townHall
        self.addBuilding(townHall)
    
    def getTownHall(self):
        return self.townHall

    def getRestaurant(self):
        return self.FindBuilding(Buildings.Restaurant)
    
    #add villagers
    def addVillager (self,villager):
        self.villagers.append(villager)
    
    #add a building to the town
    def addBuilding (self,building):
        self.buildings.append(building)
    
    #find a building of a certain type
    def FindBuilding(self, targetType):
        for b in self.buildings:
            if (isinstance(b,targetType)):
                return b
 
    #disply the town in terms of villagers or buildings
    def displayVillagers(self):
        for v in self.villagers:
            print(v)
    
    #display buildings in console
    def displayBuildings(self):
        result = ""
        for b in self.buildings:
            print(b)
            if len(b.Occupants) == 0:
                print("\tNone")
            else:
                for v in b.get_occupants():
                    print('\t',str(v))
        print(result)

    #get string version of above for display
    def getBuildingDisplay(self):
        result = ""
        for b in self.buildings:
            result += b.buildingName + "\n"
            if len(b.Occupants) == 0:
                result += "\tNone\n"
            else:
                for v in b.get_occupants():
                    result += '\t' + v.vName + "\n"
        return result

    #called every tick
    def timeUpdate(self):
        #get all necccesary data
        townData = dict()
        self.townAge += 1
        self.townAgeReadable = Utilities.convertTicksToTime(self.townAge)
        townData["town"] = self
        townData["Time"] = self.townAgeReadable
        townData["VillagerList"] = self.villagers
        townData["gold"] = self.townHall.treasury
        townData["food"] = self.townHall.stockPile
        townData["BuildingString"] = self.getBuildingDisplay()
        townData["crops"] = self.FindBuilding(Buildings.Farm).crops
        townData["mine"] = self.FindBuilding(Buildings.Mine)
        townData["farm"] = self.FindBuilding(Buildings.Farm)
        townData["trade"] = self.FindBuilding(Buildings.TradeHub)
        #update the villagers and buildings
        for v in self.villagers:
            v.update()
        #New Day
        if (self.townAge%1440 == 0):
            
            CaptainsLog.newDay()
            CaptainsLog.log(Utilities.convertTicksToTime(self.townAge))
            
            for building in self.buildings:
                building.dailyUpdate(townData)
            

            
            self.overseer.designateDailyTasks(townData)




        #Draw
        if config.getboolean("VALUES","USEUI"):
            UI.update(townData)

    #initialize the overseer
    def createOverseer(self):
        self.overseer = TownOverseer(self,self.townHall,self.villagers)

    #show local time
    def displayLocalTime(self):
        print("Local Time: Y{y} D{d} {h}:{m}".format(y=math.floor(self.townAge/525600), d=math.floor(self.townAge/1440), h = math.floor(self.townAge/60)%24,m=str(self.townAge%60) if self.townAge%60 > 9 else "0"+ str(self.townAge%60) ))

def main():
    testTown = Ship("TRANSlyvania")
    townHall = Buildings.TownHall("Town Hall",False,0,testTown)
    testTown.setTownHall(townHall)
    townRestaurant = Buildings.Restaurant("Restaurant",False,1,testTown)
    townFarm = Buildings.Farm("Farm",False,2,testTown)
    townMine = Buildings.Mine("Mine",False,3,testTown)
    testTown.addBuilding(townRestaurant)
    testTown.addBuilding(townMine)
    testTown.addBuilding(townFarm) 
    testTown.addVillager(Villagers.townsperson(nameGenerator.makeName(),25,'M',townHall,testTown))
    testTown.addVillager(Villagers.townsperson(nameGenerator.makeName(),27,'F',townFarm,testTown))
    testTown.addVillager(Villagers.townsperson(nameGenerator.makeName(),37,'M',townFarm,testTown))
    townTradeHub = Buildings.TradeHub("Trade Hub",False,4,testTown)
    testTown.addBuilding(townTradeHub)
    townTavern = Buildings.Tavern("Tavern",False,5,testTown)
    testTown.addBuilding(townTavern)
    testTown.createOverseer()

    #if just speedtesting, get average speed over TESTCOUNT ticks
    if config.getboolean("DEBUG","SPEEDTEST"):
        time_start =time.time()
        for x in range(config.getint("DEBUG","TESTCOUNT")):
            testTown.timeUpdate()
        time_end = time.time()
        print("Average Time was {number}".format(number = (time_end-time_start)/config.getint("DEBUG","TESTCOUNT")))
        CaptainsLog.closeLogs()
        input("Close")
        return
    

    if config.getboolean("VALUES","USEUI"):
        UI.inititialize(testTown.townName)
    #CENTRAL FINITE CURVE
    try:
        for x in range(Utilities.convertTimeToTicks("0:10:0:20")):
            testTown.timeUpdate()
            if config.getboolean("DEBUG","VERBOSE"):
                testTown.displayLocalTime()
                testTown.displayBuildings()

            if not config.getboolean("DEBUG","INSTANT"):
                time.sleep((420/365)/config.getfloat("VALUES","TIMESPEED"))
        testTown.displayLocalTime()
        testTown.displayBuildings()
    except Exception as e:
        print(str(e))
        testTown.displayLocalTime()
        
    
    #de-initialize

    CaptainsLog.closeLogs()
    if config.getboolean("VALUES","USEUI"):
        if config.getboolean("DEBUG","INSTANT"):
            input("Close")
        UI.deinitialize()
    return

main()