from enum import Enum

#Behavior Tree manager
class BehaviorTree():
    def __init__(self) -> None:
        self.rootNode = None

#States a node can be
class nodeStates (Enum):
    UNEXPLORED = 0
    SUCCESS = 1
    FAILED = 2
    WAITING = 3

#Node base class 
class Node ():
    def __init__(self) -> None:
        self.children = []
        self.state = nodeStates.UNEXPLORED

    def activate(self,context) -> nodeStates:
        pass

    def addChild(self,child):
        self.children.append(child)

#sequence control node, returns success if all children return success
class SequenceNode (Node):
    def activate(self,context) -> nodeStates:
        for child in self.children:
            result = child.activate(context)
            if result == nodeStates.FAILED:
                return nodeStates.FAILED
            if result == nodeStates.WAITING:
                return nodeStates.WAITING
        else:
            return nodeStates.SUCCESS

#fallback control node, returns success at the first child that returns success
class FallBackNode (Node):
    def activate(self,context) -> nodeStates:
        for child in self.children:
            result = child.activate(context)
            if result == nodeStates.SUCCESS:
                return nodeStates.SUCCESS
        else:
            return nodeStates.FAILED

#parallel control node, activates all children, then returns success if any succeeded
class ParallelNode (Node):
    def __init__(self) -> None:
        super().__init__()
    def activate(self,context) -> nodeStates:
        returnValue = nodeStates.FAILED
        for child in self.children:
            result = child.activate(context)
            #if it's waiting and a success hasn't happened
            if result == nodeStates.WAITING and returnValue != nodeStates.SUCCESS:
                returnValue = nodeStates.WAITING
            #if a child has succeeded 
            if result == nodeStates.SUCCESS:
                returnValue = nodeStates.SUCCESS
        return returnValue


#Decorator Base class
class decoratorNode (Node):
    def activate(self,context) -> nodeStates:
        if len(self.children) == 0:
            return nodeStates.UNEXPLORED
        else:
            value = self.children[0].activate(context)
            return self.function(value)

    def function(self,*args):
        pass

#converts success states to fails and vice versa
class NegateDecorator(decoratorNode):
    def __init__(self) -> None:
        super().__init__()
    def function(self, *args):
        state = args[0]
        if state == nodeStates.SUCCESS:
            return nodeStates.FAILED
        if state == nodeStates.FAILED:
            return nodeStates.SUCCESS
        return state