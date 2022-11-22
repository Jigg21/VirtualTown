from CONST import EventTypes, EventSeverity
from ConfigReader import ConfigData as config
import random

'''BASE CLASES'''
class EventHandler():
    '''handles the events for the ship'''
    def __init__(self) -> None:
        self.activeEvents = list()

        #Events that can activate randomly
        self.randomEvents = list()
        self.randomEvents.append(GoldMeteoroidHitsShip)
    
    def addEvent(self,event):
        self.activeEvents.append(event)
    
    def removeEvent(self,event):
        self.activeEvents.remove(event)

    def update(self,context):
        '''update the manager with time'''
        for event in self.activeEvents:
            event.update(context)
        
        for randomEvent in self.randomEvents:
            #if the random event happens
            if randomEvent.rollForActivation(context):
                self.activeEvents.append(randomEvent[0](context))
    
    def getEventDescriptions(self):
        '''gets a string representation of the active events'''
        result = ""
        for event in self.activeEvents:
            result += event.desc + ","
        return result

class ShipEvents():

    #Class information for each event
    desc = "EVENT DESCRIPTION"
    eventType = EventTypes.NULL
    duration = -1
    probability = .0001
    severity = EventSeverity.NEGLIGIBLE
    def __init__(self,context) -> None:
        startTime = context["Cycle"]

        #if the event is completed
        self.finished = False
        #assigns the timing information for non-conditional events
        if self.eventType == EventTypes.TEMPORARY:
            self.startTime = startTime
            self.endTime = startTime + self.duration
        if self.eventType == EventTypes.INSTANT:
            self.startTime = startTime
            self.endTime = self.startTime + config.getfloat("EVENTS","EVENTMESSAGEDELAY")
        #activate the event   
        self.activate(context)
        pass
    
    def activate(self,context):
        '''what happens when the event goes into effect'''
        raise NotImplementedError("No activation function implemented")

    def deactivate(self,context):
        '''what happens when the event ends'''
        raise NotImplementedError("No deactivation function implemented")
    
    def condition(self,context) -> (bool):
        '''if the event is conditional, what condition must be met to end it'''
        raise NotImplementedError("Conditional method was called, but none was supplied ")

    def rollForActivation(cls,context) -> (bool):
        '''roll for if the event should activate'''
        roll = 1-random.random
        if cls.probability > roll:
            if cls.precondition(context):
                return True
        return False

    def precondition(context) -> (bool):
        '''conditions that must be true for the event to trigger, defaults to true'''
        return True
    
    
    def update(self,context):
        '''called every cycle to check if the event is over'''
        if not self.finished:
            if self.eventType == EventTypes.CONDITIONAL:
                if self.condition(context):
                    self.deactivate()
                    self.finished =  True
            else:
                if context["Cycle"] >= self.endTime:
                    if self.eventType == EventTypes.TEMPORARY:
                        self.deactivate()
                    self.finished = True
        return self.finished

'''EVENT DECLARATIONS'''

class GoldMeteoroidHitsShip(ShipEvents):
    desc = "BREAKING! A meteoroid has hit the ship, initial scans suggest it to be made of solid gold!"
    eventType = EventTypes.INSTANT
    probability = 0.0001
    severity = EventSeverity.MINOR
    def activate(self,context):
        ship = context["town"]
        ship.addTreasury(1000)

class LibertariadTradeWar(ShipEvents):
    desc = "The Libertariad has decreed our Town a threat to galactic security"
    eventType = EventTypes.TEMPORARY
    probability = 0.000001
    severity = EventSeverity.EMERGENCY
    duration = 10000
    def activate(self,context):
        ship = context["town"]
        