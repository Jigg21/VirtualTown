import CargoItems
import csv

class tradeOffer():
    def __init__(self,itemId) -> None:
        '''create a trade object to represent a buy offer'''
        self.item = CargoItems.getItemObj(itemId)
        

class Market():
    '''an object to handle the market, including all the agents'''
    def __init__(self) -> None:
        self.offers = []
        self.agents = []
        self.itemsBaseLine = dict()

    def newTradeOffer(self,offer):
        '''accept a new trade offer into the market, and returns the price dictionary'''
        self.offers.append(offer)
        for agnt in self.agents:
            agnt.evaluateOffer(offer)

class tradeAgent():
    '''class for how agents trade with one another'''
    def __init__(self) -> None:
        self.gold = 0
        #a dictionary of each trade agent : their relationship to each other
        self.relations = dict()
        #a dictionary of each item : this agent's need for it 
        self.needs = dict()
        #get a few 
        with open('data\\defaultAgents.csv') as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                row["Name"] = 

    def evaluateOffer(self,offer):
        '''evaluates the '''
        pass
