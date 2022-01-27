from Crops import *
import Utilities
import CaptainsLog
import Villagers

class TownOverseer():
    town = None
    TownHall = None 
    villagers = None
    gHarvestThreshold = .9

    def __init__(self,town,townhall,villagers) -> None:
        self.town = town
        self.TownHall = townhall
        self.villagers = villagers

    def calculateTaskAllowance(self):
        return self.TownHall.treasury // self.TownHall.WorkerSalary

    def calculateTimeToStarvation(self):
        currentStockpile = self.TownHall.stockPile
        currentNeed = 0
        for v in self.villagers:
            currentNeed += 100 - v.vHunger 
        currentStockpile -= currentNeed
        cyclesUntilStarvation = currentStockpile*10//.208
        return cyclesUntilStarvation

    def chooseBestCrop(self):
        starvationTime = self.calculateTimeToStarvation()
        possibleCrops = dict()
        data = getCropData()
        for c in getCropData():
            crop = data[c]
            if Utilities.convertTimeToTicks(crop["cropRipe"]) < starvationTime:
                possibleCrops[c] = crop["cropValue"]/Utilities.convertTimeToTicks(crop["cropRipe"])
        highestRatio = 0
        highestCrop = None
        for pc in possibleCrops:
             if possibleCrops[pc] > highestRatio:
                 highestCrop = pc
                 highestRatio = possibleCrops[pc]
        return highestCrop

    def designateDailyTasks(self,townData):
        #Farm Logic TODO: Replace with smart AI
        if ("farm" in townData):
            farm = townData["farm"]
            #Harvest all ripe crops
            for c in farm.crops:
                #harvest ripe crops
                harvestPercentage = c.getHarvestPercentage(townData["Time"])
                if (harvestPercentage >= self.gHarvestThreshold):
                    self.town.bulletin.postJob(Villagers.Task(farm.harvestCrop,c.harvestLaborReq,farm,"Harvesting Crop",5,[c,townData["Time"]]))
                #maintain all unripe crops
                else:
                    self.town.bulletin.postJob(Villagers.Task(farm.maintainCrop,c.maintainLaborReq,farm,"Maintaining Crop",5,[c]))
            #Plant up to the maximum crops    
            if (len(farm.crops) < farm.maximumCrops):
                for i in range(0,farm.maximumCrops- len(farm.crops)):
                    newCrop = Crop(farm, self.chooseBestCrop(),townData["Time"])
                    self.town.bulletin.postJob(Villagers.Task(farm.plantCrop,newCrop.harvestLaborReq,farm,"Planting {crop}".format(crop=newCrop.cropName),5,[newCrop]))
        
        #TODO: Add mine logic
        if ("mine" in townData):
            mine = townData["mine"]
            for i in range(50):
                self.town.bulletin.postJob(Villagers.Task(mine.mineGold,5,mine,"Mining Gold",5))