import tkinter as tk
from tkinter import OptionMenu, StringVar, Text, ttk, scrolledtext
import Utilities
import time
from tkinter.constants import BOTH, DISABLED, END, INSERT, LEFT, VERTICAL
from threading import Thread

class ShipWindow():
    def __init__(self) -> None:
        #home tab
        self.root = tk.Tk()
        self.root.iconbitmap("dish.ico")
        self.tabControl = ttk.Notebook(self.root)
        self.tab1 = tk.Frame(self.tabControl)
        self.tabControl.add(self.tab1,text= "Home")
        self.header = TownHall(self.root,"New New New York")
        self.villagers = ListDisplay(self.tab1)
        self.cargo = dictMarquee(self.tab1,"Cargo")
        self.events = listMarquee(self.tab1,"Events")
        self.buildingTab = SimpleTextObj(self.tab1,height=20,width=80,side='left')
        self.crops = Farm(self.buildingTab)
        self.LastDrawTime = time.time()
        

        #task display tab
        self.tab2 = tk.Frame(self.tabControl)
        self.tabControl.add(self.tab2,text="Tasks")
        self.bTask = BuildingTaskDisplay(self.tab2,height=10,width=80)

        #villager detail tab
        self.tab3 = tk.Frame(self.tabControl)
        self.tabControl.add(self.tab3,text="Villagers")
        self.villagerDisplay = VillagerDisplayTab(self.tab3,height=20,width=80)     
    
    #update the ui to a new state
    def update(self):
        #Update the time
        self.header.updateTownHall(self.context["gold"],self.context["temp"],self.context["Time"])
        self.header.pack(expand=False)

        #update the villager list
        self.villagers.updateList(self.context["VillagerList"])
        self.villagers.pack(expand=False)

        #update the detailed villager tab
        self.villagerDisplay.update(self.context)
        self.villagers.pack(expand=False)

        #update the townHall
        self.cargo.updateMarquee(self.context["cargo"])
        self.cargo.pack(expand=False)

        self.events.updateMarquee(self.context["eventHandler"].getEventDescriptions())
        self.events.pack(expand=False)

        #update the buildings
        self.buildingTab.updateText(self.context["BuildingString"])
        self.buildingTab.pack(expand=False)

        self.root.after(10,self.update)
        

        #update the Farm
        if (time.time() - self.LastDrawTime)  > 1:
            self.crops.updateCrops(self.context["crops"],self.context["Time"])
            self.crops.pack(expand=False)
            self.LastDrawTime = time.time()
        

        self.bTask.updateTasks(self.context["town"].bulletin.getTaskList())
        self.bTask.pack()


        self.root.after(10,self.update)

    def inititialize(self,name,initialState):
        '''start the root and begin the execution'''
        self.root.title(name)
        self.tabControl.pack(expand=True,fill=BOTH)
        self.context = initialState
        self.root.after(10,self.update)
        self.root.mainloop()
    
    def deinitialize(self):
        self.displayThread.join()
        global exit
        exit = True

#takes a List and displays each value
class ListDisplay(tk.Frame):
    def __init__(self,parent):
        self.parent = parent
        super(ListDisplay,self).__init__(parent)
        self.label = tk.Label(parent,text="Villagers")
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=10)
        self.text.pack(padx=10,pady=10)
        self.scr = tk.Scrollbar(self.text,orient=VERTICAL,command=self.text.yview)
    
    def updateList(self,newList):
        self.text.delete("1.0",END)
        for name in newList:
            self.text.insert(INSERT,str(name) + "\t")
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

class dictDisplay(tk.Frame):
    def __init__(self,parent):
        self.parent = parent
        super(dictDisplay,self).__init__(parent,width=20,height= 1)
        
        self.label = tk.Label(parent,text="Time")
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=1)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.pack(expand=False)
    
    def updateDict(self,newDict):
        self.text.delete("1.0",END)
        for key in newDict.keys():
            self.text.insert(INSERT,"{key}: {value}".format(key=key,value=newDict[key]) + "\n")
        self.text.pack(padx=20,pady=1)

class dictMarquee(tk.Frame):
    def __init__(self,parent,title,width=80):
        self.parent = parent
        super(dictMarquee,self).__init__(parent,width=width,height=1)
        
        self.label = tk.Label(parent,text=title)
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=1)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.pack(expand=False)
        self.idx = 0
        self.width = width
    def updateMarquee(self,newDict):
        self.idx += 1
        marquee = ""
        self.text.delete("1.0",END)
        for key in newDict.keys():
            marquee += "{key}: {value} \t".format(key=str(key),value=str(newDict[key]))
        lowBound = 0
        highBound = len(marquee)
        if highBound > self.width:
            highBound = self.width
        self.text.insert(INSERT,marquee[lowBound:highBound])
        self.text.pack(padx=20,pady=1)

