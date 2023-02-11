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
from Networking import OceaniaNetworkingClient as ONC
from threading import Thread

#contains all ship-wide events and variables
class Ship:
    def __init__(self,name,townAge=-1,online=False):
        self.townName = name
        if online:
            self.networkAdapter = ONC.ShipNetworkAdapter(self)
        else:
            self.networkAdapter = None
        #basic town information
        self.townName = ""
        self.townAge = townAge
        #current ship temperature
        self.distanceToSun = 50
        #string representing the town age
        self.townAgeReadable = ""
        self.cargo = {}
        #the basic town objects
        self.villagers = []
        self.buildings = []
        self.townHall = None
        self.overseer = None
        self.treasury = 1000
        self.bulletin = Villagers.bulletinBoard(self)
        self.eventHandler = ShipEvents.EventHandler()

        #buildings
        townHall = Buildings.TownHall("Town Hall",False,0,self)
        self.setTownHall(townHall)
        townRestaurant = Buildings.Restaurant("Restaurant",False,1,self)
        townFarm = Buildings.Farm("Farm",False,2,self)
        townMine = Buildings.Mine("Mine",False,3,self)
        self.addBuilding(townRestaurant)
        self.addBuilding(townMine)
        self.addBuilding(townFarm)
        townTradeHub = Buildings.TradeHub("Trade Hub",False,4,self)
        self.addBuilding(townTradeHub)
        townTavern = Buildings.Tavern("Tavern",False,5,self)
        self.addBuilding(townTavern)
        self.createOverseer()

        #villagers
        family1 = Villagers.Family(nameGenerator.getLastName())
        family2 = Villagers.Family(nameGenerator.getLastName())
        family3 = Villagers.Family(nameGenerator.getLastName())
        self.addVillager(Villagers.townsperson(nameGenerator.makeName(),  25,'M',family1,townHall,self))
        self.addVillager(Villagers.townsperson(nameGenerator.makeName(),27,'F',family2,townFarm,self))
        self.addVillager(Villagers.townsperson(nameGenerator.makeName(),37,'M',family3,townFarm,self))

        #starting items
        self.addItemtoCargo("SUGAR_RICE",1000)


        #config
        self.context = self.getSimState()
        if config.getboolean("VALUES","USEUI"):
            self.UI = UI.ShipWindow()

    def offlineLaunch(self):
        pass

    def connect(self):
        '''connect to the server and attach timeupdate to it'''
        if config.getboolean("NETWORKING","ONLINE") and self.isOnline():
            self.networkAdapter.connect()
        else:
            raise ConnectionError
        
    def addTreasury(self,amount):
        '''get gold'''
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
        townData = self.getSimState()
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
        return townData

    def getSimState(self):
        townData = dict()
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
        return townData

    def createOverseer(self):
        '''initialize the overseer'''
        self.overseer = TownOverseer(self,self.townHall,self.villagers)

    def isViable(self):
        '''is the town viable (are there any villagers alive)'''
        for v in self.villagers:
            if v.checkAlive():
                return True
        return False
    
    def isOnline(self):
        return self.networkAdapter != None

    #show local time
    def displayLocalTime(self):
        print("Local Time: Y{y} D{d} {h}:{m}".format(y=math.floor(self.townAge/525600), d=math.floor(self.townAge/1440), h = math.floor(self.townAge/60)%24,m=str(self.townAge%60) if self.townAge%60 > 9 else "0"+ str(self.townAge%60) ))

class OfflineUpdate(Thread):
    def __init__(self,ship) -> None:
        super().__init__(daemon=True)
        self.ship = ship
    def run(self) -> None:
        while self.ship.isViable():
            self.ship.context = self.ship.timeUpdate()
            #print to console
            if config.getboolean("DEBUG","VERBOSE"):
                self.ship.displayLocalTime()
                self.ship.displayBuildings()
            #if not instant, wait for the next frame
            if not config.getboolean("DEBUG","INSTANT"):
                time.sleep((420/365)/config.getfloat("VALUES","TIMESPEED"))
        self.ship.displayLocalTime()
        self.ship.displayBuildings()

def main():
    online = config.getboolean("NETWORKING","ONLINE")
    #initialize a test ship
    testTown = Ship("New New New York",online=online)

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
    
    #CENTRAL FINITE CURVE
    
    if config.getboolean("NETWORKING","ONLINE"):
        '''if the ship is online, online behaviors are needed'''
        testTown.connect()
    else:
        sim = OfflineUpdate(testTown)
        try:
            sim.start()
            testTown.UI.inititialize(testTown.townName,testTown.context)
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            testTown.displayLocalTime()
            
    
    #de-initialize

    CaptainsLog.closeLogs()
    if config.getboolean("DEBUG","INSTANT"):
        input("Close")
        
    return

if __name__ == "__main__":
    main()