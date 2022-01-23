import json
import string
import Utilities
CROPDATA = None


def getCropData():
    global CROPDATA
    if (CROPDATA != None):
        return CROPDATA
    else:
        with open('CropData.json') as f:
            CROPDATA = json.load(f)
        return CROPDATA
        


class Crop():
    #name of the crop
    cropName = "DefaultFood"
    #when (in ticks) was it planted
    plantedTime = 0
    #how long (in ticks) does it take to mature
    ripeTime = 0
    #how much food is given upon harvest
    harvestValue = 0
    #how much labor is needed to harvest
    harvestLaborReq = 0
    #how much labor is required to maintain the crop
    maintainLaborReq = 0
    #has this crop been maintained?
    maintained = True
    #The farm this crop belongs to
    farm = None
    #what color this crop should be on the display
    cropColor = "#ff00ff"
    def __init__(self,farm,cropName,plantedTime):
        
        self.plantedTime = Utilities.convertTimeToTicks(plantedTime)
        self.cropName = cropName
        CROPDATA = getCropData()
        self.farm = farm
        try:
            self.ripeTime = Utilities.convertTimeToTicks(CROPDATA[cropName]["cropRipe"])
            self.harvestValue = CROPDATA[cropName]["cropValue"]
            self.harvestLaborReq = CROPDATA[cropName]["cropHLabor"]
            self.maintainLaborReq = CROPDATA[cropName]["cropMLabor"]
            self.cropColor = CROPDATA[cropName]["cropColor"]
        except:
            raise ValueError

    #get percentage of time planted and time needed to ripen
    def getHarvestPercentage(self,currentTime):
        if currentTime is string:
            currentTime = Utilities.convertTimeToTicks(currentTime);
        return (Utilities.convertTimeToTicks(currentTime)-self.plantedTime)/self.ripeTime

    #get the amount of food this crop would yield if harvested
    def getHarvest(self,currentTime) -> int:
        harvestPercentage = self.getHarvestPercentage(currentTime)
        if (harvestPercentage < .5):
            return 0
        if (harvestPercentage < 1 ):
            return self.harvestValue * harvestPercentage
        if (harvestPercentage >= 1 and harvestPercentage < 1.3):
            overRipe = 1.3-harvestPercentage
            return self.harvestValue * (overRipe/.3)
        else:
            return 0
    
    def dailyReset(self):
        if not self.maintained:
            self.plantedTime += 700
        self.maintained = False
    
    #do daily maintainance
    def maintain(self):
        self.maintained = True
