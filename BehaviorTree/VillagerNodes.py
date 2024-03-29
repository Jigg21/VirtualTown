from BehaviorTree import BT
from Utilities import CONST

#TODO: make a formal Test function for test tree
class TestNode_ConstantState(BT.Node):
    '''Testing node that always returns a certain state'''
    def __init__(self,state,desc="") -> None:
        super().__init__(desc)
        self.returnState = state
    
    def activate(self,context):
        super().activate(context)
        return self.returnState

class TestNode_PrintMessage(BT.Node):
    def __init__(self,message) -> None:
        super().__init__()
        self.message = message
    
    def activate(self,context):
        print(self.message)
        return BT.nodeStates.SUCCESS

class TestTree(BT.Tree):
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(BT.SequenceNode(desc="Main Sequence Loop"))
        
        testnode2 = TestNode_ConstantState(BT.nodeStates.FAILED,desc="RETURNING FAILURE")
        testdec = BT.NegateDecorator()
        self.addNodetoRoot(testdec)
        testnode = TestNode_PrintMessage("Starting")
        self.addNode(testnode,testdec)
        self.addNodetoRoot(testnode2)
        self.addNodetoRoot(TestNode_PrintMessage("DONE"))

class node_villagerInState(BT.Node):

    def __init__(self,state,desc="") -> None:
        '''returns success if the villager is in state'''
        super().__init__(desc)
        self.state = state
    
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        if context["villager"].vState == self.state:
            return BT.nodeStates.SUCCESS
        else:
            return BT.nodeStates.FAILED

class node_setVillagerState(BT.Node):
    '''set a villagers state to some predetermined state, returns result defaults to SUCCESS'''
    def __init__(self, state,result = BT.nodeStates.SUCCESS,desc="") -> None:
        super().__init__(desc)
        self.state = state
        self.result = result

    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        context["villager"].changeState(self.state)
        return self.result

class node_eatUntilFull(BT.Node):
    '''Villager goes to the restauraunt if they are not there already, \n
    and will eat until they have 100 food '''
  
    def activate(self, context) -> BT.nodeStates:
        context["villager"].goEat()
        if context["villager"].vHunger == 100:
            context["villager"].changeState(CONST.VillagerStates.IDLE)
            context["villager"].goTo(context["town"].townHall)
            return BT.nodeStates.SUCCESS
        else:
            return BT.nodeStates.WAITING

class node_hungerCheck(BT.Node):
    '''Returns success if the villager isn't hungry'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        if context["villager"].vHunger < 10:
            return BT.nodeStates.FAILED
        else:
            return BT.nodeStates.SUCCESS

class node_isTownStarving(BT.Node):
    '''returns success if the town is starving'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        if context["town"].townHall.starving:
            return BT.nodeStates.SUCCESS
        return BT.nodeStates.FAILED

class tree_HungerSatisfactionTree(BT.Tree):
    '''checks if the villager has enough food and eats if neccesary'''
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(BT.FallBackNode("Hunger Satisfaction Tree"))
        
        #if eating, eat until full
        eatingLoop = BT.SequenceNode("eating loop")
        isEating = node_villagerInState(CONST.VillagerStates.EATING)
        eatToFull = node_eatUntilFull("eating until full")
        self.addNodetoRoot(eatingLoop)
        self.addNode(isEating,eatingLoop)
        self.addNode(eatToFull,eatingLoop)
        #check if the villager is hungry and if the town has food
        townFoodCheck = node_isTownStarving("Town Check")
        hungerCheck = node_hungerCheck("hunger check")
        self.addNodetoRoot(townFoodCheck)
        self.addNodetoRoot(hungerCheck)
        self.addNodetoRoot(node_setVillagerState(CONST.VillagerStates.EATING,result=BT.nodeStates.FAILED,desc="Setting State to Eating"))

class node_workUntilJobdone(BT.Node):
    '''work until the current task is complete'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        villager = context["villager"]
        #returns success if the job is done, waiting if it's still working, or failed if there is no job
        if villager.vTask is not None:
            villager.goWork()
            if villager.work():
                return BT.nodeStates.SUCCESS
            else:
                return BT.nodeStates.WAITING
        else:
            return BT.nodeStates.FAILED   

class node_vilagerHasWork(BT.Node):
    def activate(self, context):
        super().activate(context)
        if context["villager"].hasWork():
            return BT.nodeStates.SUCCESS
        else:
            return BT.nodeStates.FAILED

class node_doesTownHaveWork(BT.Node):
    '''checks if the town has tasks to give out'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        board = context["board"]
        if board.hasWork():
            return BT.nodeStates.SUCCESS
        else:
            return BT.nodeStates.FAILED

