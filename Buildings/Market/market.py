import math
import Buildings.Market.CargoItems as CargoItems
import csv
import random
from Utilities.ConfigReader import ConfigData as config
from Utilities import CONST
from NameGenerator import nameGenerator

class tradeOffer():
    def __init__(self,itemId,agent,amount=0) -> None:
        '''create a trade object to represent a buy offer'''
        self.item = CargoItems.getItemObj(itemId)
        self.agent = agent
        self.amount = amount
    
    def getAgent(self):
        return self.agent
    
    def sell(self, amount):
        '''removes an amount of the item and returns how much is left on the offer'''
        self.amount -= amount
        if self.amount >= 0:
            return self.amount
        else:
            return 0
    
    def __str__(self):
        return "{Agent} is selling {count} {item}s".format(Agent=self.agent.name,count=self.amount,item=self.item.ID)
        
class Market():
    '''an object to handle the market, including all the agents'''
    def __init__(self,itemList,agentList=None) -> None:
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
        
        if agentList == None:
            #generate a number of random agents specified in config.ini
            for i in range(int(config["VALUES"]["TRADEAGENTS"])):
                newAgent = tradeAgent(self)
                self.agents.append(newAgent)
                newAgent.initRandom()
        else:
            self.agents = agentList
    
    def getLiberPrices(self,item):
        return self.itemsBaseLine[item]["Default_Value"]

    def newTradeOffer(self,offer):
        '''accept a new trade offer into the market, and returns the price dictionary'''
        self.offers.append(offer)

    def getTradeOffers(self):
        return self.offers

    def DailyUpdate(self):
        '''update the market for a new day, closes outstanding deals'''
        currentOffers = self.getTradeOffers()
        bestPrices = dict()
        #for each agent, make deals and update needs/gold
        for agent in self.agents:
            #make deals for items
            for need in agent.needs:
                #if the agent needs the item
                if agent.needs[need] > 0:
                    #get the best offer
                    for offer in currentOffers:
                        if offer.item == need:
                            evaluation = agent.evaluateOffer(offer)
                            if offer.item in bestPrices:
                                if evaluation[0] < bestPrices[offer.item]:
                                    bestPrices[offer.item] = offer
            
            #then update the needs and gold
            


    def makeTrade(self,offer,buyer):
        '''make a trade and reverberate that through the market'''
        #get trade values
        seller = offer.getAgent()
        item = offer.item
        buyerValue,itemCount = buyer.evaluateOffer(offer)
        saleValue = buyerValue * itemCount

        #make the sale/purchase
        seller.makeSale(item,itemCount,saleValue)
        buyer.makePurchase(item,itemCount,saleValue)

        #update the relationships
        buyer.alterAgentRelations(seller,(0.1,0.01))

    def __str__(self) -> str:
        result = ""
        for a in self.agents:
            result += a.name
            result += "Gold: {gold} ".format(gold=a.gold)
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
        #a dictionary of each item : this agent's need for it Austin, TX
        self.needs = dict()
        #construct the agent's production dictionary
        self.agentType = None
        self.production = dict()
    
    def initRandom(self):
        '''completely randomizes the trade agent'''
        culture = random.choice(list(CONST.cultures))
        self.name = nameGenerator.getPlaceName(culture)
        self.gold = random.randrange(1000,10000)
        self.econSize =  random.randrange(100,500)
        self.agentType = random.choice(list(CONST.VillageTypes))

        #generate needs and production 
        for item in self.market.items:
            #initialize a random starting need/surplus for each item
            self.needs[item] = random.uniform(-1,1)
            item = CargoItems.getItemObj(item)

            #construct the production dictionary 
            if  item.subcategory == "PROCCESSED_FOOD":
                if self.agentType == CONST.VillageTypes.AGRICULTURAL:
                    self.production[item] = random.random()
                if self.agentType == CONST.VillageTypes.CULTURE:
                    self.production[item] = -random.random()
                if self.agentType == CONST.VillageTypes.MILITANT:
                    self.production[item] = -random.random()
            
            if item.subcategory == "CROP":
                if self.agentType == CONST.VillageTypes.AGRICULTURAL:
                    self.production[item] = random.random()
                if self.agentType == CONST.VillageTypes.INDUSTRIOUS:
                    self.production[item] = -random.random()

            if item.subcategory == "DELICACY":
                pass

            if item.subcategory == "ORE":
                pass
            
            if item.subcategory == "RAW_MATERIALS":
                if self.agentType == CONST.VillageTypes.INDUSTRIOUS:
                    self.production[item] = -random.random()
                if self.agentType == CONST.VillageTypes.MILITANT:
                    self.production[item] = random.random()
                pass
                
            if item.subcategory == "RESOURCE":
                if self.agentType == CONST.VillageTypes.ENERGISTIC:
                    self.production[item] = -random.random()
                if self.agentType == CONST.VillageTypes.INDUSTRIOUS:
                    self.production[item] = -random.random()
                pass
                
            if item.subcategory == "FUEL":
                if self.agentType == CONST.VillageTypes.ENERGISTIC:
                    self.production[item] = random.random()
                if self.agentType == CONST.VillageTypes.MILITANT:
                    self.production[item] = -random.random()
                pass
                
            if item.subcategory == "MEDICAL":
                pass

            if item.subcategory == "CONSUMER":
                if self.agentType == CONST.VillageTypes.AGRICULTURAL:
                    self.production[item] = -random.random()
                if self.agentType == CONST.VillageTypes.ENERGISTIC:
                    self.production[item] = -random.random()
                if self.agentType == CONST.VillageTypes.INDUSTRIOUS:
                    self.production[item] = random.random()

            if item.subcategory == "TOOLS":
                if self.agentType == CONST.VillageTypes.AGRICULTURAL:
                    self.production[item] = -random.random()
                if self.agentType == CONST.VillageTypes.INDUSTRIOUS:
                    self.production[item] = random.random()
                if self.agentType == CONST.VillageTypes.MILITANT:
                    self.production[item] = random.random()
                pass

            if item.subcategory == "MEDIA":
                pass

            if item.subcategory == "INDUSTRIAL":
                pass

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
        '''evaluates the offer, returns tuple (cost per unit, number of units) '''
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
        '''gain gold'''
        self.gold += 1
    
    def payGold(self,amount):
        '''lose gold'''
        if self.gold < amount:
            self.gold = 0
        else:
            self.gold -= amount
    
    def makePurchase(self,item,count,value):
        '''make changes to the agent to buy an item '''
        self.needs[item.ID] -= count/self.econSize
        self.payGold(value)
        self.econSize += 1
        pass
    
    def makeSale(self,item,count,value):
        '''make changes to the agent to sell an item'''
        self.needs[item.ID] += count/self.econSize
        self.addGold(value)
        self.econSize += 1
        pass

    def produce(self):
        for item in self.needs:
            self.needs[item] += self.production[item]
            if self.needs[item] > 1: 
                self.needs[item] = 1
            if self.needs[item] < -1:
                self.needs[item] = -1
        
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
    mark.DailyUpdate()
    print()
    print(mark)
    print()
    buyOfferB = agentB.evaluateOffer(offer)
    buyOfferC = agentC.evaluateOffer(offer)
    print("{Name} would buy {count} {offer} for {value} each".format(Name=agentB.name,count=buyOfferB[1],offer=offer.item.ID,value = buyOfferB[0]))
    print("{Name} would buy {count} {offer} for {value} each".format(Name=agentC.name,count=buyOfferC[1],offer=offer.item.ID,value = buyOfferC[0]))
