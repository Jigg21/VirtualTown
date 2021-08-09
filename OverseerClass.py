from Crops import *
import Utilities

class TownOverseer():
    town = None
    TownHall = None 
    villagers = None
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
            if convertTimeToCycles(crop["cropRipe"]) < starvationTime:
                possibleCrops[c] = crop["cropValue"]/convertTimeToCycles(crop["cropRipe"])
        highestRatio = 0
        highestCrop = None
        for pc in possibleCrops:
             if possibleCrops[pc] > highestRatio:
                 highestCrop = pc
                 highestRatio = possibleCrops[pc]
        return highestCrop

    def designateDailyTasks(farm,townData):
        #ADD FARM LOGIC HERE
        if ("farm" in townData):
            farm = townData["farm"]
            for c in farm.crops:
                harvestPercentage = c.getHarvestPercentage()
                if (harvestPercentage >= 1):
                    farm.activeTasks.append(farm.harvestCrop(c))
            for c in farm.crops:
                farm.activeTasks.append(farm.maintainCrop(c))

            if (len(farm.crops) < farm.maximumCrops):
                for i in range(0,farm.maximumCrops- len(farm.crops)):
                    farm.activeTasks.append(farm.plantCrop(Crop(farm, farm.town.overseer.chooseBestCrop())))
        
        #ADD MINE LOGIC HERE
        if ("mine" in townData):
            mine = townData["mine"]
            mine.activeTasks = []
            for i in range(50):
                mine.activeTasks.append(mine.mineGold())
            


    
    