class node_assignJobifAble(BT.Node):
    '''gives the villager a job if it can'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        board = context["board"]
        if board.hasWork() and context["villager"].vTask == None:
            board.assignJob(context["villager"])
            context["villager"].changeState(CONST.VillagerStates.WORKING)
            return BT.nodeStates.WAITING
        context["villager"].changeState(CONST.VillagerStates.IDLE)
        return BT.nodeStates.SUCCESS

class tree_workTree(BT.Tree):
    '''assigns work if possible and the villager does not already have work'''
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(BT.FallBackNode("Work Tree"))

        hasWork = node_vilagerHasWork(desc="Checking for Tasks")
        negate = BT.NegateDecorator("")
        townHasWork = node_doesTownHaveWork(desc="Checking for Tasks")
        self.addNodetoRoot(hasWork)
        self.addNodetoRoot(negate)
        self.addNode(townHasWork,negate)
        self.addNodetoRoot(node_assignJobifAble("Getting a job if possible"))

class tree_doWork(BT.Tree):
    '''Performs the work action depending on the type of task'''
    def __init__(self, rootnode=None) -> None:
        super().__init__(rootnode)
        self.addRootNode(BT.FinishDecorator("do work tree"))
        root = BT.SequenceNode()
        self.addNodetoRoot(root)
        self.addNode(node_vilagerHasWork("Villager has something to do"),root)
        #coop tasks
        coopSubTree = BT.FallBackNode("Worker Sync")
        self.addNode(coopSubTree,root)
        negate = BT.NegateDecorator("not in coop task")
        inCoop = node_inCoopTask()
        self.addNode(negate,coopSubTree)
        self.addNode(inCoop,negate)
        waitingforWorkers = node_WaitingOnWorkers("Waiting on workers")
        self.addNode(waitingforWorkers,coopSubTree)
        normalWork = node_workUntilJobdone("Work until done")
        self.addNode(normalWork,root)
        
class node_inCoopTask(BT.Node):
    '''returns success if the current task is cooperative'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        if context["villager"].vTask.coop:
            return BT.nodeStates.SUCCESS
        else:
            return BT.nodeStates.FAILED

class node_WaitingOnWorkers(BT.Node):
    '''returns waiting if the villager is in a cooperative task, but waiting on workers
       succeeds otherwise'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        if context["villager"].vTask.isWaiting():
            return BT.nodeStates.WAITING
        else:
            return BT.nodeStates.SUCCESS

class node_goToTavern(BT.Node):
     
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        villager = context["villager"]
        villager.goToBuildingType(CONST.buildingClass.TAVERN)

class node_villagerSleep(BT.Node):
    def activate(self, context):
        super().activate(context)
        villager = context["villager"]
        #villager goes to sleep and returns success if the villager is fully rested
        villager.goSleep()
        return BT.nodeStates.WAITING

class node_needSleep(BT.Node):
    def activate(self, context):
        super().activate(context)
        town = context["town"]
        time = town.townAge
        time%=525600
        time%=1440
        hr = time//60
        time%=60
        min = time%60
        #if the time is past 10PM or earlier than 7AM
        if (hr > 22 or hr < 7) or context["villager"].vEnergy <= 10:
            #the villager needs sleep
            return BT.nodeStates.SUCCESS
        else:
            #the villager doesn't need sleep
            return BT.nodeStates.FAILED

class node_hasRoominHouse(BT.Node):
    def activate(self,context):
        #if the villager has no home
        if context["villager"].home == None:
            return BT.nodeStates.FAILED
        
class tree_haveChild(BT.Tree):
    def __init__(self, rootnode=None) -> None:
        self.addRootNode(BT.FinishDecorator("Have Children tree"))
        super().__init__(rootnode)

class tree_SleepUntilRested(BT.Tree):
    def __init__(self, rootNode=None):
        super().__init__()
        self.addRootNode(BT.FinishDecorator())
        sequenceRoot = BT.SequenceNode("Sleep Tree")
        self.addNodetoRoot(sequenceRoot)
        needSleepNode = node_needSleep("Needs Sleep?")
        self.addNode(needSleepNode,sequenceRoot)
        sleepNode = node_villagerSleep("sleeping...")
        self.addNode(sleepNode,sequenceRoot)

        
        


class tree_VillagerBehaviorTree(BT.Tree):
    '''constructed villager behavior tree'''
    def __init__(self, rootnode=None) -> None:
        super().__init__()
        self.addRootNode(BT.SequenceNode("Root"))
        self.addNodetoRoot(tree_HungerSatisfactionTree())
        self.addNodetoRoot(tree_SleepUntilRested())
        self.addNodetoRoot(tree_workTree())
        self.addNodetoRoot(tree_doWork())
        self.addNodetoRoot(node_goToTavern("Go to the pub"))

