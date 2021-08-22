import CaptainsLog
from Crops import Crop
import time
import math
from enum import Enum
from OverseerClass import TownOverseer
import Utilities
#Time Speed 1 = 1 year every week
TIMESPEED = 1

ENDLESSFOOD = True

#Do not wait between time updates (for debugging)
INSTANT = True
#Display every cycle
VERBOSE = False

#contains all town-wide events and variables
class Town:
    townName = ""
    townAge = -1
    townAgeReadable = ""
    villagers = []
    buildings = []
    townHall = None
    overseer = None
    def __init__(self,name):
        self.townName = name

    #get and set townhall
    def setTownHall(self,townHall):
        self.townHall = townHall
        self.addBuilding(townHall)
    
    def getTownHall(self):
        return self.townHall

    #add villagers and buildings
    def addVillager (self,villager):
        self.villagers.append(villager)
    
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
    
    def displayBuildings(self):
        for b in self.buildings:
            print(b)
            if len(b.Occupants) == 0:
                print("\tNone")
            else:
                for v in b.get_occupants():
                    print('\t',v)

    #called every tick
    def timeUpdate(self):
        self.townAge += 1
        self.townAgeReadable = Utilities.convertTicksToTime(self.townAge)
        for v in self.villagers:
            v.update()

        #New Day
        if (self.townAge%1440 == 0):
            #A dictionary of useful information
            CaptainsLog.newDay()
            CaptainsLog.log(Utilities.convertTicksToTime(self.townAge))
            townData = dict()
            townData["farm"] = self.FindBuilding(Farm)
            self.overseer.designateDailyTasks(townData)

        for building in self.buildings:
            building.timeUpdate()
    
    #initialize the overseer
    def createOverseer(self):
        self.overseer = TownOverseer(self,self.townHall,self.villagers)

    #show local time
    def displayLocalTime(self):
        print("Local Time: Y{y} D{d} {h}:{m}".format(y=math.floor(self.townAge/525600), d=math.floor(self.townAge/1440), h = math.floor(self.townAge/60)%24,m=str(self.townAge%60) if self.townAge%60 > 9 else "0"+ str(self.townAge%60) ))

class VillagerStates(Enum):
    IDLE = 1
    EATING = 2
    WORKING = 3

class townsperson:
    vName = ""
    vAge = 0
    vGender = 'M'
    currentLocation = None
    vHunger = 100
    town = []
    vState = VillagerStates.IDLE
    job = None
    vMoney = 10
    vTask = None
    offWork = False
    experience = 0
    def __init__(self,name,age,gender,startLocation,town,job):
        self.vAge = age
        self.vGender = gender
        self.vName = name
        self.currentLocation = startLocation
        self.currentLocation.add_occupant(self)
        self.town = town
        self.job = job

    #called once a tick
    def update(self):
        self.vHunger -= .208
        self.currentLocation.activate(self)
        if (self.vHunger < 10):
            self.vState = VillagerStates.EATING
            self.goEat()
            
        if (self.vHunger > 95 and self.vState == VillagerStates.EATING):
            self.vState = VillagerStates.IDLE
        
        if (self.vState == VillagerStates.IDLE):
            if (not self.offWork):
                self.goWork()
            
       
    def eat(self,amount):
        self.vHunger += amount
        if (self.vHunger > 100):
            self.vHunger = 100
    
    def finishWork(self,pay):
        self.offWork = True
        self.vState = VillagerStates.IDLE
        self.makeSalary(pay)
        self.experience += 1

    def goTo(self,location):
        self.currentLocation.remove_occupant(self)
        self.currentLocation = location
        self.currentLocation.add_occupant(self)

    def goEat(self):
        if (not isinstance(self.currentLocation, Restaurant)):
            self.goTo(self.town.FindBuilding(Restaurant))
    
    def goWork(self):
        if (self.currentLocation != self.job):
            self.goTo(self.job)
        self.vState = VillagerStates.WORKING

    def makeSalary(self,amount):
        hall = self.town.getTownHall()
        hall.spendTreasury(amount)
        self.vMoney += amount
    
    def makeMoney(self,amount):
        self.vMoney += amount
    
    def canAfford(self,amount):
        return self.vMoney > amount

    def spendMoney(self,amount):
        self.vMoney -= amount

    def work(self) -> bool:
        try:
            return next(self.vTask)
        except StopIteration:
            return True
        
    def hasWork(self) -> bool:
        return self.vTask != None
    
    def getWork(self,task):
        self.vTask = task
        

    def __str__(self) -> str:
        result = self.vName
        result += " ({age}/{gender})".format(age=self.vAge,gender=self.vGender)
        result += " Hunger: {hunger}".format(hunger = math.floor(self.vHunger))
        result += " Money: {money}".format(money=self.vMoney)
        result += " EXP: {exp}".format(exp=self.experience)
        return result

