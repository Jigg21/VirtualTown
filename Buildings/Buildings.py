import math
import random
from Utilities.ConfigReader import ConfigData as config
from Townspeople import Villagers
from Town import CaptainsLog
from Utilities import Utilities
from Utilities import CONST
from Buildings.Market  import CargoItems

TAVERNCOMRADETHRESHOLD = 0

#building base class
class Building:
    WorkerSalary = 5

    def __init__(self,buidingName,IsPrivate, buildingNumber,town,coords):
        self.buildingName = buidingName
        self.IsPrivate = IsPrivate
        self.Occupants = []
        self.buildingNumber = buildingNumber
        self.Town = town
        self.bClass = CONST.buildingClass.MISC
        #list representing all the coords this building takes up
        self.coords = coords
        return

    #for actions that are activated by villagers
    def activate(self,Villager):
        '''activation base function, does nothing on its own'''
        pass
    
    #for actions that activate every tick
    def timeUpdate(self):
        pass
    
    #returns true if the building is of a certain class
    def isClassOf(self,classType):
        return self.bClass == classType

    #for actions that activate every day
    def dailyUpdate(self,data):
        pass
    
    #manage occupants
    def addOccupant(self,Villager):
        self.Occupants.append(Villager)
    
    def removeOccupant(self,Villager):
        self.Occupants.remove(Villager)
    
    def getOccupants(self):
        return self.Occupants.copy()
    
    #string representation
    def __str__(self):
        result = self.buildingName
        return result

#Town Hall to coordinate villagers        
class TownHall(Building):
    treasury = 1000
    starving = False

    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship, coords)
        self.bClass = CONST.buildingClass.TOWNHALL

    def enterStarving(self):
        self.starving = True
        CaptainsLog.log("WE'RE STARVING")

    def __str__(self):
        result = super().__str__()
        result += "(Treasury: " + str(self.treasury) + ")"
        return result

class Restaurant(Building):
    '''Place for villagers to eat'''
    #how much hunger each food satisfies
    hungerSatisfaction = 10
    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship,coords)
        self.bClass = CONST.buildingClass.RESTAURANT

    def activate(self,Villager):
        itemList = self.Town.getCargoList()
        hall = self.Town.townHall
        #if the town has food
        for item in itemList:
            itemobj = CargoItems.getItemObj(item)
            if itemobj.isEdible():
                self.Town.removeCargo(item,1)
                if Villager.canAfford(5):
                    Villager.spendMoney(5)
                    self.Town.addTreasury(5)
                else:
                    CurrentMoney = Villager.vMoney
                    Villager.spendMoney(CurrentMoney)
                    self.Town.addTreasury(CurrentMoney)
                Villager.eat(self.hungerSatisfaction)
                break
        else:
            if config.getboolean("DEBUG","ENDLESSFOOD"):
                if Villager.canAfford(5):
                    Villager.spendMoney(5)
                    hall.addTreasury(5)
                else:
                    CurrentMoney = Villager.vMoney
                    Villager.spendMoney(CurrentMoney)
                    hall.addTreasury(CurrentMoney)
                Villager.eat(self.hungerSatisfaction)
            hall.enterStarving()

#Grows food 
class Farm(Building):
    crops = []
    maximumCrops = 100

    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship, coords)
        self.bClass = CONST.buildingClass.FARM

    #harvest a crop and get food value
    def harvestCrop(self,crop):
        #add the crop to the cargo
        harvestAmount = crop.getHarvest()
        self.Town.addItemtoCargo(crop.cropName,harvestAmount)
        if crop in self.crops:
            self.crops.remove(crop)
    
    #get overseer data for crops 
    def getHarvestData(self):
        GUTotal = 0
        cropCount = 0
        for c in self.crops:
            GUTotal += c.getRemainingGU()
            cropCount += 1
        if cropCount > 0:
            mean = GUTotal/cropCount
            timeToHarvest = math.ceil(mean / 5)
        else:
            timeToHarvest = math.inf
        
        return timeToHarvest

    #do daily maintenance on crops
    def maintainCrop(self,crop):
        crop.maintain()
    
    #plant a new crop
    def plantCrop(self,crop):
        self.crops.append(crop)

    def dailyUpdate(self, data):
        for c in self.crops:
            c.dailyUpdate()
    
    def __str__(self):
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
        
