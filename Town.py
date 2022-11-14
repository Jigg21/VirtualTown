from ConfigReader import ConfigData as config
from OverseerClass import TownOverseer
import CaptainsLog
import time
import math
import Utilities
import interface as UI
import traceback
import Buildings
import Villagers
import traceback
import nameGenerator
import ShipEvents
#contains all ship-wide events and variables
class Ship:
    def __init__(self,name):
        self.townName = name
        
        #basic town information
        self.townName = ""
        self.townAge = -1
        #current ship temperature
        self.distanceToSun = 50
        #string representing the town age
        self.townAgeReadable = ""
        self.cargo = {}
        #the town objects
        self.villagers = []
        self.buildings = []
        self.townHall = None
        self.overseer = None
        self.treasury = 1000
        self.bulletin = Villagers.bulletinBoard(self)
        self.eventHandler = ShipEvents.EventHandler()


    
    def addTreasury(self,amount):
        self.treasury += amount
        CaptainsLog.logResource("Gold",amount)
    
    def spendTreasury(self,amount,acceptIncomplete = False):
        if self.treasury > amount:
            self.treasury -= amount
            CaptainsLog.logResource("Gold",-1*amount)
            return True
        elif acceptIncomplete:
            CaptainsLog.logResource("Gold",-1*self.treasury)
            self.treasury = 0
            return True
        return False

    #getters and setters
    def setTownHall(self,townHall):
        self.townHall = townHall
        self.addBuilding(townHall)
    
    def getTownHall(self):
        return self.townHall

    def getRestaurant(self):
        return self.FindBuilding(Buildings.Restaurant)
    
    def getShipTemp(self):
        '''returns the current temperature inside the ship'''
        return (100-self.distanceToSun)/100

    def addItemtoCargo(self, item, quantity):
        '''adds an item to cargo'''
        if item in self.cargo.keys():
            self.cargo[item] += quantity
        else:
            self.cargo[item] = quantity

    def hasEnoughItem(self,item,quantity):
        '''checks if the ship has enough of an item in the cargo'''
        if item in self.cargo.keys():
            return self.cargo[item] >= quantity
        else:
            return False
    
    def getCargoCount(self,item):
        '''get how much of an item is in the cargo'''
        if item in self.cargo.keys():
            return self.cargo[item]
        else:
            return 0

    def removeCargo(self,item,quantity):
        '''remove a quanity of item from cargo'''
        if item in self.cargo.keys():
            self.cargo[item] -= quantity
            if self.cargo[item] < 0:
                self.cargo[item] =  0
        else:
            return False
    
    def getCargoList(self):
        '''get a list of all the cargo onship'''
        cargoList = list()
        for cargoItem in self.cargo.keys():
            if self.cargo[cargoItem] > 0:
                cargoList.append(cargoItem)
        return cargoList
       
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

    def getBuildingDisplay(self):
        '''get string representation of buildings for display'''
        result = ""
        for b in self.buildings:
            result += b.buildingName + "\n"
            if len(b.Occupants) == 0:
                result += "\tNone\n"
            else:
                for v in b.get_occupants():
                    result += '\t' + v.vName + "\n"
        return result

    def timeUpdate(self):
        '''called every tick'''
        #get all necccesary data
        townData = dict()
        self.townAge += 1
        self.townAgeReadable = Utilities.convertTicksToTime(self.townAge)
        townData["town"] = self
        townData["Time"] = self.townAgeReadable
        townData["Cycle"] = self.townAge
        townData["VillagerList"] = self.villagers
        townData["gold"] = self.treasury
        townData["BuildingString"] = self.getBuildingDisplay()
        townData["crops"] = self.FindBuilding(Buildings.Farm).crops
        townData["mine"] = self.FindBuilding(Buildings.Mine)
        townData["farm"] = self.FindBuilding(Buildings.Farm)
        townData["trade"] = self.FindBuilding(Buildings.TradeHub)
        townData["temp"] = self.getShipTemp()
        townData["cargo"] = self.cargo
        townData["eventHandler"] = self.eventHandler
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

        self.eventHandler.update(townData)
        #Draw
        if config.getboolean("VALUES","USEUI"):
            UI.update(townData)

    def createOverseer(self):
        '''initialize the overseer'''
        self.overseer = TownOverseer(self,self.townHall,self.villagers)

    def isViable(self):
        '''is the town viable (are there any villagers alive)'''
        for v in self.villagers:
            if v.checkAlive():
                return True
        return False
    
    #show local time
    def displayLocalTime(self):
        print("Local Time: Y{y} D{d} {h}:{m}".format(y=math.floor(self.townAge/525600), d=math.floor(self.townAge/1440), h = math.floor(self.townAge/60)%24,m=str(self.townAge%60) if self.townAge%60 > 9 else "0"+ str(self.townAge%60) ))

def main():
    #initialize a ship
    testTown = Ship("New New New York")
    townHall = Buildings.TownHall("Town Hall",False,0,testTown)
    testTown.setTownHall(townHall)
    townRestaurant = Buildings.Restaurant("Restaurant",False,1,testTown)
    townFarm = Buildings.Farm("Farm",False,2,testTown)
    townMine = Buildings.Mine("Mine",False,3,testTown)
    testTown.addBuilding(townRestaurant)
    testTown.addBuilding(townMine)
    testTown.addBuilding(townFarm)
    family1 = Villagers.Family(nameGenerator.getLastName())
    family2 = Villagers.Family(nameGenerator.getLastName())
    family3 = Villagers.Family(nameGenerator.getLastName())
    testTown.addVillager(Villagers.townsperson(nameGenerator.makeName(),  25,'M',family1,townHall,testTown))
    testTown.addVillager(Villagers.townsperson(nameGenerator.makeName(),27,'F',family2,townFarm,testTown))
    testTown.addVillager(Villagers.townsperson(nameGenerator.makeName(),37,'M',family3,townFarm,testTown))
    townTradeHub = Buildings.TradeHub("Trade Hub",False,4,testTown)
    testTown.addBuilding(townTradeHub)
    townTavern = Buildings.Tavern("Tavern",False,5,testTown)
    testTown.addBuilding(townTavern)
    testTown.createOverseer()

    testTown.addItemtoCargo("SUGAR_RICE",1000)

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
        while testTown.isViable():
            testTown.timeUpdate()
            #print to console
            if config.getboolean("DEBUG","VERBOSE"):
                testTown.displayLocalTime()
                testTown.displayBuildings()
            #if not instant, wait fo the next frame
            if not config.getboolean("DEBUG","INSTANT"):
                time.sleep((420/365)/config.getfloat("VALUES","TIMESPEED"))
        testTown.displayLocalTime()
        testTown.displayBuildings()
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        testTown.displayLocalTime()
        
    
    #de-initialize
    CaptainsLog.closeLogs()
    if config.getboolean("VALUES","USEUI"):
        if config.getboolean("DEBUG","INSTANT"):
            input("Close")
        UI.deinitialize()
    return

if __name__ == "__main__":
    main()