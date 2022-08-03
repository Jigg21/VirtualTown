from distutils.log import error
import json
from lib2to3.pytree import Base
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
    #how many growth units this crop has
    growUnits = 0
    #how many growthUnits it takes to grow
    ripeTime = 0
    #how much food is given upon harvest
    harvestValue = 0
    #how much labor is needed to harvest
    harvestLaborReq = 0
    #how much labor is required to maintain the crop
    maintainLaborReq = 0
    #has this crop been maintained?
    maintained = True
    #days since last maintainance
    lastMaintain = 0
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
            self.ripeTime = int(CROPDATA[cropName]["cropRipe"])
            self.harvestValue = CROPDATA[cropName]["cropValue"]
            self.harvestLaborReq = CROPDATA[cropName]["cropHLabor"]
            self.maintainLaborReq = CROPDATA[cropName]["cropMLabor"]
            self.cropColor = CROPDATA[cropName]["cropColor"]
        except BaseException as E:
            print (E)
            raise ValueError

    #get percentage of time planted and time needed to ripen
    def getHarvestPercentage(self):
        return self.growUnits/self.ripeTime

    #get the amount of food this crop would yield if harvested
    def getHarvest(self) -> int:
        harvestPercentage = self.getHarvestPercentage()
        if (harvestPercentage < .5):
            return 0
        if (harvestPercentage < 1 ):
            return self.harvestValue * harvestPercentage
        if (harvestPercentage >= 1 and harvestPercentage < 1.3):
            overRipe = 1.3-harvestPercentage
            return self.harvestValue * (overRipe/.3)
        else:
            return 0
    
    #return the remaining Grow units before maturation
    def getRemainingGU(self):
        return self.ripeTime - self.growUnits
        
    #update daily
    def dailyUpdate(self):
        #TODO: Make growUnits earned dependant on ship location
        self.growUnits += 5
        if not self.maintained:
            self.lastMaintain += 1
            self.growUnits -= 2**self.lastMaintain
        self.maintained = False
    
    #do daily maintainance
    def maintain(self):
        self.maintained = True
        self.lastMaintain = 0
