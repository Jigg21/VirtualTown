import csv
import os

CROPDATA = None
FILEPATH = os.getcwd()


def getCropData():
    '''load the crop data from file and return a dictionary'''
    global CROPDATA
    if (CROPDATA != None):
        return CROPDATA
    else:
        #with open('data\\CropData.json') as f:
            #CROPDATA = json.load(f)

        CROPDATA = {}
        with open(os.path.join(FILEPATH,"data","Crops.csv")) as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                cropDict = {"cropRipe":int(row["ripeTime"]),"cropValue":int(row["cropValue"]),"cropHLabor":int(row["harvestLabor"]),"cropMLabor":int(row["maintainanceLabor"]),"cropColor":row["color"]}
                CROPDATA[row["Crop"]] = cropDict
        
    return CROPDATA
        

class Crop():
    '''Crop Class'''
    def __init__(self,farm,cropName,plantedTime):
        self.plantedTime = plantedTime
        self.cropName = cropName
        global CROPDATA
        self.farm = farm
        self.growUnits = 0
        self.maintained = False
        self.lastMaintain = 0
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

getCropData()