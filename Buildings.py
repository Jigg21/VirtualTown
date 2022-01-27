from unittest import result
import Villagers
import CaptainsLog
import Config
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

    def activate(self,Villager):
        pass

    def timeUpdate(self):
        pass

    def add_occupant(self,Villager):
        self.Occupants.append(Villager)
    
    def remove_occupant(self,Villager):
        self.Occupants.remove(Villager)
    
    def get_occupants(self):
        return self.Occupants.copy()
    
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
    
    def spendTreasury(self,amount):
        self.treasury -= amount
        CaptainsLog.logResource("Gold",-1*amount)

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
        if hall.getFood() > 0 or Config.ENDLESSFOOD:            
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
    def harvestCrop(self,crop,currentTime):
        harvestAmount = crop.getHarvest(currentTime)
        self.town.getTownHall().addFood(harvestAmount)
        if crop in self.crops:
            self.crops.remove(crop)
    
    #do daily maintenance on crops
    def maintainCrop(self,crop):
        crop.maintain()
    
    #plant a new crop
    def plantCrop(self,crop):
        self.crops.append(crop)

    #update each crop about the time it was in
    def timeUpdate(self):
        pass
        #for c in self.crops:
            #c.timeUpdate()
    
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

#use to give jobs to passengers
class bulletinBoard():
    def __init__(self):
        self.activeTasks = []
    
    #assigns a job to the given passenger
    def assignJob(self, passenger):
        return self.activeTasks.pop()
    
    #adds a task to the board
    def postJob(self,task):
        self.activeTasks.append(task)

    #returns true if the bulletin board has any active tasks
    def hasWork(self):
        return len(self.activeTasks) > 0

    def getTaskList(self):
        result = ""
        for t in self.activeTasks:
            result += str(t) + "\n"
        return result
