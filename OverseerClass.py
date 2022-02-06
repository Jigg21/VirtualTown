from Buildings import TradeHub
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

    #calculates time until villagers starve (in ticks)
    def calculateTimeToStarvation(self):
        currentStockpile = self.TownHall.stockPile
        currentNeed = 0
        for v in self.villagers:
            currentNeed += 100 - v.vHunger 
        currentStockpile -= currentNeed
        ticksUntilStarvation = currentStockpile*10//.208
        return ticksUntilStarvation

    #choose the best crop for the situation
    def chooseBestCrop(self):
        #ensure that crops will grown before town starves
        starvationTime = self.calculateTimeToStarvation()
        possibleCrops = dict()
        data = getCropData()
        for c in getCropData():
            crop = data[c]
            #if the crop can be grown before starvation, calculate the ratio of value over growunits
            if (crop["cropRipe"]/5)*1440 < starvationTime:
                possibleCrops[c] = crop["cropValue"]/crop["cropRipe"]
        highestRatio = 0
        highestCrop = None
        for pc in possibleCrops:
             if possibleCrops[pc] > highestRatio:
                 highestCrop = pc
                 highestRatio = possibleCrops[pc]
        return highestCrop
    
    #Post jobs for everything that needs to be done
    def designateDailyTasks(self,townData):

        #Sell food when there is a surplus
        if ("trade" in townData):
            tradeHub = townData["trade"]
            #if food is highly valued
            if tradeHub.dailyTradeRate >= 15:
                timeToHarvest = townData["farm"].getHarvestData()
                #get the amount of surplus food
                reqFood = (timeToHarvest+1) * len(self.town.villagers) * 30
                surplusFood = self.TownHall.getFood() - reqFood
                if surplusFood > 0:
                    self.town.bulletin.postJob(Villagers.Task(tradeHub.sellFood,1,tradeHub,"Selling Food to Market",5,[surplusFood]),self.TownHall)

        #Farm Logic TODO: Replace with smart AI
        if ("farm" in townData):
            farm = townData["farm"]
            #Harvest all ripe crops
            for c in farm.crops:
                #harvest ripe crops
                harvestPercentage = c.getHarvestPercentage()
                if (harvestPercentage >= self.gHarvestThreshold):
                    self.town.bulletin.postJob(Villagers.Task(farm.harvestCrop,c.harvestLaborReq,farm,"Harvesting Crop",5,[c]),self.TownHall)
                #maintain all unripe crops
                else:
                    self.town.bulletin.postJob(Villagers.Task(farm.maintainCrop,c.maintainLaborReq,farm,"Maintaining Crop",5,[c]),self.TownHall)
            #Plant up to the maximum crops    
            if (len(farm.crops) < farm.maximumCrops):
                for i in range(0,farm.maximumCrops- len(farm.crops)):
                    newCrop = Crop(farm, self.chooseBestCrop(),townData["Time"])
                    self.town.bulletin.postJob(Villagers.Task(farm.plantCrop,newCrop.harvestLaborReq,farm,"Planting {crop}".format(crop=newCrop.cropName),5,[newCrop]),self.TownHall)
        
        #TODO: Add mine logic
        if ("mine" in townData):
            mine = townData["mine"]
            for i in range(50):
                self.town.bulletin.postJob(Villagers.Task(mine.mineGold,5,mine,"Mining Gold",5),self.TownHall)
        
