import math
from ConfigReader import ConfigData as config
from unittest import result
import Villagers
import CaptainsLog
import Utilities

#building base class
class Building:
    Occupants = []
    IsPrivate = False
    buildingNumber = 0
    buildingName = ""
    town = None
    WorkerSalary = 5
    def __init__(self,buidingName,IsPrivate, buildingNumber,town):
        self.buildingName = buidingName
        self.IsPrivate = IsPrivate
        self.Occupants = []
        self.buildingNumber = buildingNumber
        self.town = town
        return

    #for actions that are activated by villagers
    def activate(self,Villager):
        pass
    
    #for actions that activate every tick
    def timeUpdate(self):
        pass
    
    #for actions that activate every day
    def dailyUpdate(self,data):
        pass
    
    #manage occupants
    def add_occupant(self,Villager):
        self.Occupants.append(Villager)
    
    def remove_occupant(self,Villager):
        self.Occupants.remove(Villager)
    
    def get_occupants(self):
        return self.Occupants.copy()
    
    #string representation
    def __str__(self):
        result = self.buildingName
        return result

#Town Hall to coordinate villagers        
class TownHall(Building):
    stockPile = 1000
    treasury = 1000
    starving = False

    def addFood(self,amount):
        self.stockPile += amount
        CaptainsLog.logResource("Food",amount)
    
    def getFood(self):
        return self.stockPile

    def subtractFood(self,amount):
        self.stockPile -= amount
        CaptainsLog.logResource("Food",-1*amount)

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
        


    def enterStarving(self):
        self.starving = True
        CaptainsLog.log("WE'RE STARVING")

    
    def __str__(self):
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
        if hall.getFood() > 0 or config.getboolean("DEBUG","ENDLESSFOOD"):            
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

    #harvest a crop and get food value
    def harvestCrop(self,crop):
        harvestAmount = crop.getHarvest()
        self.town.getTownHall().addFood(harvestAmount)
        if crop in self.crops:
            self.crops.remove(crop)
    
    #get overseer data for crops 
    def getHarvestData(self):
        GUTotal = 0
        cropCount = 0
        for c in self.crops:
            GUTotal += c.getRemainingGU()
            cropCount += 1
        mean = GUTotal/cropCount
        timeToHarvest = math.ceil(mean / 5)
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
        
#Can mine gold for the treasury or iron for upgrades
class Mine(Building):
    ironStockpile = 0
    mineEfficiency = 1

    def mineGold(self):
        self.town.townHall.addTreasury(self.mineEfficiency)
        

    def mineIron(self):
        for i in range(5):
            yield False
        self.ironStockpile += 1
        yield True

    def __str__(self):
        result = super().__str__()
        result += "(Iron: {iron})".format(iron=self.ironStockpile)
        return result

#A place to sell food for gold
class TradeHub(Building):

    dailyTradeRate = 0
    def __init__(self, buidingName, IsPrivate, buildingNumber, town):
        super().__init__(buidingName, IsPrivate, buildingNumber, town)
    
    def sellFood(self,amount):
        print("selling")
        self.town.townHall.subtractFood(amount)
        self.town.townHall.addTreasury(amount*self.dailyTradeRate)
        CaptainsLog.logSale("Food",amount,amount*self.dailyTradeRate)
    
    def dailyUpdate(self,data):
        self.getDailyTradeRate(data["Time"])

    def getDailyTradeRate(self,currentTime):
        self.dailyTradeRate = Utilities.getRandomValue(currentTime,0,20)
        CaptainsLog.log("Today's trade rate for food is: {rate}".format(rate=self.dailyTradeRate))

        

    


