from enum import Enum
import math
#base class for all tasks passengers can do
class Task:
    function = None
    pay = 0
    desc = "Task"
    laborReq = 0
    completed = False
    functionArgs = []
    assignedVillager = None
    location = None
    def __init__(self,function,labor,location,desc="Task",pay=0,workArgs=[]):
        self.function = function
        self.desc = desc
        self.pay = pay
        self.laborReq = labor
        self.functionArgs = workArgs
        self.location = location


    def work(self,villager):
        self.laborReq -= 1
        if (self.laborReq <= 0):
            self.function(*self.functionArgs)
            self.completed = True
            villager.makeSalary(self.pay)
    
    def isCompleted(self):
        return self.completed

    def __str__(self):
        return "({location}){desc} for {pay} gold, {labor} work left".format(location=self.location.buildingName, desc=self.desc,pay=self.pay,labor=self.laborReq)

#use to give jobs to passengers
class bulletinBoard():
    def __init__(self):
        self.activeTasks = []
    
    #assigns a job to the given passenger
    def assignJob(self, passenger):
        return self.activeTasks.pop()
    
    #adds a task to the board
    def postJob(self,task,townHall):
        if townHall.spendTreasury(task.pay):
            self.activeTasks.append(task)

    #returns true if the bulletin board has any active tasks
    def hasWork(self):
        return len(self.activeTasks) > 0

    def getTaskList(self):
        result = ""
        for t in self.activeTasks:
            result += str(t) + "\n"
        return result

#enum of villager AI states
class VillagerStates(Enum):
    IDLE = 1
    EATING = 2
    WORKING = 3
    HOSPITALIZED = 4

#villager class
class townsperson:

    def __init__(self,name,age,gender,startLocation,town):
        '''name: villager name\n
        age: defaults to 0'''
        self.vAge = age
        self.vGender = gender
        self.vName = name
        self.currentLocation = startLocation
        self.currentLocation.add_occupant(self)
        self.town = town
        self.vTask = None
        self.vHunger = 100
        self.vState = VillagerStates.IDLE
        self.vMoney = 10
        self.offWork = False
        self.experience = 0

    #called once a tick
    def update(self):

        self.vHunger -= .208
        self.currentLocation.activate(self)
        if (self.vHunger < 10 and not self.town.townHall.starving):
            self.vState = VillagerStates.EATING
            self.goEat()
        elif self.vState == VillagerStates.IDLE:
                if self.town.bulletin.hasWork():
                    self.vTask = self.town.bulletin.assignJob(self)
                    self.goWork()
                    self.vState = VillagerStates.WORKING
                else:
                    self.goTo(self.town.townHall)
        elif self.vState == VillagerStates.WORKING:
                self.work()     
        elif self.vState == VillagerStates.EATING:
                if (self.vHunger > 95):
                    self.vState = VillagerStates.IDLE


    #replenish hunger
    def eat(self,amount):
        self.vHunger += amount
        if (self.vHunger > 100):
            self.vHunger = 100
    
    #complete all jobs and get paid
    def finishWork(self):
        self.offWork = True
        self.vState = VillagerStates.IDLE
        self.experience += 1
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
