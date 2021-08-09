import json

CROPDATA = None
test = None


def getCropData():
    global CROPDATA
    if (CROPDATA != None):
        return CROPDATA
    else:
        with open('CropData.json') as f:
            CROPDATA = json.load(f)
        return CROPDATA
        

def convertTimeToCycles(timeString):
    timeSplit = timeString.split(":")
    cycles = 0
    #Years
    cycles += int(timeSplit[0])*525600
    #Days
    cycles += int(timeSplit[1])*1440
    #Hours
    cycles += int(timeSplit[2]*60)
    #Minutes
    cycles += int(timeSplit[3])

    return cycles

class Crop():
    cropName = "DefaultFood"
    plantedTime = 0
    ripeTime = "0:0:0:0"
    harvestValue = 0
    harvestLaborReq = 0
    harvestProgress = 0
    maintainLaborReq = 0
    maintained = True
    farm = None

    def __init__(self,farm,cropName):
        self.cropName = cropName
        CROPDATA = getCropData()
        self.farm = farm
        try:
            self.ripeTime = CROPDATA[cropName]["cropRipe"]
            self.harvestValue = CROPDATA[cropName]["cropValue"]
            self.harvestLaborReq = CROPDATA[cropName]["cropHLabor"]
            self.maintainLaborReq = CROPDATA[cropName]["cropMLabor"]
        except:
            raise ValueError

    def getHarvestPercentage(self) -> float:
        return self.plantedTime/convertTimeToCycles(self.ripeTime)

    def getHarvest(self) -> int:
        harvestPercentage = self.getHarvestPercentage()
        if (harvestPercentage < .5):
            return 0
        if (harvestPercentage < 1 ):
            return self.harvestValue * self.getHarvestPercentage
        if (harvestPercentage >= 1 and harvestPercentage < 1.3):
            overRipe = 1.3-harvestPercentage
            return self.harvestValue * (overRipe/.3)
        else:
            return 0

    def timeUpdate(self):
        self.plantedTime += 1
    
    def dailyReset(self):
        self.maintained = False
    
    def maintain(self):
        self.maintained = True
