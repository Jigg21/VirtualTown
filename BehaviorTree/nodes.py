from BehaviorTree import *
#from BehaviorTree.BehaviorTree import *
##Where Node logic is added

class TestNode_ConstantState(Node):
    def __init__(self,state,desc="") -> None:
        super().__init__(desc)
        self.returnState = state
    
    def activate(self,context):
        super().activate(context)
        return self.returnState


class TestNode_PrintMessage(Node):
    def __init__(self,message) -> None:
        super().__init__()
        self.message = message
    
    def activate(self,context):
        print(self.message)
        return nodeStates.SUCCESS

#converts success states to fails and vice versa
class NegateDecorator(decoratorNode):
        
    def function(self, *args):
        state = args[0]
        if state == nodeStates.SUCCESS:
            return nodeStates.FAILED
        if state == nodeStates.FAILED:
            return nodeStates.SUCCESS
        return state

#test tree
class TestTree(Tree):
    def __init__(self) -> None:
        super().__init__()
        self.addRootNode(FallBackNode(desc="Main Sequence Loop"))
        
        testnode2 = TestNode_ConstantState(nodeStates.FAILED,desc="RETURNING FAILURE")
        testdec = NegateDecorator(desc="Negate!")
        self.addNodetoRoot(testdec)
        testnode = TestNode_PrintMessage("Starting")
        self.addNode(testnode,testdec)
        self.addNodetoRoot(testnode2)
        self.addNodetoRoot(TestNode_PrintMessage("DONE"))
        

TestTree().activate({"Verbose":True})
