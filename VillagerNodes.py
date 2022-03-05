from BehaviorTree import BT
from CONST import VillagerStates

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
            context["villager"].changeState(VillagerStates.IDLE)
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
        isEating = node_villagerInState(VillagerStates.EATING)
        eatToFull = node_eatUntilFull("eating until full")
        self.addNodetoRoot(eatingLoop)
        self.addNode(isEating,eatingLoop)
        self.addNode(eatToFull,eatingLoop)
        #check if the villager is hungry and if the town has food
        townFoodCheck = node_isTownStarving("Town Check")
        hungerCheck = node_hungerCheck("hunger check")
        self.addNodetoRoot(townFoodCheck)
        self.addNodetoRoot(hungerCheck)
        self.addNodetoRoot(node_setVillagerState(VillagerStates.EATING,result=BT.nodeStates.FAILED,desc="Setting State to Eating"))

class node_workUntilJobdone(BT.Node):
    '''work until the current task is complete'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        villager = context["villager"]
        #returns success if the job is done, waiting if it's still working, or failed if there is no job
        if villager.vTask is not None:
            villager.goWork()
            villager.vTask.work(villager)
            if villager.vTask.completed:
                villager.finishWork()
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

class node_assignJobifAble(BT.Node):
    '''gives the villager a job if it can'''
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        board = context["board"]
        if board.hasWork() and context["villager"].vTask == None:
            board.assignJob(context["villager"])
            context["villager"].changeState(VillagerStates.WORKING)
            return BT.nodeStates.WAITING
        context["villager"].changeState(VillagerStates.IDLE)
        return BT.nodeStates.SUCCESS

class tree_workTree(BT.Tree):
    '''works while there are tasks to be done'''
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(BT.FallBackNode("Work Tree"))

        workLoop = BT.SequenceNode("Work Loop")
        workCheck = BT.FallBackNode("Work Check")
        hasWork = node_vilagerHasWork(desc="Checking for work")
        inStateWorking = node_villagerInState(VillagerStates.WORKING)
        workUntilDone = node_workUntilJobdone("Work Until done")
        self.addNodetoRoot(workLoop)
        self.addNode(workCheck,workLoop)
        self.addNode(inStateWorking,workCheck)
        self.addNode(hasWork,workCheck)
        self.addNode(workUntilDone,workLoop)
        self.addNodetoRoot(node_assignJobifAble("Getting a job if possible"))

