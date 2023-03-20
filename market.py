import math
import CargoItems
import csv
import random
from ConfigReader import ConfigData as config
import CONST
from NameGenerator import nameGenerator

class tradeOffer():
    def __init__(self,itemId,agent) -> None:
        '''create a trade object to represent a buy offer'''
        self.item = CargoItems.getItemObj(itemId)
        self.agent = agent
    
    def getAgent(self):
        return self.agent
        
        
class Market():
    '''an object to handle the market, including all the agents'''
    def __init__(self,itemList) -> None:
        self.offers = []
        self.agents = []
        self.items = itemList
        #generate the Libertariad
        self.itemsBaseLine = dict()
        self.Liber = tradeAgent(self)
        self.agents.append(self.Liber)
        #generate a number of random agents specified in config.ini
        for i in range(int(config["VALUES"]["TRADEAGENTS"])):
            newAgent = tradeAgent(self)
            self.agents.append(newAgent)
            newAgent.initRandom()

    def getLiberPrices(self,item):
        return self.itemsBaseLine[item]

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
        #a dictionary of each trade agent : their relationship to each other
        self.relations = dict()
        #a dictionary of each item : this agent's need for it 
        self.needs = dict()
    
    def initRandom(self):
        '''completely randomizes the trade agent'''
        culture = random.choice(list(CONST.cultures))
        self.name = nameGenerator.getPlaceName(culture)
        
        for item in self.market.items:
            self.needs[item] = random.random()
        for agent in self.market.agents:
            relationsNew = (random.random(),random.random())
            agent.setAgentRelations(self,relationsNew)
            self.setAgentRelations(agent,relationsNew)
    
    def setAgentRelations(self,agent,relations):
        self.relations[agent] = relations
    
    def alterAgentRelations(self,agent,relations):
        relationsNew = (self.relations[0] + relations[0], self.relations[1] + relations[1])
        agent.setAgentRelations(self,relationsNew)
        self.setAgentRelations(agent,relationsNew)

    def evaluateOffer(self,offer):
        '''evaluates the offer based on the other agent  '''
        otherAgent = offer.getAgent()
        #get agent relations and calculate the relationship multiplier
        agentARelation = self.relations[otherAgent]
        agentBRelation = otherAgent.relations[self.agent]
        relationVal = agentARelation + agentBRelation
        c = config.getfloat("MARKET","RELATIONSCONSTANT")
        relationMult = c * math.log(relationVal+2)+1.5

        #get agent needs



        



if __name__ == "__main__":
    cargoList = CargoItems.ITEMS.keys()
    mark = Market(cargoList)
    agentA = mark.agents[1]
    agentB = mark.agents[2]
    offer = tradeOffer("RICE_BEER",agentA)
    print(mark)
    print()
    mark.newTradeOffer(offer)
    print(agentA.evaluateOffer(offer))
    print(mark) 