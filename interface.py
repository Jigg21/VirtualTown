from ast import arg
from enum import Flag
from math import exp, floor
import tkinter as tk
from tkinter import OptionMenu, StringVar, Text, ttk
import Utilities
import time
from tkinter.constants import BOTH, DISABLED, END, INSERT, LEFT, VERTICAL




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
class SimpleTextObj(tk.Frame):
    def __init__(self,parent,height=1,width=1,side='top'):
        self.parent = parent
        super(SimpleTextObj,self).__init__(parent,width=width,height= height)
        
        self.text = tk.Text(parent,height=height,width=width)
        self.text.pack(expand=False,side=side,padx=40)

        
    #takes string from console and displays it
    def updateText(self,text):
        self.text.delete("1.0",END)
        self.text.insert(INSERT,text)
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
        self.crops.delete('all')
        Coord1 = [0,0]
        for c in cropList:
            self.crops.create_oval(Coord1[0],Coord1[1],  Coord1[0]+30,Coord1[1]+30,outline=c[0],width=5,fill=Utilities.interpolateRedtoGreen(c[1]))
            Coord1[0] += 30
            if (Coord1[0] > 300):
                Coord1[0] = 0
                Coord1[1] += 30
        self.crops.pack(expand=False)

    #parse the crop values and dispay them on the canvas
    def updateCrops(self,crops,currentTime):
        tuples = []
        for c in crops:
            tuples.append((c.cropColor,c.getHarvestPercentage(currentTime)))
            
        self.drawCrops(tuples)

#display certain building's tasks only
class BuildingTaskDisplay(tk.Frame):
    #strings that represent the current 
    allTasks = ""
    farmTasks = ""
    mineTasks = ""
    def __init__(self,parent,height=1,width=1,side='top'):
        self.parent = parent
        super(BuildingTaskDisplay,self).__init__(parent,width=width,height= height)
        
        self.dropDownVariable = StringVar(parent)
        self.dropDownVariable.set("Choose Building")

        self.dropDown = OptionMenu(parent,self.dropDownVariable,"All","Farm","Mine",command=self.displayTasks)
        self.dropDown.pack()

        self.text = tk.Text(parent,height=height,width=width)
        self.text.pack(expand=False,side=side,padx=40)
    
    
    def displayTasks(self,*args):
        currentSelection = self.dropDownVariable.get()
        self.text.delete("1.0",END)
        if (currentSelection == "All"):
            self.text.insert(INSERT,self.allTasks)
            self.text.pack()
        if currentSelection == "Farm":
            self.text.insert(INSERT,self.farmTasks)
            self.text.pack()
        
        if currentSelection == "Mine":
            self.text.insert(INSERT,self.mineTasks)
            self.text.pack()

    def updateTasks(self,taskString):
        tasks = taskString.split("\n")
        self.allTasks = taskString
        self.farmTasks = ""
        self.mineTasks = ""
        for task in tasks:
            if (task != ""):
                buildingLocation = task[0:task.find(")")+1]
                if buildingLocation == "(Farm)":
                    self.farmTasks += task + "\n"
                
                if buildingLocation == "(Mine)":
                    self.mineTasks += task + "\n"
        
        self.text.delete("1.0",END)
        self.displayTasks()


    

root = tk.Tk()
tabControl = ttk.Notebook(root)
tab1 = tk.Frame(tabControl)
tabControl.add(tab1,text= "Home")
timeObj = TimeObj(root)
villagers = Villagers(tab1)
townHall = TownHall(tab1)
buildingTab = SimpleTextObj(tab1,height=20,width=35,side='left')
crops = Farm(buildingTab)
LastDrawTime = time.time()

tab2 = tk.Frame(tabControl)
tabControl.add(tab2,text="Tasks")
bTask = BuildingTaskDisplay(tab2,height=10,width=80)
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
    buildingTab.updateText(args["BuildingString"])
    buildingTab.pack(expand=False)

    #update the Farm
    global LastDrawTime
    if (time.time() - LastDrawTime)  > 1:
        crops.updateCrops(args["crops"],args["Time"])
        crops.pack(expand=False)
        LastDrawTime = time.time()
    

    bTask.updateTasks(args["town"].bulletin.getTaskList())
    bTask.pack()


    root.update()


def inititialize():
  root.title("Nuke Town")
  tabControl.pack(expand=True,fill=BOTH)
  

def deinitialize():
    root.quit()
    global exit
    exit = True


