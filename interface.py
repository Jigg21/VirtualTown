from enum import Flag
from math import exp
import tkinter as tk
import Utilities
import time
from tkinter.constants import DISABLED, END, INSERT, LEFT, VERTICAL




#displays the villagers and their stats
class Villagers(tk.Frame):
    def __init__(self,parent):
        self.parent = parent
        super(Villagers,self).__init__(parent)
        self.label = tk.Label(parent,text="Villagers")
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=10)
        self.text.pack(padx=10,pady=10)
        self.scr = tk.Scrollbar(self.text,orient=VERTICAL,command=self.text.yview)
    
    def updateList(self,newList):
        self.text.delete("1.0",END)
        for name in newList:
            self.text.insert(INSERT,str(name) + "\n")
        self.text.pack(padx=20,pady=1)

#displays the time and date
class TimeObj(tk.Frame):
    timePadX = 20
    timePadY = 1
    #creates layout
    def __init__(self,parent):
        self.parent = parent
        super(TimeObj,self).__init__(parent,width=20,height= 1)
        
        self.label = tk.Label(parent,text="Time")
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=1)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.pack(padx=self.timePadX,pady=self.timePadY,expand=False)
        
    #takes the time and displays it
    def updateTime(self,newTime):
        self.text.delete("1.0",END)
        self.text.insert(INSERT,newTime + "\n")
        self.text.tag_add("center","1.0","end")
        self.text.pack(padx=self.timePadX,pady=self.timePadY,expand=False)


#Displays townhall data
class TownHall(tk.Frame):
    #text padding
    padX = 10
    padY = 1
    def __init__(self,parent):
        self.parent = parent
        super(TownHall,self).__init__(parent,width=20,height= 1)
        
        self.label = tk.Label(parent,text="Town Hall")
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=2)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.pack(padx=self.padX,pady=self.padY,expand=False)
        
    #displays gold and food as text
    def updateTownHall(self,treasury,stockPile):
        self.text.delete("1.0",END)
        self.text.insert(INSERT,"Gold: {value}".format(value=treasury) + "\n")
        self.text.insert(INSERT,"Food: {value}".format(value=stockPile) + "\n")
        self.text.tag_add("center","1.0","end")
        self.text.pack(padx=self.padX,pady=self.padY,expand=False)

#Buildings Display
class Buildings(tk.Frame):
    def __init__(self,parent):
        self.parent = parent
        super(Buildings,self).__init__(parent,width=20,height= 1)
        
        self.text = tk.Text(parent,height=20,width=35)
        self.text.pack(expand=False,side='left',padx=20)

        #self.label = tk.Label(self.text,text="Buildings")
        #self.label.pack(expand=True)

        
    #takes string from console and displays it
    def updateBuildings(self,buildingString):
        self.text.delete("1.0",END)
        self.text.insert(INSERT,buildingString)
        self.text.pack(expand=False)

#display crops
class Farm(tk.Frame):
    def __init__(self,parent):
        self.parent = parent
        super(Farm,self).__init__(parent,width=20,height= 1)
        
        #label
        self.label = tk.Label(parent,text="Crops")
        self.label.pack(padx=0,pady=0)
        
        #canvas
        self.crops = tk.Canvas(parent,bg= "brown",width=300,height=300)
        crops = [("#ff00ff",0)]
        self.crops.delete("all")
        self.drawCrops(crops)
        self.crops.pack(expand=False)

    #draw the canvas
    def drawCrops(self,cropList):
        Coord1 = [0,0]
        for c in cropList:
            self.crops.create_oval(Coord1[0],Coord1[1],  Coord1[0]+30,Coord1[1]+30,outline=c[0],width=5,fill=Utilities.interpolateRedtoGreen(c[1]))
            Coord1[0] += 30
            if (Coord1[0] > 300):
                Coord1[0] = 0
                Coord1[1] += 30
        self.crops.pack(expand=False)

    #parse the crop values and dispay them on the canvas
    def updateCrops(self,crops):
        tuples = []
        for c in crops:
            tuples.append((c.cropColor,c.getHarvestPercentage()))
            
        self.drawCrops(tuples)

root = tk.Tk()
timeObj = TimeObj(root)
villagers = Villagers(root)
townHall = TownHall(root)
buildingTab = Buildings(root)
crops = Farm(buildingTab)
LastDrawTime = time.time()

#called every tick
def update(args):
    #Update the time
    timeObj.updateTime(args["Time"])
    timeObj.pack(expand=False)

    #update the villager list
    villagers.updateList(args["VillagerList"])
    villagers.pack(expand=False)

    #update the townHall
    townHall.updateTownHall(args["gold"],args["food"])
    townHall.pack(expand=False)

    #update the buildings
    buildingTab.updateBuildings(args["BuildingString"])
    buildingTab.pack(expand=False)

    #update the Farm
    global LastDrawTime
    if (time.time() - LastDrawTime)  > 1:
        crops.updateCrops(args["crops"])
        crops.pack(expand=False)
        LastDrawTime = time.time()
    

        

    root.update()


def inititialize():
  root.title("Nuke Town")
  

def deinitialize():
    root.quit()
    global exit
    exit = True