#Can mine various materials
class Mine(Building):
    
    ironStockpile = 0
    mineEfficiency = 1

    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship, coords)
        self.bClass= CONST.buildingClass.MINE

    def mineGold(self):
        self.Town.addTreasury(self.mineEfficiency)
        

    def mineIron(self):
        for i in range(5):
            yield False
        self.ironStockpile += 1
        yield True

    def __str__(self):
        result = super().__str__()
        result += "(Iron: {iron})".format(iron=self.ironStockpile)
        return result

class TradeHub(Building):
    '''A place to sell food for gold'''
    dailyTradeRate = 0
    def __init__(self, buidingName, IsPrivate, buildingNumber, town, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, town, coords)
        self.bClass.TRADE
    def sellFood(self,amount):
        self.Town.townHall.subtractFood(amount)
        self.Town.townHall.addTreasury(amount*self.dailyTradeRate)
        CaptainsLog.logSale("Food",amount,amount*self.dailyTradeRate)
    
    def dailyUpdate(self,data):
        self.getDailyTradeRate(data["Time"])

    def getDailyTradeRate(self,currentTime):
        self.dailyTradeRate = Utilities.getRandomValue(0,20)
        CaptainsLog.log("Today's trade rate for food is: {rate}".format(rate=self.dailyTradeRate))

class GameHall(Building):
    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship, coords)
        self.bClass = CONST.buildingClass.GAMEHALL
        self.betters = []
    '''Villagers can play games between each other'''
    def activate(self, Villager):
        super().activate(Villager)    
        if len(self.betters) > 2:
            player1 = self.betters.pop()
            player2 = self.betters.pop()
            newGame = Villagers.coopTask()

    def playGame(self,player1,player2):
        '''two player game, one player gets 5 money the other loses 5 money '''
        randomChoice = Utilities.getRandomValue(0,1)
        if randomChoice == 1:
            player1.makeMoney(5)
            player2.spendMoney(5)
        else:
            player1.spendMoney(5)
            player2.makeMoney(5)
        


        
    def addOccupant(self, Villager):
        super().addOccupant(Villager)
        self.betters.append(Villager)

    def removeOccupant(self, Villager):
        super().removeOccupant(Villager)
        try:
            self.betters.remove(Villager)
        except ValueError:
            pass

class Tavern(Building):
    '''a place for villagers to build relations with others'''
    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship, coords)
        self.bClass = CONST.buildingClass.TAVERN
        self.comaraderie = 0
    

    def activate(self, Villager):
        super().activate(Villager)
        self.comaraderie += 1
        if self.comaraderie >= 4:
            self.comaraderie = 0
            for v in self.Occupants:
                if Villager != v:
                    v.drink()
                    Villager.changeRelation(v,random.uniform(-1,1.002**(Villager.vDrunkeness)))
                    v.changeRelation(Villager,random.uniform(-1,1.002**(v.vDrunkeness)))
        
class Factory(Building):

    def __init__(self, buidingName, IsPrivate, buildingNumber, ship, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, ship, coords)

class Home(Building):
    '''a place for villagers tor rest, center of family dynamics'''
    def __init__(self, buidingName, IsPrivate, buildingNumber, town, coords):
        super().__init__(buidingName, IsPrivate, buildingNumber, town, coords)
        self.popLimit = config.getint("BUILDINGS","HOUSEMAX")
        self.residents = []
        self.headFamily = None
    
    def addResident(self,resident):
        '''adds a villager to the house as a resident'''
        self.residents.append(resident)
        #if the house is empty, the villager takes over the house
        if len(self.residents) == 1:
            self.headFamily = resident.family
        else:
            resident.changeFamily(self.headFamily)
    
    def removeResident(self,resident):
        '''remove a resident from the house'''
        if resident in self.residents:
            self.residents.remove(resident)
            if len(self.residents) == 0:
                self.headFamily = None
        else:
            return False




