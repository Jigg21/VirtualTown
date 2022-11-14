from enum import Enum
import csv
ITEMS = None

def loadItemData():
    global ITEMS
    if ITEMS != None:
        return ITEMS
    else:
        ITEMS = {}
        with open('data\\Items.csv') as csvFile:
                reader = csv.DictReader(csvFile)
                for row in reader:
                    ITEMS[row["Name"]] = row
    return ITEMS

def getItemObj(id):
    return Item(id)

class Item():
    def __init__(self,ID) -> None:
        global ITEMS
        if ITEMS == None:
            loadItemData()
        self.category = ITEMS[ID]["Category"]
        self.bulk = ITEMS[ID]["Bulk"]

    def isEdible(self):
        '''checks if this item is edible'''
        return self.category == "FOOD"

loadItemData()