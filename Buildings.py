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
    activeTasks = []
    def __init__(self,buidingName,IsPrivate, buildingNumber,town):
        self.buildingName = buidingName
        self.IsPrivate = IsPrivate
        self.Occupants = []
        self.buildingNumber = buildingNumber
        self.town = town
        return

    def activate(self,Villager):
        #if (Villager.vState == Villagers.VillagerStates.IDLE ):
            if (Villager.hasWork()):
                Villager.work()
                if (Villager.vTask.isCompleted()):
                    if (len(self.activeTasks) > 0):
                        Villager.getWork(self.activeTasks.pop(0))
                    else:
                        Villager.finishWork()       
            else:
                if (len(self.activeTasks) > 0):
                    Villager.getWork(self.activeTasks.pop(0))
                else:
                    Villager.finishWork()

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

    def harvestCrop(self,crop):
        CaptainsLog.log("Starting Harvest")
        self.town.getTownHall().addFood(crop.getHarvest())
        if crop in self.crops:
            self.crops.remove(crop)
        return True

    def maintainCrop(self,crop):
        crop.maintain()
        CaptainsLog.log("Maitain")
    
    def plantCrop(self,crop):
        self.crops.append(crop)
        CaptainsLog.log("Planted Crops")

    def timeUpdate(self):
        for c in self.crops:
            c.timeUpdate()
    
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
