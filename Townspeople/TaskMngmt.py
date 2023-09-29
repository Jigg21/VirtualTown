from Utilities import CONST

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
    def __init__(self,ship):
        self.activeTasks = []
        self.taskCount = 0
        self.ship = ship
    
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
    def postJob(self,task):
        if self.ship.spendTreasury(task.pay):
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
    
    def getTaskRefund(self):
        result = 0
        for t in self.activeTasks:
            result += t.pay
        return result
