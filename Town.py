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




#contains all ship-wide events and variables
class Town:
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
        self.bulletin = Buildings.bulletinBoard()

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
        #update the villagers
        for v in self.villagers:
            v.update()

        #New Day
        if (self.townAge%1440 == 0):
            #A dictionary of useful information
            CaptainsLog.newDay()
            CaptainsLog.log(Utilities.convertTicksToTime(self.townAge))
            
            townData["farm"] = self.FindBuilding(Buildings.Farm)
            self.overseer.designateDailyTasks(townData)

        #update the buildings
        for building in self.buildings:
            building.timeUpdate()

        #Draw
        if config["VALUES"]["USEUI"]:
            UI.update(townData)

        
    #initialize the overseer
    def createOverseer(self):
        self.overseer = TownOverseer(self,self.townHall,self.villagers)

    #show local time
    def displayLocalTime(self):
        print("Local Time: Y{y} D{d} {h}:{m}".format(y=math.floor(self.townAge/525600), d=math.floor(self.townAge/1440), h = math.floor(self.townAge/60)%24,m=str(self.townAge%60) if self.townAge%60 > 9 else "0"+ str(self.townAge%60) ))




def main():
    testTown = Town("Nuketown")
    townHall = Buildings.TownHall("Town Hall",False,0,testTown)
    testTown.setTownHall(townHall)
    townTavern = Buildings.Restaurant("Tavern",False,1,testTown)
    townFarm = Buildings.Farm("Farm",False,2,testTown)
    townMine = Buildings.Mine("Mine",False,3,testTown)
    testTown.addBuilding(townTavern)
    testTown.addBuilding(townMine)
    testTown.addBuilding(townFarm) 
    testTown.addVillager(Villagers.townsperson("Michael",25,'M',townHall,testTown))
    testTown.addVillager(Villagers.townsperson("Pichael",27,'F',townFarm,testTown))
    testTown.addVillager(Villagers.townsperson("Nickle",37,'M',townFarm,testTown))
    testTown.createOverseer()
    print (config.sections())
    if config.getboolean("VALUES","USEUI"):
        UI.inititialize()
    #Main Time Loop
    try:
        for x in range(Utilities.convertTimeToTicks("0:1:0:20")):
            testTown.timeUpdate()
            if config.getboolean("DEBUG","VERBOSE"):
                testTown.displayLocalTime()
                testTown.displayBuildings()

            if not config.getboolean("DEBUG","INSTANT"):
                time.sleep((420/365)/config.getfloat("VALUES","TIMESPEED"))
        testTown.displayLocalTime()
        testTown.displayBuildings()
    except Exception as e:
        print("Error!:" + str(e))
        traceback.print_exc()
        testTown.displayLocalTime()
        
    
    #de-initialize

    CaptainsLog.closeLogs()
    if config.getboolean("VALUES","USEUI"):
        if config.getboolean("DEBUG","INSTANT"):
            input("Close")
        UI.deinitialize()
    return


main()