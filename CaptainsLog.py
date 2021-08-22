logs = []
day = 0
class logOBJ():
    
    def __init__(self) -> None:
        self.contents = []
    
    def addContent (self,message):
        if (message not in self.contents):
            self.contents.append(message)
    
    def makeLog(self):
        with open('DailyLog.log', 'a') as f:
            f.write("=========================================\n")
            for message in self.contents:
                f.write(message + "\n")
            

def newDay():
    global logs
    global day
    logs[day].makeLog()
    day += 1
    newDayOBJ = logOBJ()
    newDayOBJ.addContent("Log #{Lday}".format(Lday=day))
    logs.append(newDayOBJ)
    

def log(message):
    global logs
    global day
    message = str(message)
    logs[day].addContent(message)
    



def initialize():
    global logs
    global day
    initLog = logOBJ()
    initLog.addContent("ALL SYSTEMS GO")
    logs.append(initLog)
    with open('DailyLog.log', 'w') as f: 
	    f.write("BEGIN CAPTAINS LOG\n\n")

def closeLogs():
    global logs
    global day
    with open('DailyLog.log', 'a') as f:
        f.write("=========================================\n")
        for message in logs[day].contents:
            f.write(message + "\n")
        f.write("=========================================\n")

        
        
initialize()