#Base class
class Building:
    Occupants = []
    IsPrivate = False
    buildingNumber = 0
    buildingName = ""
    town = None
    WorkerSalary = 5
    activeTasks = []
    def __init__(self,buidingName,IsPrivate, buildingNumber,town):
        self.buildingName = buidingName
        self.IsPrivate = IsPrivate
        self.Occupants = []
        self.buildingNumber = buildingNumber
        self.town = town
        return

    def activate(self,Villager):
        if (Villager.hasWork()):
            finishedWork = Villager.work()
            if (finishedWork):
                if (len(self.activeTasks) > 0):
                    Villager.getWork(self.activeTasks.pop(0))
                else:
                    Villager.finishWork(self.WorkerSalary)
        else:
            if (len(self.activeTasks) > 0):
                Villager.getWork(self.activeTasks.pop(0))

    def timeUpdate(self):
        pass

    def add_occupant(self,Villager):
        self.Occupants.append(Villager)
    
    def remove_occupant(self,Villager):
        self.Occupants.remove(Villager)
    
    def get_occupants(self):
        return self.Occupants.copy()
    
    def __str__(self) -> str:
        result = self.buildingName
        return result

#Town Hall to coordinate villagers        
class TownHall(Building):
    stockPile = 400
    treasury = 1000
    starving = False

    def addFood(self,amount):
        self.stockPile += amount
    
    def getFood(self) -> int:
        return self.stockPile

    def subtractFood(self,amount):
        self.stockPile -= amount

    def addTreasury(self,amount):
        self.treasury += amount
    
    def spendTreasury(self,amount):
        self.treasury -= amount

    def enterStarving(self):
        self.starving = True
        CaptainsLog.log("WE'RE STARVING")

    
    def __str__(self) -> str:
        result = super().__str__()
        result += "(Food: " + str(self.stockPile) + ")"
        result += "(Treasury: " + str(self.treasury) + ")"
        return result

#Place for villagers to eat
class Restaurant(Building):

    #how much hunger each food satisfies
    hungerSatisfaction = 10

    def activate(self,Villager):
        hall = self.town.getTownHall()
        #if the town has food
        if hall.getFood() > 0 or ENDLESSFOOD:            
            hall.subtractFood(1)
            if Villager.canAfford(5):
                Villager.spendMoney(5)
                hall.addTreasury(5)
            else:
                CurrentMoney = Villager.vMoney
                Villager.spendMoney(CurrentMoney)
                hall.addTreasury(CurrentMoney)

            Villager.eat(self.hungerSatisfaction)
        else:
            hall.enterStarving()

#Grows food 
class Farm(Building):
    crops = []
    maximumCrops = 100
    def harvestCrop(self,crop):
        CaptainsLog.log("Starting Harvest")
        neededLabor = crop.harvestLaborReq
        for i in range(neededLabor):
            if crop in self.crops:
                yield False
            else:
                return False
        self.town.getTownHall().addFood(crop.getHarvest())
        if crop in self.crops:
            self.crops.remove(crop)
        return True

    def maintainCrop(self,crop):
        neededLabor = crop.maintainLaborReq
        for i in range(neededLabor):
            yield False
        crop.maintain()
        CaptainsLog.log("Maitain")
        yield True
    
    def plantCrop(self,crop):
        for i in range(crop.harvestLaborReq):
            yield False
        self.crops.append(crop)
        CaptainsLog.log("Planted Crops")
        return True

    def timeUpdate(self):
        for c in self.crops:
            c.timeUpdate()
    
    def __str__(self) -> str:
        result = super().__str__()
        fields = dict()
        for crop in self.crops:
            if crop.cropName in fields:
                fields[crop.cropName] += 1
            else:
                fields[crop.cropName] = 1
        
        for cropB in fields:
            result += "({sCrop}:{sCount})".format(sCrop = cropB,sCount = fields[cropB])
        return result
        
#Can mine gold for the treasury or iron for upgrades
class Mine(Building):
    ironStockpile = 0
    mineEfficiency = 1

    def mineGold(self):
        for i in range(5):
            yield False
        self.town.townHall.addTreasury(self.mineEfficiency)
        print("mined gold")
        yield True

    def mineIron(self):
        for i in range(5):
            yield False
        self.ironStockpile += 1
        yield True

    def timeUpdate(self):
        super().timeUpdate()

    def __str__(self) -> str:
        result = super().__str__()
        result += "(Iron: {iron})".format(iron=self.ironStockpile)
        return result


def main():
    testTown = Town("Nuketown")
    townHall = TownHall("Town Hall",False,0,testTown)
    testTown.setTownHall(townHall)
    townTavern = Restaurant("Tavern",False,1,testTown)
    townFarm = Farm("Farm",False,2,testTown)
    townMine = Mine("Mine",False,3,testTown)
    testTown.addBuilding(townTavern)
    testTown.addBuilding(townMine)
    testTown.addBuilding(townFarm) 
    testTown.addVillager(townsperson("Michael",25,'M',townHall,testTown,townFarm))
    testTown.addVillager(townsperson("Pichael",27,'F',townFarm,testTown,townFarm))
    testTown.addVillager(townsperson("Nickle",37,'M',townFarm,testTown,townMine))
    testTown.createOverseer()
    try:
        for x in range(Utilities.convertTimeToTicks("0:15:0:20")):
            testTown.timeUpdate()
            if VERBOSE:
                testTown.displayLocalTime()
                testTown.displayBuildings()

            if not INSTANT:
                time.sleep((420/365)/(TIMESPEED))
        testTown.displayLocalTime()
        testTown.displayBuildings()
    except Exception as e:
        print("Error!:" + str(e))
        testTown.displayLocalTime()
    CaptainsLog.log("See you space cowboy...")
    CaptainsLog.closeLogs()
    return


main()