class listMarquee(tk.Frame):
    def __init__(self,parent,title,width=80,speed = 5):
        self.parent = parent
        super(listMarquee,self).__init__(parent,width=width,height=1)
        
        self.label = tk.Label(parent,text=title)
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=1)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.pack(expand=False)
        self.idx = 0
        self.offset = 0
        self.width = width
        self.speed = speed

    def updateMarquee(self,newList):
        self.idx += 1
        if self.idx > self.speed:
            self.idx = 0
            self.offset += 1
        marquee = ""
        self.text.delete("1.0",END)
        for value in newList:
            marquee += value
        lowBound = 0
        highBound = len(marquee)
        if highBound > self.width:
            if self.offset / highBound > 2:
                self.offset = len(marquee)
            lowBound = self.offset + self.width
            highBound = self.width + self.offset
        self.text.insert(INSERT,marquee[lowBound:highBound])
        self.text.pack(padx=20,pady=1)

#Displays townhall data
class TownHall(tk.Frame):
    #text padding
    padX = 10
    padY = 1
    def __init__(self,parent,shipName):
        self.parent = parent
        super(TownHall,self).__init__(parent,width=20,height= 1)
        
        self.label = tk.Label(parent,text=shipName)
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=2)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.pack(padx=self.padX,pady=self.padY,expand=False)
        
    #displays gold and food as text
    def updateTownHall(self,treasury,temperature,time):
        self.text.delete("1.0",END)
        self.text.insert(INSERT,"Gold: {value} \t".format(value=treasury))
        self.text.insert(INSERT,"Temp: {value} \n".format(value=temperature))
        self.text.insert(INSERT,"Time: {value}".format(value=time))
        self.text.tag_add("center","1.0","end")
        self.text.pack(padx=self.padX,pady=self.padY,expand=False)

#Just takes text and displays it
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
            tuples.append((c.cropColor,c.getHarvestPercentage()))
            
        self.drawCrops(tuples)

#display certain building's tasks only
class BuildingTaskDisplay(tk.Frame):
    #strings that represent the current 
    allTasks = ""
    farmTasks = ""
    mineTasks = ""
    def __init__(self,parent,height=1,width=1,side='top'):
        self.parent = parent
        super(BuildingTaskDisplay,self).__init__(parent,width=width,height=height)
        
        self.taskCount = tk.Text(parent,height=1,width=width)
        self.taskCount.pack(expand=False,side=side,padx=40)
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

    #update tasks from 
    def updateTasks(self,taskString):
        tasks = taskString.split("\n")
        self.taskCount.delete("1.0",END)
        self.taskCount.insert(tk.END, "Total Tasks: " + str(len(tasks)))
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

class VillagerDisplayTab(tk.Frame):
        def __init__(self,parent,height=1,width=1,side='top'):
            self.parent = parent
            super().__init__(parent,width=width,height= height)
            self.dropDownVariable = StringVar(parent)
            self.dropDownVariable.set("Choose Villager")
            self.dropDown = OptionMenu(parent,self.dropDownVariable,"Villager",command=self.getVillager)
            self.dropDown.pack()
            self.villagers = []

            self.relationsText = scrolledtext.ScrolledText(self.parent,height=10,width=width)
            self.relationsText.pack(expand=False,side=side,padx=4)
        
        #center a villager and get their information
        def getVillager(self, *args):
            currentSelection = self.dropDownVariable.get()
            self.relationsText.delete("1.0",END)
            villager = self.villagers[currentSelection]
            for value in villager.Relationships.keys():
                self.relationsText.insert(tk.END,"{other} : {value}\n".format(other=value.vName,value= round(villager.Relationships[value],2)))

            
            
        def update(self,context) -> None:
            i = 0
        # Add menu items.
            villagerList = dict()
            dropDownList = list()
            for v in context["VillagerList"]:
                villagerList[v.vName + str(v.vBirthCycle)] = v
                dropDownList.append(v.vName + str(v.vBirthCycle))
            self.villagers = villagerList
            self.dropDown.destroy()
            self.dropDown = OptionMenu(self.parent,self.dropDownVariable,*dropDownList,command=self.getVillager)
            self.dropDown.pack()

            if self.dropDownVariable.get() != "Choose Villager":
                self.getVillager()
            return super().update()

          


