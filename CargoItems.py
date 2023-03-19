import csv
import os

FILEPATH = os.getcwd()
ITEMS = None

def loadItemData():
    '''load the item data from file'''
    global ITEMS
    if ITEMS != None:
        return ITEMS
    else:
        ITEMS = {}
        with open(os.path.join(FILEPATH,"data","Items.csv")) as csvFile:
                reader = csv.DictReader(csvFile)
                for row in reader:
                    ITEMS[row["Name"]] = row
    return ITEMS

def getItemObj(id):
    return cargoItem(id)

class cargoItem():
    '''class for cargo items when they are being handled'''
    def __init__(self,ID) -> None:
        global ITEMS
        if ITEMS == None:
            loadItemData()
        self.ID = ID
        self.category = ITEMS[ID]["Category"]
        self.bulk = ITEMS[ID]["Bulk"]

    def isEdible(self):
        '''checks if this item is edible'''
        return self.category == "FOOD"

loadItemData()