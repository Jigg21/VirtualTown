import tkinter as tk
from Utilities.ConfigReader import ConfigData as config
from tkinter import OptionMenu, StringVar, Text, ttk, scrolledtext, messagebox, filedialog
import Utilities
import time
from tkinter.constants import BOTH, DISABLED, END, INSERT, LEFT, VERTICAL
from PIL import Image, ImageTk
import signal
import pickle
import os

FILEPATH = os.getcwd()

class ShipWindow():
    def __init__(self) -> None:
        #home tab
        self.root = tk.Tk()
        self.root.configure(bg=config["UI"]["DARKBACKGROUND"])
        bgColor = config["UI"]["DARKBACKGROUND"]
        #if running Windows
        if os.name == 'nt':
            self.root.iconbitmap(os.path.join(FILEPATH,"Dish.ico"))
        
        style = ttk.Style()
        style.theme_create( "DarkMode", parent="alt", settings={
                "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0],"background":config["UI"]["DARKBACKGROUND"],"borderwidth": 1}},
                "TNotebook.Tab": {
                    "configure": {"padding": [5, 1], "background": config["UI"]["BACKGROUND"]},
                    "map":       {"background": [("selected", config["UI"]["LIGHTBACKGROUND"])],
                                "expand": [("selected", [1, 1, 1, 0])] } } } )
        style.theme_use("DarkMode")

        self.tabControl = ttk.Notebook(self.root)
        self.tab1 = tk.Frame(self.tabControl,bg=bgColor)
        self.tab1.configure(bg=config["UI"]["DARKBACKGROUND"])
        self.tabControl.add(self.tab1,text= "Home")
        self.header = TownHall(self.root,"New New New York",bg=bgColor)
        self.villagers = ListDisplay(self.tab1,width=120,bg=config["UI"]["DARKBACKGROUND"])
        self.cargo = dictMarquee(self.tab1,"Cargo")
        self.events = listMarquee(self.tab1,"Events")
        self.buildingTab = SimpleTextObj(self.tab1,height=20,width=80,side='left')
        self.buildingTab.configure(bg=config["UI"]["DARKBACKGROUND"])
        self.crops = Farm(self.buildingTab)
        self.LastDrawTime = time.time()

        #File menu
        self.menuBar = tk.Menu(self.root,bg=bgColor)
        self.fileMenu = tk.Menu(self.menuBar,tearoff=0)
        self.fileMenu.add_command(label="Save Town",command=self.saveTown)
        self.fileMenu.add_command(label="Load Town",command=self.loadTown)
        self.menuBar.add_cascade(label="File",menu=self.fileMenu)
        self.root.configure(menu=self.menuBar)

        #task display tab
        self.tab2 = tk.Frame(self.tabControl,bg=bgColor)
        self.tabControl.add(self.tab2,text="Tasks")
        self.bTask = BuildingTaskDisplay(self.tab2,height=10,width=80)

        #villager detail tab
        self.tab3 = tk.Frame(self.tabControl,bg=bgColor)
        self.tabControl.add(self.tab3,text="Villagers")
        self.villagerDisplay = VillagerDisplayTab(self.tab3,height=20,width=80)

        #map tab 
        self.tab4 = tk.Frame(self.tabControl,bg=bgColor)
        self.tabControl.add(self.tab4,text="Map")
        self.map = MapCanvas(self.tab4) 

        #Weather Tab
        self.tab5 = tk.Frame(self.tabControl,bg=bgColor)
        self.tabControl.add(self.tab5,text="Weather")
        self.worldMap = WorldMap(self.tab5)
    
    #update the ui to a new state
    def update(self):
        
        self.context = self.ship.getSimState()
        tabCurrent = self.tabControl.index(self.tabControl.select())
        render = (time.time() - self.LastDrawTime)  > 1/float(config["UI"]["REFRESHRATE"])
        #Update the townhall
        self.header.updateTownHall(self.context["gold"],self.context["temp"],self.context["Time"])
        self.header.pack(expand=False)
        

        if tabCurrent == 0:
            #update the main page
            #update the villager list
            self.villagers.updateList(self.context["VillagerList"])
            self.villagers.pack(expand=False)

            #update the detailed villager tab
            self.villagerDisplay.update(self.context)
            self.villagers.pack(expand=False)

            #update cargo
            self.cargo.updateMarquee(self.context["cargo"])
            self.cargo.pack(expand=False)

            self.events.updateMarquee(self.context["eventHandler"].getEventDescriptions())
            self.events.pack(expand=False)

            #update the buildings
            self.buildingTab.updateText(self.context["BuildingString"])
            self.buildingTab.pack(expand=False)
                

            #update the Farm
            if render:
                self.crops.updateCrops(self.context["crops"],self.context["Time"])
                self.crops.pack(expand=False)
                self.LastDrawTime = time.time()
        
        if tabCurrent == 1:
            #update the task list
            self.bTask.updateTasks(self.context["town"].bulletin.getTaskList())
            self.bTask.pack()

        if tabCurrent == 3 and render:
            #update the map
            self.map.draw(self.context)

        
        if tabCurrent == 4:
            #update the map
            self.worldMap.getData(self.context)
        
        

        #Start it all over again
        self.root.after(1,self.update)

    def onClosing(self):
        if messagebox.askokcancel("Quit","Ready to stop?"):
            signal.raise_signal(signal.SIGTERM)
            self.root.destroy()
            
    def inititialize(self,name,initialState,pauseEvent):
        '''start the root and begin the execution'''
        try:
            self.root.title(name)
            self.tabControl.pack(expand=True,fill=BOTH)
            self.context = initialState
            self.ship = initialState["town"]
            self.root.after(10,self.update)
            self.root.protocol("WM_DELETE_WINDOW",self.onClosing)
            self.pauseEvent = pauseEvent
            self.root.mainloop()
        except:
            pass
    
    def deinitialize(self):
        self.displayThread.join()
        global exit
        exit = True

    def saveTown(self):
        self.pauseEvent.set()
        self.ship.save()
        print("Saved!")
        self.pauseEvent.clear()

    def loadTown(self):
        with filedialog.askopenfile(mode='rb', filetypes=[('Town Files', '*.SSF')]) as f:
            pickle.load(f)
        print("Loaded!")

