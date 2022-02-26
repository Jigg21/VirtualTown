from enum import Enum

#Behavior Tree manager
class Tree():
    def __init__(self) -> None:
        self.rootNode = None
    
    #add the root node
    def addRootNode(self,node):
        self.rootNode = node
    
    #adds node to the tree as a child of parent
    def addNode(self,node,parent):
        p = self.rootNode.findChild(parent)
        if p is None:
            return None
        else:
            p.addChild(node)

    #add node to the tree as a child of the root node
    def addNodetoRoot(self,node):
        self.rootNode.addChild(node)
    
    #traverse the tree
    def activate(self,context):
        self.rootNode.activate(context)
    

#States a node can be
class nodeStates (Enum):
    UNEXPLORED = 0
    SUCCESS = 1
    FAILED = 2
    WAITING = 3

#Node base class 
class Node ():
    def __init__(self,desc = "") -> None:
        self.children = []
        self.state = nodeStates.UNEXPLORED
        self.desc = desc

    #ticks the node
    def activate(self,context) -> nodeStates:
        if context["Verbose"]:
            print(self.desc)

    #adds a child to the node
    def addChild(self,child):
        self.children.append(child)
    
    #recursively find target in children
    def findChild(self,target):
        if self == target:
            return self
        elif len(self.children) == 0:
            return None
        else:
            for child in self.children:
                result = child.findChild(target)
                if result == target:
                    return result


#sequence control node, activates children one by one, returns success if all children return success
class SequenceNode (Node):
    def activate(self,context) -> nodeStates:
        super().activate(context)
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
        super().activate(context)
        for child in self.children:
            result = child.activate(context)
            if result == nodeStates.SUCCESS:
                return nodeStates.SUCCESS
        else:
            return nodeStates.FAILED

#parallel control node, activates all children, then returns success if any succeeded
class ParallelNode (Node):
    def activate(self,context) -> nodeStates:
        super().activate(context)
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
        super().activate(context)
        if len(self.children) == 0:
            return nodeStates.UNEXPLORED
        else:
            value = self.children[0].activate(context)
            return self.function(value)

    def function(self,*args):
        pass


    
