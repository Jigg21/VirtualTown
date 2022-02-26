from BehaviorTree import BT
from Villagers import VillagerStates

class TestNode_ConstantState(BT.Node):
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
    '''returns success if the villager is in the proper state'''
    def __init__(self,state,desc="") -> None:
        super().__init__(desc)
        self.state = state
    
    def activate(self, context) -> BT.nodeStates:
        super().activate(context)
        if context["villager"].vState == self.state:
            return BT.nodeStates.SUCCESS
        else:
            return BT.nodeStates.FAILED

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
        if context["town"].

TestTree().activate({"Verbose":True})
