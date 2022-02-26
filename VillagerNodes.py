from BehaviorTree import BT
from CONST import VillagerStates
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

#test tree
class TestTree(BT.Tree):
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(BT.FallBackNode(desc="Main Sequence Loop"))
        
        testnode2 = TestNode_ConstantState(BT.nodeStates.FAILED,desc="RETURNING FAILURE")
        testdec = BT.NegateDecorator(desc="Negate!")
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
    '''set a villagers state to some predetermined state'''
    def __init__(self, state,desc="") -> None:
        super().__init__(desc)
        self.state = state

    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        context["villager"].changeState(self.state)
        return BT.nodeStates.SUCCESS

class node_eatUntilFull(BT.Node):
    '''Villager goes to the restauraunt if they are not there already, \n
    and will eat until they have 100 food '''
  
    def activate(self, context) -> BT.nodeStates:
        context["villager"].goEat()
        if context["villager"].vHunger == 100:
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
        if context["town"].townhall.starving:
            return BT.nodeStates.SUCCESS
        return BT.nodeStates.FAILED

class tree_HungerSatisfactionTree(BT.Tree):
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(BT.FallBackNode("Hunger Satisfaction Tree"))
        
        #if eating, eat until full
        eatingLoop = BT.SequenceNode("Get food loop")
        isEating = node_villagerInState(VillagerStates.EATING)
        eatToFull = node_eatUntilFull("eating until full")
        self.addNodetoRoot(eatingLoop)
        self.addNode(isEating,eatingLoop)
        self.addNode(eatToFull,eatingLoop)
        #check if the villager is hungery and if the
        notStarvingDec = BT.NegateDecorator("NOT")
        townFoodCheck = node_isTownStarving("Town Check")
        hungerCheck = node_hungerCheck("hunger check")
        self.addNodetoRoot(notStarvingDec)
        self.addNode(townFoodCheck,notStarvingDec)
        self.addNodetoRoot(hungerCheck)
        self.addNodetoRoot(node_setVillagerState(VillagerStates.EATING))



TestTree().activate({"Verbose":True})
