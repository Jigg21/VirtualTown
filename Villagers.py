from ConfigReader import ConfigData as config
from CONST import TaskStatus, VillagerStates
from BehaviorTree import BT
import math

from VillagerNodes import tree_HungerSatisfactionTree, tree_workTree
class Task:
    '''base class for all tasks villagers can do'''

    def __init__(self,function,labor,location,desc="Task",pay=0,workArgs=[]):
        self.function = function
        self.desc = desc
        self.pay = pay
        self.laborReq = labor
        self.functionArgs = workArgs
        self.location = location
        self.assignedVillager = None
        self.state = TaskStatus.WAITING
        

    def work(self,villager):
        '''do the task'''
        self.laborReq -= 1
        if (self.laborReq <= 0):
            self.function(*self.functionArgs)
            self.completed = True
            
    
    def isCompleted(self):
        return self.completed

    def __str__(self):
        return "({location}){desc} for {pay} gold, {labor} work left".format(location=self.location.buildingName, desc=self.desc,pay=self.pay,labor=self.laborReq)      

class coopTask(Task):
    '''Tasks involving multiple villagers'''
    def __init__(self, function, labor, location, reqVillagers, desc="Task", pay=0, workArgs=[]):
        super().__init__(function, labor, location, desc, pay, workArgs)
        self.reqVillagers = reqVillagers
    
    def work(self, villager):
        if self.state == TaskStatus.WAITING:
            if villager.state != VillagerStates.READY:
                villager.changeState(VillagerStates.READY)
                villager.goTo(self.location)
                self.reqVillagers += 1
    
                

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
        return self.activeTasks.pop()
    
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

    def __init__(self,name,age,gender,startLocation,town):
        '''name: villager name\n
        age: defaults to 0'''
        self.vAge = age
        self.vGender = gender
        self.vName = name
        self.ID = 0
        self.currentLocation = startLocation
        self.currentLocation.add_occupant(self)
        self.town = town
        self.vTask = None
        self.vHunger = 100
        self.vState = VillagerStates.IDLE
        self.vMoney = 10
        self.offWork = False
        self.experience = 0
        self.RelationShips = {self:0}
        #set up behavior tree
        self.behaviorTree = BT.Tree(BT.SequenceNode("ROOT NODE"))
        self.behaviorTree.addNodetoRoot(tree_HungerSatisfactionTree())
        self.behaviorTree.addNodetoRoot(tree_workTree()) 

    #called once a tick
    def update(self):

        self.vHunger -= .208
        self.currentLocation.activate(self)
        #assemble context and traverse behavior tree
        context = {}
        context["villager"] = self
        context["town"] = self.town
        context["board"] = self.town.bulletin
        context["Verbose"] = config.getboolean("DEBUG","BTVerbose")
        self.behaviorTree.traverse(context)

    def changeState(self,newState):
        '''change the villagers state'''
        self.vState = newState
    
    def eat(self,amount):
        '''Replenish hunger by amount'''
        self.vHunger += amount
        if (self.vHunger > 100):
            self.vHunger = 100
    
    #complete job and get paid
    def finishWork(self):
        self.offWork = True
        self.vState = VillagerStates.IDLE
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
    
    #go to work
    def goWork(self):
        if (self.currentLocation != self.vTask.location):
            self.goTo(self.vTask.location)
        self.vState = VillagerStates.WORKING

    
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
        self.vState = VillagerStates.HOSPITALIZED
    
    def gainRelation(self,otherVillager,amount):
        '''gain amount of friendship with otherVillager'''
        self.RelationShips[otherVillager] += amount

    #string representation
    def __str__(self):
        result = self.vName
        result += " ({age}/{gender})".format(age=self.vAge,gender=self.vGender)
        result += " Hunger: {hunger}".format(hunger = math.floor(self.vHunger))
        result += " Money: {money}".format(money=self.vMoney)
        result += " EXP: {exp}".format(exp=self.experience)
        result += "State: {state}".format(state = str(self.vState))
        result += "Task: {task}".format(task=str(self.vTask))
        return result

