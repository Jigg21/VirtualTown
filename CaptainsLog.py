from tkinter import Message
import random

logs = []
day = 0
currentLog = None
class logOBJ():
    
    def __init__(self) -> None:
        self.contents = []
        self.resourceDict = dict()
    
    def addContent (self,message):
        if (message not in self.contents):
            self.contents.append(message)
    
    #add to the resource count
    def addResource(self,resource,amount):
        if resource in self.resourceDict:
            self.resourceDict[resource] += amount
        else:
            self.resourceDict[resource] = amount

    def makeLog(self):
        with open('DailyLog.log', 'a') as f:
            f.write("=========================================\n")
            #log all messages
            for message in self.contents:
                f.write(message + "\n")

            #log resource counts for today
            for key in self.resourceDict:
                value = self.resourceDict[key]
                if value > 0:
                    f.write("gathered {value} {resource}\n".format(value=value,resource=key))
                if value < 0:
                    f.write("lost {value} {resource}\n".format(value=abs(value),resource=key))
            

def newDay():
    global currentLog
    currentLog.makeLog()
    newDayOBJ = logOBJ()
    newDayOBJ.addContent("Log #{Lday}".format(Lday=day))
    currentLog = newDayOBJ
    
#Log a certain message
def log(message):
    global currentLog
    message = str(message)
    currentLog.addContent(message)

#log a change in resources
def logResource(resource,amount):
    global currentLog
    currentLog.addResource(resource,amount)

def logSale(resource,amount,pay):
    global currentLog
    currentLog.addContent("Sold {a} {r} for {p} gold".format(a=amount,r=resource,p=pay))

def initialize():
    global currentLog
    initLog = logOBJ()
    currentLog = initLog
    with open('DailyLog.log', 'w') as f: 
	    f.write("BEGIN CAPTAINS LOG\n\n")

def closeLogs():
    global currentLog
    Outros = ["See you space cowboy...","Shutting Down...","Just what do you think you're doing, Dave?"]
    closer = random.choice(Outros)
    currentLog.makeLog()
    log(closer)
        
        
initialize()