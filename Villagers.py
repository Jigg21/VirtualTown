from email.parser import BytesParser
from ConfigReader import ConfigData as config
import CONST
from BehaviorTree import BT
import math
from VillagerNodes import tree_VillagerBehaviorTree
import Utilities


class Task:
    '''base class for all tasks villagers can do'''

    def __init__(self,function,labor,location,desc="Task",pay=0,workArgs=[]):
        #the function to be done when the task is complete
        self.function = function
        self.desc = desc
        self.pay = pay
        self.laborReq = labor
        self.functionArgs = workArgs
        self.location = location
        self.assignedVillager = None
        self.state = CONST.TaskStatus.WAITING
        self.coop = False

    def work(self,villager):
        '''do the task'''
        if self.state == CONST.TaskStatus.WAITING:
            self.state = CONST.TaskStatus.INPROGRESS
        if self.state == CONST.TaskStatus.INPROGRESS:
            self.laborReq -= 1
            if (self.laborReq <= 0):
                self.function(*self.functionArgs)
                self.state = CONST.TaskStatus.COMPLETED
    
    def isWaiting(self):
        '''Returns true if task is in state WAITING'''
        return self.state == CONST.TaskStatus.WAITING
    
    def isComplete(self):
        '''Returns true if task is complete'''
        if (self.laborReq <= 0):
            self.function(*self.functionArgs)
            self.state = CONST.TaskStatus.COMPLETED
        return self.state == CONST.TaskStatus.COMPLETED

    def isCompleted(self):
        return self.completed

    def __str__(self):
        return "({location}){desc} for {pay} gold, {labor} work left".format(location=self.location.buildingName, desc=self.desc,pay=self.pay,labor=self.laborReq)      

class coopTask(Task):
    '''Tasks involving multiple villagers'''
    def __init__(self, function, labor, location, reqVillagers, desc="Task", pay=0, workArgs=[]):
        super().__init__(function, labor, location, desc, pay, workArgs)
        self.reqVillagers = reqVillagers
        self.currentVillagers = 0
        self.coop = True

    def work(self, villager):
        if self.state == CONST.TaskStatus.WAITING:
            if villager.state != CONST.VillagerStates.READY:
                villager.changeState(CONST.VillagerStates.READY)
                villager.goTo(self.location)
                self.currentVillagers += 1
            if self.reqVillagers <= self.currentVillagers:
                self.state == CONST.TaskStatus.INPROGRESS
                super().work(villager)

class bulletinBoard():
    '''use to give jobs to villagers'''
    def __init__(self):
        self.activeTasks = []
        self.taskCount = 0
    
    #assigns a job to the given villager
    def assignJob(self, villager):
        self.taskCount -= 1
        task = self.activeTasks.pop()
        villager.getWork(task)
        try:
            return self.activeTasks.pop()
        except:
            return None
    
    #adds a task to the board
    def postJob(self,task,townHall):
        if townHall.spendTreasury(task.pay):
            self.activeTasks.append(task)
            self.taskCount += 1

    #returns true if the bulletin board has any active tasks
    def hasWork(self):
        return len(self.activeTasks) > 0

    def getTaskList(self):
        result = ""
        for t in self.activeTasks:
            result += str(t) + "\n"
        return result

#villager class
class townsperson:

    def __init__(self,name,birthCycle,gender,startLocation,town,family):
        '''name: villager name\n
        age: defaults to 0'''
        self.vBirthCycle = birthCycle
        self.vGender = gender
        self.vName = name
        self.ID = 0
        self.currentLocation = startLocation
        self.currentLocation.add_occupant(self)
        self.town = town
        self.vTask = None
        self.vHunger = 100
        self.vState = CONST.VillagerStates.IDLE
        self.vMoney = 10
        self.vHealth = 100
        self.alive = True
        self.offWork = False
        self.experience = 0
        self.Relationships = {}
        #set up behavior tree
        self.behaviorTree = tree_VillagerBehaviorTree(BT.SequenceNode("ROOT NODE"))

    #called once a tick
    def update(self):
        self.checkAlive()
        if self.alive:
            self.vHunger -=  config.getfloat("PASSENGERS","HUNGERDRAIN")
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
            self.vHunger = Utilities.clamp(-100,100,self.vHunger)
            self.vHealth = Utilities.clamp(0,100,self.vHealth)

    def checkAlive(self):
        '''Check if the villager is alive'''
        if self.vHealth <= 0:
            self.alive = False
            self.changeState(CONST.VillagerStates.DEAD)
            
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
        self.currentLocation.remove_occupant(self)
        self.currentLocation = location
        self.currentLocation.add_occupant(self)
    
    def goEat(self):
        '''Go to a restuarant if the villager is not already there'''
        if self.currentLocation != self.town.getRestaurant():
            self.goTo(self.town.getRestaurant())    
    

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
            self.vTask.work(self)
            if self.vTask.completed:
                self.finishWork()
    
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
        else:
            self.Relationships[otherVillager] = amount

    #string representation
    def __str__(self):
        result = self.vName
        result += " ({age}/{gender})".format(age=self.vBirthCycle,gender=self.vGender)
        result += " Hunger: {hunger}".format(hunger = math.floor(self.vHunger))
        result += " Health: {health}".format(health=math.floor(self.vHealth))
        result += " Money: {money}".format(money=self.vMoney)
        result += " EXP: {exp}".format(exp=self.experience)
        result += "State: {state}".format(state = str(self.vState))
        result += "Task: {task}".format(task=str(self.vTask))
        return result