#takes a List and displays each value
class ListDisplay(tk.Frame):
    def __init__(self,parent,width = 80,**kwargs):
        self.parent = parent
        super().__init__(parent,**kwargs)
        self.label = tk.Label(parent,text="Villagers",bg=config["UI"]["LIGHTBACKGROUND"])
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=10,width=width,bg=config["UI"]["BACKGROUND"])
        self.text.configure(fg=config["UI"]["FOREGROUND"])
        self.text.configure(borderwidth=0)
        self.text.pack(padx=10,pady=10)
        self.scr = tk.Scrollbar(self.text,orient=VERTICAL,command=self.text.yview,bg=config["UI"]["DARKBACKGROUND"])
    
    def updateList(self,newList):
        self.text.delete("1.0",END)
        for name in newList:
            self.text.insert(INSERT,str(name) + "\n")
        self.text.pack(padx=20,pady=1)

#Class to display the town as a map
class MapCanvas(tk.Frame):

    def __init__(self,root):
        self.mapCanvas = tk.Canvas(root,bg="grey",width=512,height=512)
        self.mapCanvas.pack()
        self.zoomLevel = 3
        self.center = (1,1)

        self.controlPanel = tk.Frame(root)
        self.controlPanel.configure(bg=config["UI"]["DARKBACKGROUND"])
        self.zoomButtons = tk.Frame(root)
        self.zoomButtons.configure(bg=config["UI"]["DARKBACKGROUND"])

        self.zoomInButton = tk.Button(self.zoomButtons,text="+",command=self.zoomIn)
        self.zoomInButton.pack()

        self.zoomOutButton = tk.Button(self.zoomButtons,text="-",command=self.zoomOut)
        self.zoomOutButton.pack()

        self.moveButtons = tk.Frame(self.controlPanel)
        self.moveButtons.configure(bg=config["UI"]["DARKBACKGROUND"])

        self.moveUpButton = tk.Button(self.moveButtons,text="^",command=self.moveCenterUp)
        self.moveUpButton.pack()

        self.moveDownButton = tk.Button(self.moveButtons,text="v",command=self.moveCenterDown)
        self.moveDownButton.pack(side=tk.BOTTOM) 

        self.moveLeftButton = tk.Button(self.moveButtons,text=">",command=self.moveCenterLeft)
        self.moveLeftButton.pack(side=tk.RIGHT)

        self.moveRightButton = tk.Button(self.moveButtons,text="<",command=self.moveCenterRight)
        self.moveRightButton.pack(side=tk.LEFT) 
        self.zoomButtons.pack(side=tk.LEFT)
        self.moveButtons.pack(side=tk.RIGHT)
        self.controlPanel.pack()

    def zoomOut(self):
        self.zoomLevel += 1
    
    def zoomIn(self):
        self.zoomLevel -= 1

    def moveCenterUp(self):
        self.center = (self.center[0],self.center[1]+1)
    
    def moveCenterDown(self):
        self.center = (self.center[0],self.center[1]-1)
    
    def moveCenterLeft(self):
        self.center = (self.center[0]+1,self.center[1])
    
    def moveCenterRight(self):
        self.center = (self.center[0] -1 ,self.center[1])

    #draw a rectangle
    def createBuilding(self,coords):
        #TODO: Make it look better
        self.mapCanvas.create_rectangle()
    
    def draw(self,data):
        '''draw the town'''
        #testing buildings
        buildings = []
        for b in data["town"].buildings:
            buildings.append(b.coords)
        
        #reset the window
        self.mapCanvas.delete("all")
        #calculate the draw window
        #if the zoom level is 9, just check the center
        if self.zoomLevel == 0:
            if self.center in buildings:
                self.mapCanvas.create_rectangle(0,0,512,512,fill="black")
        else:
            #determine the draw window by number of units 
            upperCorner = (self.center[0] - self.zoomLevel, self.center[1] + self.zoomLevel)
            lowerCorner = (self.center[0] + self.zoomLevel, self.center[1] - self.zoomLevel)
            unitSize = 512/2**(self.zoomLevel)
            for building in buildings:
                if Utilities.coordsInRange(building,upperCorner,lowerCorner):
                    pCoordsX = (building[0] - upperCorner[0]) * unitSize
                    pCoordsY = (upperCorner[1] - building[1]) * unitSize
                    self.mapCanvas.create_rectangle(pCoordsX,pCoordsY,pCoordsX+unitSize,pCoordsY+unitSize,fill="black")

