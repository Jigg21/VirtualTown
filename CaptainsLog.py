
logs = []


class log():
    day = 0
    contents = ""
    def __init__(self,day) -> None:
        self.day = day
    
    def addContent (self,message):
        self.contents += message + "\n"
        

def makeCaptainsLog(day):
    with open('dailyLog', 'a') as f: 
        f.write(logs[day])

def initialize():
    with open('dailyLog', 'w') as f: 
	    f.write('data') 
	    f.close() 

initialize()