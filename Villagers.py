from ConfigReader import ConfigData as config
from VillagerNodes import tree_VillagerBehaviorTree
from NameGenerator import nameGenerator
from BehaviorTree import BT
import CONST
import math
import Utilities
import Familes
#villager class
class Villager:

    def __init__(self,name,birthCycle,gender,**kwargs):
        '''name: villager name\n
        age: defaults to 0'''
        self.vName = name
        self.vBirthCycle = birthCycle
        self.vGender = gender

        #parse keyword arguments

        if "family" in kwargs.keys():
            self.vFamily = kwargs["family"]
        else:
            self.vFamily = Familes.Family()

        if "town" in kwargs.keys():
            self.town = kwargs["town"] 

        if "startLocation" in kwargs.keys():
            self.currentLocation = kwargs["startLocation"]
            self.currentLocation.addOccupant(self)
        else:
            self.currentLocation = self.town.getTownHall()
            self.currentLocation.addOccupant(self)

        if "home" in kwargs.keys():
            self.currentLocation = kwargs["home"]
            self.home = kwargs["home"]
        else:
            self.home = None


        
        self.vName += " " + self.vFamily.fName
        #where the villager currently is

        self.vTask = None
        self.vHunger = 100
        self.vState = CONST.VillagerStates.IDLE
        self.vMoney = 10
        self.vHealth = 100
        self.vEnergy = 1000
        self.alive = True
        self.offWork = False
        self.experience = 0
        self.Relationships = {}
        self.romancable = True
        self.romanceCoolDown = 0
        #set up behavior tree
        self.behaviorTree = tree_VillagerBehaviorTree(BT.SequenceNode("ROOT NODE"))
        self.vDrunkeness = 0

    #called once a tick
    def update(self):
        self.checkAlive()
        if self.alive:
            if self.vState != CONST.VillagerStates.SLEEPING and self.vState != CONST.VillagerStates.DEAD:
                self.vHunger -=  config.getfloat("PASSENGERS","HUNGERDRAIN")
            else:
                self.vHunger -=  .25 * config.getfloat("PASSENGERS","HUNGERDRAIN")

            if self.vHunger <= 0:
                self.vHealth -= config.getfloat("PASSENGERS","HUNGERDEATH")
            if self.vHunger > 25 and self.vHealth < 100:
                self.vHealth += self.vHunger-25/100 * config.getfloat("PASSENGERS","HEALRATE")
            self.currentLocation.activate(self)
            #assemble context and traverse behavior tree
            context = {}
            context["villager"] = self
            context["town"] = self.town
            context["board"] = self.town.bulletin
            context["Verbose"] = config.getboolean("DEBUG","BTVerbose")
            self.behaviorTree.traverse(context)
            if self.vState == CONST.VillagerStates.SLEEPING:
                self.vHunger = Utilities.clamp(-100,100,self.vHunger)
                self.vHealth = Utilities.clamp(0,100,self.vHealth)

            self.vHunger = Utilities.clamp(-100,100,self.vHunger)
            self.vHealth = Utilities.clamp(0,100,self.vHealth)
            self.vDrunkeness -= .25
            self.vDrunkeness = Utilities.clamp(0,100,self.vDrunkeness)

            if not self.romancable:
                self.romanceCoolDown -= 1
                if self.romanceCoolDown <= 0:
                    self.romancable = True

    def checkAlive(self):
        '''Check if the villager is alive'''
        if self.vHealth <= 0:
            self.alive = False
            self.changeState(CONST.VillagerStates.DEAD)
            return False
        return self.alive
            
    def changeState(self,newState):
        '''change the villagers state'''
        self.vState = newState
    
    def eat(self,amount):
        '''Replenish hunger by amount'''
        self.vHunger += amount
        if (self.vHunger > 100):
            self.vHunger = 100
    
    def finishWork(self):
        '''complete job and get paid'''
        self.offWork = True
        self.vState = CONST.VillagerStates.IDLE
        self.experience += 1
        self.makeMoney(self.vTask.pay)
        self.vTask = None
   
    def goTo(self,location):
        '''sends villager to location and removes it it's current location'''
        self.currentLocation.removeOccupant(self)
        self.currentLocation = location
        self.currentLocation.addOccupant(self)
    
    def goEat(self):
        '''Go to a restuarant if the villager is not already there'''
        if self.currentLocation.bClass != CONST.buildingClass.RESTAURANT:
            self.goTo(self.town.FindBuilding(CONST.buildingClass.RESTAURANT))    
    
    def goSleep(self):
        '''sends the villager to sleep'''
        self.goToBuildingType(CONST.buildingClass.TOWNHALL)
        if self.vEnergy >= 1000:
            self.vEnergy = 1000
            return True
        else:
            self.vEnergy += 2
            self.vState = CONST.VillagerStates.SLEEPING
            return False

    def goToBuildingType(self,bType):
        '''Go to a building of type btype, in the case of multiples it will go to the first'''
        if (not self.currentLocation.isClassOf(bType)):
            for b in self.town.buildings:
                if b.isClassOf(bType):
                    self.goTo(b)
                    return True
            else:
                return False
        else:
            return True
    
    #go to work
    def goWork(self):
        if (self.currentLocation != self.vTask.location):
            self.goTo(self.vTask.location)
        self.vState = CONST.VillagerStates.WORKING
    
    def makeSalary(self,amount):
        '''make salary by charging the treasury'''
        self.vMoney += amount
    
    #get money without changing the treasury
    def makeMoney(self,amount):
        self.vMoney += amount
    
    #can the villager afford this amount
    def canAfford(self,amount):
        return self.vMoney > amount

    #spend the money
    def spendMoney(self,amount):
        self.vMoney -= amount

    #perform one labor on the current task
    def work(self):
        if self.vTask is not None:
            if self.vEnergy > 0:
                self.vEnergy -= 1
                self.vTask.work(self)
                if self.vTask.isComplete():
                    self.finishWork()
                    return True
        return False
    
    #does the villager have something to do
    def hasWork(self):
        return self.vTask != None
    
    #assign what the villager must do
    def getWork(self,task):
        self.vTask = task
    
    #When the villager has been hospitalized
    def hospitalize (self):
        self.vState = CONST.VillagerStates.HOSPITALIZED
    
    def changeRelation(self,otherVillager,amount):
        '''gain amount of friendship with otherVillager'''
        if otherVillager in self.Relationships.keys():
            self.Relationships[otherVillager] += amount
            #if above a certain level and open to romance, attempt a romance
            if self.Relationships[otherVillager] > config.getint("PASSENGERS","ROMANCETHRESH") and self.romancable:
                self.romanceVillager(otherVillager)
        else:
            self.Relationships[otherVillager] = amount

    def romanceVillager(self,otherVillager):
        '''attempt a romantic relationship with another villager'''
        #if both parties are high enough relationship
        if self.reciprocatesRomance(otherVillager) and otherVillager.reciprocatesRomance(self):
            self.town.addVillager(Villager(nameGenerator.makeName(),  25,'M',self.vFamily,self.currentLocation,self.town))
        else:
            #otherwise the villager loses 100 relation 
            self.changeRelation(otherVillager, -100)
            self.rejectedRomance(otherVillager)
    
    def rejectedRomance(self,otherVillager):
        self.romancable = False
        self.romanceCoolDown = 10000

    def reciprocatesRomance(self,otherVillager):
        '''checks if the villager loves the other back'''
        thresh = config.getint("PASSENGERS","ROMANCETHRESH")
        if self.Relationships[otherVillager] >= thresh:
            self.rejectedRomance(otherVillager)
        return self.Relationships[otherVillager] >= thresh
    
    def drink(self): 
        self.vDrunkeness += 1
    
    def changeFamily(self,newFamily):
        self.vFamily = newFamily

    #string representation
    def __str__(self):
        result = self.vName 
        result += " ({age}/{gender})".format(age=self.vBirthCycle,gender=self.vGender)
        result += " Hunger: {hunger}".format(hunger = math.floor(self.vHunger))
        result += " Health: {health}".format(health=math.floor(self.vHealth))
        result += " Energy: {energy}".format(energy=self.vEnergy)
        result += " EXP: {exp}".format(exp=self.experience)
        result += "State: {state}".format(state = str(self.vState)[15:])
        result += "Task: {task}".format(task=str(self.vTask))
        return result