#Display the world and weather
class WorldMap(tk.Frame):
    def __init__(self,root):
        self.mapCanvas = tk.Label(root)
        self.mapCanvas.pack()
        self.zoomLevel = 3
        self.center = (1,1)

        self.controlPanel = tk.Frame(root)
        self.controlPanel.configure(bg=config["UI"]["DARKBACKGROUND"])
        self.zoomButtons = tk.Frame(root)
        self.zoomButtons.configure(bg=config["UI"]["DARKBACKGROUND"])

        self.zoomInButton = tk.Button(self.zoomButtons,text="+",command=self.zoomIn)
        self.zoomInButton.pack()

        self.zoomOutButton = tk.Button(self.zoomButtons,text="-",command=self.zoomOut)
        self.zoomOutButton.pack()

        self.moveButtons = tk.Frame(self.controlPanel)
        self.moveButtons.configure(bg=config["UI"]["DARKBACKGROUND"])

        self.moveUpButton = tk.Button(self.moveButtons,text="^",command=self.moveCenterUp)
        self.moveUpButton.pack()

        self.moveDownButton = tk.Button(self.moveButtons,text="v",command=self.moveCenterDown)
        self.moveDownButton.pack(side=tk.BOTTOM) 

        self.moveLeftButton = tk.Button(self.moveButtons,text=">",command=self.moveCenterLeft)
        self.moveLeftButton.pack(side=tk.RIGHT)

        self.moveRightButton = tk.Button(self.moveButtons,text="<",command=self.moveCenterRight)
        self.moveRightButton.pack(side=tk.LEFT) 

        self.updateButton = tk.Button(self.moveButtons,text="Update",command=self.manualUpdate)
        self.updateButton.pack(side=tk.LEFT) 

        self.zoomButtons.pack(side=tk.LEFT)

        self.moveButtons.pack(side=tk.RIGHT)
        self.controlPanel.pack()
        
        self.context = None

    def initialize(self,data):
        self.mapDict = dict()
        acres = []
        for row in data["weather"].map:
            for acre in row:
                self.map[acre.pos] = self.mapCanvas.create_rectangle(pCoordsX,pCoordsY,pCoordsX+unitSize,pCoordsY+unitSize,fill=a.getWeatherColor())

        
        #reset the window
        self.mapCanvas.delete("all")
        #calculate the draw window
        #if the zoom level is 9, just check the center
        if self.zoomLevel == 0:
            if self.center in acres:
                self.mapCanvas.create_rectangle(0,0,512,512,fill="black")
        else:
            #determine the draw window by number of units 
            upperCorner = (self.center[0] - self.zoomLevel, self.center[1] + self.zoomLevel)
            lowerCorner = (self.center[0] + self.zoomLevel, self.center[1] - self.zoomLevel)
            unitSize = 512/2**(self.zoomLevel)
            for a in acres:
                if Utilities.coordsInRange(a.pos,upperCorner,lowerCorner):
                    pCoordsX = (a.pos[0] - upperCorner[0]) * unitSize
                    pCoordsY = (upperCorner[1] - a.pos[1]) * unitSize
    
    def zoomOut(self):
        self.zoomLevel += 1
    
    def zoomIn(self):
        self.zoomLevel -= 1

    def manualUpdate(self):
        self.draw(self.context)


    def getData(self,context):
        self.context = context

    def moveCenterUp(self):
        self.center = (self.center[0],self.center[1]+1)
    
    def moveCenterDown(self):
        self.center = (self.center[0],self.center[1]-1)
    
    def moveCenterLeft(self):
        self.center = (self.center[0]+1,self.center[1])
    
    def moveCenterRight(self):
        self.center = (self.center[0] -1 ,self.center[1])

    #draw a rectangle
    def createBuilding(self,coords):
        #TODO: Make it look better
        self.mapCanvas.create_rectangle()
    
    def draw(self,data):
        '''draw the town'''
        #TODO: Improve performance
        weatherData = data["weather"]
        img = Image.new(mode="RGB",size=(int(config["WORLDGEN"]["WORLDSIZEX"]),int(config["WORLDGEN"]["WORLDSIZEY"]))) # create the pixel map
        img = img.convert("RGB")
        #d = img.getdata()
        new_image = []
        for x in range(0,int(config["WORLDGEN"]["WORLDSIZEX"])):
            for y in range(0,int(config["WORLDGEN"]["WORLDSIZEY"])):
                new_image.append(weatherData.map[(x,y)].getWeatherColor())
 
        # update image data
        img.putdata(new_image)
        map = ImageTk.PhotoImage(image=img)
        self.mapCanvas.config(image=map)
        self.mapCanvas.pack()
        #self.mapCanvas.create_image()

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
        self.text.configure(fg=config["UI"]["FOREGROUND"])
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
        self.text.configure(fg=config["UI"]["FOREGROUND"])
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
        
        self.label = tk.Label(parent,text=title,bg=config["UI"]["LIGHTBACKGROUND"])
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=1,bg=config["UI"]["BACKGROUND"])
        self.text.configure(borderwidth=0)
        self.text.configure(fg=config["UI"]["FOREGROUND"])
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
        
        self.label = tk.Label(parent,text=title,bg=config["UI"]["LIGHTBACKGROUND"])
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=1,bg=config["UI"]["BACKGROUND"],borderwidth=0)
        self.text.tag_configure("center",justify='center')
        self.text.tag_add("center","1.0","end")
        self.text.configure(fg=config["UI"]["FOREGROUND"])
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
    def __init__(self,parent,shipName, **kwargs):
        self.parent = parent
        super().__init__(parent,width=20,height= 1, bg=config["UI"]["DARKBACKGROUND"])
        
        self.label = tk.Label(parent,text=shipName,bg=config["UI"]["LIGHTBACKGROUND"])
        self.label.pack(padx=0,pady=0)
        self.text = tk.Text(parent,height=2,bg=config["UI"]["BACKGROUND"],borderwidth=0)
        self.text.tag_configure("center",justify='center')
        self.text.configure(fg=config["UI"]["FOREGROUND"])
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
    def __init__(self,parent,height=1,width=1,side='top',**kwargs):
        self.parent = parent
        super().__init__(parent,width=width,height= height,**kwargs)
        
        self.text = tk.Text(parent,height=height,width=width)
        self.text.configure(bg=config["UI"]["BACKGROUND"])
        self.text.configure(fg=config["UI"]["FOREGROUND"])
        self.text.configure(borderwidth=0)
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
        super().__init__(parent,width=20,height= 1,bg=config["UI"]["DARKBACKGROUND"])
        
        #label
        self.label = tk.Label(parent,text="Crops",bg=config["UI"]["lightbackground"])
        self.label.configure(fg=config["UI"]["FOREGROUNDH"])
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
        self.taskCount.configure(background=config["UI"]["BACKGROUND"])
        self.taskCount.configure(borderwidth=0)
        self.taskCount.configure(fg=config["UI"]["FOREGROUND"])
        self.taskCount.pack(expand=False,side=side,padx=40)
        self.dropDownVariable = StringVar(parent)
        self.dropDownVariable.set("Choose Building")
        self.dropDown = OptionMenu(parent,self.dropDownVariable,"All","Farm","Mine",command=self.displayTasks)
        self.dropDown.configure(background=config["UI"]["LIGHTBACKGROUND"])
        self.dropDown.configure(borderwidth=0)
        self.dropDown.pack()

        self.text = tk.Text(parent,height=height,width=width)
        self.text.configure(bg=config["UI"]["BACKGROUND"])
        self.text.configure(borderwidth=0)
        self.text.configure(fg=config["UI"]["FOREGROUND"])
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
            self.dropDown.configure(bg=config["UI"]["BACKGROUND"])
            self.dropDown.pack()
            self.villagers = []

            self.relationsText = scrolledtext.ScrolledText(self.parent,height=10,width=width)
            self.relationsText.configure(bg=config["UI"]["BACKGROUND"])
            self.relationsText.configure(borderwidth=0)
            self.relationsText.configure(fg=config["UI"]["FOREGROUND"])
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

