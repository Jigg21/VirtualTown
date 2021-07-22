from Crops import Crop
import time
import math
from enum import Enum

#Time Speed 1 = 1 year every week
TIMESPEED = 1

#Do not wait between time updates (for debugging)
INSTANT = True
#Display every cycle
VERBOSE = False

class Town:
    townName = ""
    townAge = -1
    townAgeReadable = ""
    villagers = []
    buildings = []
    townHall = None
    def __init__(self,name):
        self.townName = name

    def setTownHall(self,townHall):
        self.townHall = townHall
        self.addBuilding(townHall)
    
    def getTownHall(self):
        return self.townHall

    def addVillager (self,villager):
        self.villagers.append(villager)
    
    def addBuilding (self,building):
        self.buildings.append(building)
    
    def FindBuilding(self, targetType):
        for b in self.buildings:
            if (isinstance(b,targetType)):
                return b
 
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

    def timeUpdate(self):
        self.townAge += 1
        self.townAgeReadable = convertCyclesToTime(self.townAge)
        for v in self.villagers:
            v.update()
        if (self.townAge%1440 == 0):
            self.FindBuilding(Farm).startWorkDay()
        self.FindBuilding(Farm).timeUpdate()
    
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

    def __init__(self,name,age,gender,startLocation,town,job):
        self.vAge = age
        self.vGender = gender
        self.vName = name
        self.currentLocation = startLocation
        self.currentLocation.add_occupant(self)
        self.town = town
        self.job = job


    def update(self):
        self.vHunger -= .208
        self.currentLocation.activate(self)
        if (self.vHunger < 10):
            self.vState = VillagerStates.EATING
            self.goEat()
            
        if (self.vHunger > 95 and self.vState == VillagerStates.EATING):
            self.vState = VillagerStates.WORKING
            self.goWork()
        
    def eat(self,amount):
        self.vHunger += amount
        if (self.vHunger > 100):
            self.vHunger = 100
    
    def finishWork(self):
        self.offWork = True
        self.vState = VillagerStates.IDLE
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

    def makeSalary(self,amount):
        hall = self.town.getTownHall()
        hall.spendTreasury(amount)
        self.vMoney += amount
    
    def makeMoney(self,amount):
        self.vMoney += amount
            
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
        result += "Money: {money}".format(money=self.vMoney)
        return result

class Building:
    Occupants = []
    IsPrivate = False
    buildingNumber = 0
    buildingName = ""
    town = None
    def __init__(self,buidingName,IsPrivate, buildingNumber,town):
        self.buildingName = buidingName
        self.IsPrivate = IsPrivate
        self.Occupants = []
        self.buildingNumber = buildingNumber
        self.town = town
        return

    def activate(self,Villager):
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
    stockPile = 0
    treasury = 1000
    def addFood(self,amount):
        self.stockPile += amount
    
    def subtractFood(self,amount):
        self.stockPile -= amount

    def addTreasury(self,amount):
        self.treasury += amount
    
    def spendTreasury(self,amount):
        self.treasury -= amount
    
    def __str__(self) -> str:
        result = super().__str__()
        result += "(Food: " + str(self.stockPile) + ")"
        result += "(Treasury: " + str(self.treasury) + ")"
        return result

#Place for villagers to eat
class Restaurant(Building):

    hungerSatisfaction = 10

    def activate(self,Villager):
        Villager.spendMoney(5)
        Villager.eat(self.hungerSatisfaction)
        hall = self.town.getTownHall()
        hall.subtractFood(1)
        hall.addTreasury(5)

class Farm(Building):
    crops = []
    maximumCrops = 100
    activeTasks = []
    def harvestCrop(self,crop):
        neededLabor = crop.harvestLaborReq
        for i in range(neededLabor):
            yield False
        self.town.getTownHall().addFood(crop.getHarvest())
        yield True

    def maintainCrop(self,crop):
        neededLabor = crop.maintainLaborReq
        for i in range(neededLabor):
            yield False
        yield True
    
    def plantCrop(self,crop):
        for i in range(crop.harvestLaborReq):
            yield False
        self.crops.append(crop)
        return True

    def timeUpdate(self):
        for c in self.crops:
            c.timeUpdate()

    def startWorkDay(self):
        self.activeTasks = []
        for c in self.crops:
            harvestPercentage = c.getHarvestPercentage()
            if (harvestPercentage >= 1):
                self.activeTasks.append(self.harvestCrop(c))
        for c in self.crops:
            self.activeTasks.append(self.maintainCrop(c))

        if (len(self.crops) < self.maximumCrops):
            for i in range(0,self.maximumCrops- len(self.crops)):
                self.activeTasks.append(self.plantCrop(Crop(self,"WinterBerries")))
        
    def activate(self, Villager):
        if (Villager.hasWork()):
            finishedWork = Villager.work()
            if (finishedWork):
                if (len(self.activeTasks) > 0):
                    Villager.getWork(self.activeTasks.pop(0))
                else:
                    Villager.finishWork()
        else:
            if (len(self.activeTasks) > 0):
                print("assigning work")
                Villager.getWork(self.activeTasks.pop(0))

class Mine(Building):
    labor = 0
    def activate(self, Villager):
        self.labor += 1
        Villager.makeSalary(5)
        if (self.labor > 4):
            self.labor -= 4
            self.town.getTownHall().addTreasury(1)


def convertTimeToCycles(timeString):
    timeSplit = timeString.split(":")
    cycles = 0
    #Years
    cycles += int(timeSplit[0])*525600
    #Days
    cycles += int(timeSplit[1])*1440
    #Hours
    cycles += int(timeSplit[2]*60)
    #Minutes
    cycles += int(timeSplit[3])

    return cycles

def convertCyclesToTime(time):
    result = ""
    result += str(time//525600) + ":"
    result += str(time//1440) + ":"
    result += str(time//60) + ":"
    result += str(time%60)
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

    Villager1 = townsperson("Michael",25,'M',townHall,testTown,townFarm)
    Villager2 = townsperson("Pichael",27,'F',townFarm,testTown,townFarm)
    testTown.addVillager(Villager1)
    testTown.addVillager(Villager2)

    try:
        for x in range(convertTimeToCycles("0:11:0:20")):
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

    return


main()