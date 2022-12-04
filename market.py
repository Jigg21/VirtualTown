import CargoItems
import csv

class tradeOffer():
    def __init__(self,id,isSale,p) -> None:
        '''create a trade object to represent a buy order'''
        self.item = CargoItems.getItemObj(id)
        self.cost = 0    

class Market():
    '''an object to handle the market'''
    def __init__(self) -> None:
        self.items = []
        self.agents = []


class tradeAgent():
    '''class for how agents trade with one another'''
    def __init__(self) -> None:
        self.gold = 0
        self.relations = dict()
        with open('data\\defaultAgents.csv') as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                row["Name"] = row

def getItemCost() -> int:
    pass

def sellItem() -> int:
    pass

def buyItem() -> str:
    pass