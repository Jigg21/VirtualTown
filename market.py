import math
import CargoItems
import csv
import random
from ConfigReader import ConfigData as config
import CONST
from NameGenerator import nameGenerator

class tradeOffer():
    def __init__(self,itemId,agent,amount=0) -> None:
        '''create a trade object to represent a buy offer'''
        self.item = CargoItems.getItemObj(itemId)
        self.agent = agent
        self.amount = amount
    
    def getAgent(self):
        return self.agent
    
    def __str__(self):
        return "{Agent} is selling {count} {item}s".format(Agent=self.agent.name,count=self.amount,item=self.item.ID)
        



class Market():
    '''an object to handle the market, including all the agents'''
    def __init__(self,itemList) -> None:
        self.offers = []
        self.agents = []
        self.items = itemList
        #generate the Libertariad
        self.itemsBaseLine = dict()
        for item in itemList:
            self.itemsBaseLine[item] = CargoItems.ITEMS[item]
        self.Liber = tradeAgent(self)
        self.Liber.name = "Libertariad"
        self.agents.append(self.Liber)
        #generate a number of random agents specified in config.ini
        for i in range(int(config["VALUES"]["TRADEAGENTS"])):
            newAgent = tradeAgent(self)
            self.agents.append(newAgent)
            newAgent.initRandom()

    def getLiberPrices(self,item):
        return self.itemsBaseLine[item]["Default_Value"]

    def newTradeOffer(self,offer):
        '''accept a new trade offer into the market, and returns the price dictionary'''
        self.offers.append(offer)

    def getTradeOffers(self):
        return self.offers

    def __str__(self) -> str:
        result = ""
        for a in self.agents:
            result += a.name
            result += str(a.needs)
            result += "\n"
            result += "Relations: ["
            for b in a.relations.keys():
                result += b.name
                result += ":"
                result += "("
                valueA = a.relations[b][0]
                valueB = a.relations[b][1]
                valueA = int(valueA*1000) / 1000
                valueB = int(valueB*1000) / 1000

                result += str(valueA) + "," + str(valueB)
                result += ")"
            result += "]\n"
        return result


class tradeAgent():
    '''class for how agents trade with one another'''
    def __init__(self,market) -> None:
        self.name=""
        self.market = market
        self.gold = 0
        self.econSize = 0
        #a dictionary of each trade agent : their relationship to each other
        self.relations = dict()
        #a dictionary of each item : this agent's need for it 
        self.needs = dict()
    
    def initRandom(self):
        '''completely randomizes the trade agent'''
        culture = random.choice(list(CONST.cultures))
        self.name = nameGenerator.getPlaceName(culture)
        self.gold = random.randrange(1000,10000)
        self.econSize =  random.randrange(100,500)
        
        for item in self.market.items:
            self.needs[item] = random.random()

        for agent in self.market.agents:
            #if the agent isn't itself, add a new relationship between them
            if agent != self:
                relationsNew = (random.uniform(-1,1),0)
                agent.setAgentRelations(self,relationsNew)
                self.setAgentRelations(agent,relationsNew)
    
    def setAgentRelations(self,agent,relations):
        self.relations[agent] = relations
    
    def alterAgentRelations(self,agent,change):
        relationsNew = (self.relations[agent][0] + change[0], self.relations[agent][1] + change[1])
        self.setAgentRelations(agent,relationsNew)

    def evaluateOffer(self,offer,otherAgent = None):
        '''evaluates the offer based on the other agent, returns tuple (cost per unit, number of units) '''
        if otherAgent == None:
            otherAgent = offer.getAgent()
        #get agent relations and calculate the relationship multiplier
        agentARelation = self.relations[otherAgent]
        agentBRelation = otherAgent.relations[self]
        relationVal = agentARelation[0] + agentBRelation[0]
        c = config.getfloat("MARKET","RELATIONSCONSTANT")
        relationMult = c * math.log(relationVal+2)+1.5

        #get the generic value of a good
        value = self.market.getLiberPrices(offer.item.ID)

        #determine the unit cost of an item
        unitCost = float(value) * relationMult
        unitCount = math.floor((self.needs[offer.item.ID] * self.econSize))

        #check if the original agent can sell the needed amount
        if unitCount > offer.amount:
            unitCount = offer.amount
        #check if the agent can afford the whole lot
        if unitCost * unitCount > self.gold:
            unitCount = math.floor(self.gold/unitCost)
        return (unitCost , unitCount)

    def addGold(self,amount):
        self.gold += 1
    
    def payGold(self,amount):
        if self.gold < amount:
            self.gold = 0
        else:
            self.gold -= amount
    def makeTrade(self,offer):
        '''accept an offer, make relavant changes to each agent'''
        itemValue = self.evaluateOffer(offer)
        saleValue = itemValue[0] * itemValue[1]
        offer.agent.addGold(saleValue)
        self.payGold(saleValue)
        offer.agent.alterAgentRelations(self,(0.1,0.01))
        self.alterAgentRelations(offer.agent,(0.1,0.01))

    



if __name__ == "__main__":
    cargoList = CargoItems.ITEMS.keys()
    mark = Market(cargoList)
    Libertariad = mark.agents[0]
    agentA = mark.agents[1]
    agentB = mark.agents[2]
    agentC = mark.agents[3]
    offer = tradeOffer("WOOD",agentA,amount=500)
    print(mark)
    print()
    print(offer)
    mark.newTradeOffer(offer)
    buyOfferB = agentB.evaluateOffer(offer)
    buyOfferC = agentC.evaluateOffer(offer)
    print("{Name} would buy {count} {offer} for {value} each".format(Name=agentB.name,count=buyOfferB[1],offer=offer.item.ID,value = buyOfferB[0]))
    print("{Name} would buy {count} {offer} for {value} each".format(Name=agentC.name,count=buyOfferC[1],offer=offer.item.ID,value = buyOfferC[0]))
    agentC.makeTrade(offer)
    print("{Name} bought {count} {offer} for {value} total".format(Name=agentC.name,count=buyOfferC[1],offer=offer.item.ID,value = buyOfferC[0]*buyOfferC[1]))
    print()
    print(mark)