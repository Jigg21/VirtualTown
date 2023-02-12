
class Family():
    def __init__(self,name) -> None:
        self.fName = name
        self.fGold = 0
        self.fMembers = []
    
    def isAbsorbed(self,otherFam):
        return len(self.fMembers) < len(otherFam.fMembers)
    
