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
        return "({location}){desc} for {pay} gold, {labor} work left".format(location=self.location, desc=self.desc,pay=self.pay,labor=self.laborReq)


#enum of villager AI states
class VillagerStates(Enum):
    IDLE = 1
    EATING = 2
    WORKING = 3

#villager class
class townsperson:
    vName = ""
    vAge = 0
    vGender = 'M'
    currentLocation = None
    vHunger = 100
    town = None
    vState = VillagerStates.IDLE
    job = None
    vMoney = 10
    vTask = None
    offWork = False
    experience = 0
    def __init__(self,name,age,gender,startLocation,town):
        self.vAge = age
        self.vGender = gender
        self.vName = name
        self.currentLocation = startLocation
        self.currentLocation.add_occupant(self)
        self.town = town
        self.vTask = None

    #called once a tick
    def update(self):
        self.vHunger -= .208
        self.currentLocation.activate(self)
        if (self.vHunger < 10):
            self.vState = VillagerStates.EATING
            self.goEat()
        match self.vState:
            case VillagerStates.IDLE:
                if self.town.bulletin.hasWork():
                    self.vTask = self.town.bulletin.assignJob(self)
                    self.goWork()
                    self.vState = VillagerStates.WORKING
                else:
                    self.goTo(self.town.townHall)
                    
            case VillagerStates.WORKING:
                self.work()
                
            case VillagerStates.EATING:
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

    #Go to location
    def goTo(self,location):
        self.currentLocation.remove_occupant(self)
        self.currentLocation = location
        self.currentLocation.add_occupant(self)

    #go to a restaurant
    def goEat(self):
        self.goTo(self.town.getRestaurant())
    
    #go to work
    def goWork(self):
        if (self.currentLocation != self.vTask.location):
            self.goTo(self.vTask.location)
        self.vState = VillagerStates.WORKING

    #make salary by charging the treasury
    def makeSalary(self,amount):
        hall = self.town.getTownHall()
        hall.spendTreasury(amount)
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
