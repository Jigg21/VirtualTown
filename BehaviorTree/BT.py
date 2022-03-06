from ctypes import resize
from enum import Enum
from unittest import result


class Tree():
    '''tree base class'''
    def __init__(self,rootnode = None) -> None:
        '''Creates a tree object with a given rootnode'''
        self.rootNode = rootnode  
    
    def addRootNode(self,node):
        '''designates a node as the root node'''
        self.rootNode = node
    
    
    def addNode(self,node,parent):
        '''adds node to the tree as a child of parent'''
        p = self.rootNode.findChild(parent)
        if p is None:
            return None
        else:
            p.addChild(node)

    
    def addNodetoRoot(self,node):
        '''add node to the tree as a child of the root node'''
        self.rootNode.addChild(node)
    
    def activate(self,context):
        '''Traverse the tree with given dictionary context'''
        return self.rootNode.activate(context)
    
    def traverse(self,context):
        '''Traverse the tree with given dictionary context'''
        results = self.rootNode.activate(context)
        if context["Verbose"]:
            print("RESULT: {result}".format(result=results))

class nodeStates (Enum):
    '''States a node can be'''
    UNEXPLORED = 0
    SUCCESS = 1
    FAILED = 2
    WAITING = 3

class Node ():
    '''Node Base Class'''
    def __init__(self,desc = "") -> None:
        '''make a node with this description'''
        self.children = []
        self.state = nodeStates.UNEXPLORED
        self.desc = desc

    
    def activate(self,context) -> nodeStates:
        '''ticks the node, prints desc if Verbose is on'''
        if context["Verbose"]:
            print(self.desc)

    
    def addChild(self,child):
        '''adds a child to the node'''
        self.children.append(child)
    
    def findChild(self,target):
        '''Recursively find target in children'''
        if self == target:
            return self
        elif len(self.children) == 0:
            return None
        else:
            for child in self.children:
                result = child.findChild(target)
                if result == target:
                    return result

class SequenceNode (Node):
    '''sequence control node, activates children one by one, returns success if all children return success'''
    def activate(self,context) -> nodeStates:
        super().activate(context)
        for child in self.children:
            cResult = child.activate(context)
            if cResult == nodeStates.FAILED:
                return nodeStates.FAILED
            if cResult == nodeStates.WAITING:
                return nodeStates.WAITING
        else:
            return nodeStates.SUCCESS

class FallBackNode (Node):
    def activate(self,context):
        '''fallback control node, returns success at the first child that returns success or waiting'''
        super().activate(context)
        for child in self.children:
            result = child.activate(context)
            if result == nodeStates.SUCCESS:
                return nodeStates.SUCCESS
            if result == nodeStates.WAITING:
                return nodeStates.WAITING
        return nodeStates.FAILED

class ParallelNode (Node):
    '''fallback control node, returns success at the first child that returns success or waiting'''
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

class decoratorNode (Node):
    '''Decorator Base class'''
    def activate(self,context) -> nodeStates:
        super().activate(context)
        if len(self.children) == 0:
            return nodeStates.UNEXPLORED
        else:
            value = self.children[0].activate(context)
            return self.function(value)

    def function(self,*args):
        pass

class NegateDecorator(decoratorNode):
    '''converts success states to fails and vice versa'''    
    def function(self, *args):
        state = args[0]
        if state == nodeStates.SUCCESS:
            return nodeStates.FAILED
        if state == nodeStates.FAILED:
            return nodeStates.SUCCESS
        return state

class FinishDecorator(decoratorNode):
    '''returns success if child returns success or failure, Fails otherwise'''
    def function(self, *args):
        state = args[0]
        if state == nodeStates.SUCCESS:
            return nodeStates.SUCCESS
        if state == nodeStates.FAILED:
            return nodeStates.SUCCESS
        return nodeStates.FAILED