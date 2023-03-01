import math
from Buildings import TradeHub
from Crops import *
import Utilities
import CaptainsLog
import Villagers
import CargoItems
import TaskMngmt

class TownAdvisor():
    ship = None
    TownHall = None 
    villagers = None
    gHarvestThreshold = .9

    def __init__(self,town,townhall,villagers) -> None:
        self.ship = town
        self.TownHall = townhall
        self.villagers = villagers

    def calculateTaskAllowance(self):
        '''returns the number of task the overseer can afford to issue'''
        return self.TownHall.treasury // self.TownHall.WorkerSalary

    def getCurrentFoodLevel(self):
        '''gets a tally of the food onboard'''
        foodLevel = 0
        for item in self.ship.getCargoList():
            itemobj = CargoItems.getItemObj(item)
            if itemobj.isEdible():
                foodLevel += self.ship.getCargoCount(item)
            return foodLevel
    
    #calculates time until villagers starve (in ticks)
    def calculateTimeToStarvation(self):
        currentStockpile = self.getCurrentFoodLevel()
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
        #if no crop will grow before the town starves, plant the fastest growing crop
        if len(possibleCrops) == 0:
            fastestGrowth = math.inf
            fastestCrop = None
            for c in getCropData():
                crop = data[c]
                if crop["cropRipe"] < fastestGrowth:
                    fastestGrowth = crop["cropRipe"]
                    fastestCrop = c
            return fastestCrop
                

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
            '''
            tradeHub = townData["trade"]
            #if food is highly valued
            if tradeHub.dailyTradeRate >= 15:
                timeToHarvest = townData["farm"].getHarvestData()
                #get the amount of surplus food
                reqFood = ((timeToHarvest+1) * len(self.town.villagers) * 30)
                reqFood = Utilities.clamp(len(self.villagers)*30,math.inf,reqFood)
                surplusFood = self.TownHall.getFood() - reqFood
                if surplusFood > 0:
                    self.town.bulletin.postJob(Villagers.Task(tradeHub.sellFood,1,tradeHub,"Selling Food to Market",5,[surplusFood]),self.TownHall)
            '''
        
        #Farm Logic TODO: Replace with smart AI
        if ("farm" in townData):
            farm = townData["farm"]
            #Harvest all ripe crops
            for c in farm.crops:
                #harvest ripe crops
                harvestPercentage = c.getHarvestPercentage()
                if (harvestPercentage >= self.gHarvestThreshold):
                    self.ship.bulletin.postJob(TaskMngmt.Task(farm.harvestCrop,c.harvestLaborReq,farm,"Harvesting Crop",5,[c]))
                #maintain all unripe crops
                else:
                    self.ship.bulletin.postJob(TaskMngmt.Task(farm.maintainCrop,c.maintainLaborReq,farm,"Maintaining Crop",5,[c]))
            #Plant up to the maximum crops    
            if (len(farm.crops) < farm.maximumCrops):
                for i in range(0,farm.maximumCrops- len(farm.crops)):
                    newCrop = Crop(farm, self.chooseBestCrop(),townData["Cycle"])
                    self.ship.bulletin.postJob(TaskMngmt.Task(farm.plantCrop,newCrop.harvestLaborReq,farm,"Planting {crop}".format(crop=newCrop.cropName),5,[newCrop]))
        
        #TODO: Add mine logic
        if ("mine" in townData):
            mine = townData["mine"]
            for i in range(50):
                self.ship.bulletin.postJob(TaskMngmt.Task(mine.mineGold,5,mine,"Mining Gold",5))
        
