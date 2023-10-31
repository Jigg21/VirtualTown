from PIL import Image
import os
import sys
root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)
from Utilities.ConfigReader import ConfigData as config
import random
import Utilities.Utilities
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt
from progress.bar import PixelBar
import numpy as np
import math


SIZEX = int(config["WORLDGEN"]["WORLDSIZEX"])
SIZEY = int(config["WORLDGEN"]["WORLDSIZEY"])

CARDINAL = [(1,0),(0,1),(-1,0),(0,-1)]


class WorldObj():
    def __init__(self) -> None:
        self.map = Image.new(mode="RGB",size=(SIZEX,SIZEY)) # create the pixel map
        #pos:mapacre dictionary
        self.mapObj = dict()
        #self.map = self.map.convert("RGB")
        self.regions = []
        #noise = PerlinNoise(octaves=12)
        self.plates = []



        #create acres
        with PixelBar('Generating Acres',max=SIZEX*SIZEY) as bar:
            for i in range(SIZEX):
                for j in range(SIZEY):
                    acre = MapAcre((i,j))
                    self.mapObj[(i,j)] = acre
                    bar.next()

        #create regions
        # for i in range(int(config["WORLDGEN"]["BIOMECOUNT"])):
        #s     region = MapRegion((random.choice(range(SIZEX)),random.choice(range(SIZEY))),self.mapObj)
        #     self.regions.append(region)



        
        
        #create plates    
        for t in range(int(config["WORLDGEN"]["PLATECOUNT"])):
            self.plates.append(MapPlate((random.choice(range(SIZEX)),random.choice(range(SIZEY)))))
            
        #assign regions to plates
        self.makeVoronoiPlates()

        newImage=[]


        for x in range(SIZEX):
            for y in range(SIZEY):
                newImage.append(self.mapObj[(x,y)].getColor())


        self.map.putdata(newImage)
        self.map.save("Resources/Map.png")

    def assignAcresViaFrontier(self):
        emptyAcres = SIZEX * SIZEY
        with PixelBar('Filling Regions',max=emptyAcres) as bar:
            while emptyAcres > 0:
                for region in self.regions:
                    new = region.getRandomFrontier(self.mapObj)
                    if new != None:
                        emptyAcres -= 1
                        bar.next()
    
    def makeVoronoiPlates(self):
        emptyAcres = SIZEX * SIZEY
        #for each acre on the map
        with PixelBar('Filling Regions',max=emptyAcres) as bar:
            for acre in self.mapObj.values():
                bar.next() 
                closest = None
                closestVal = 10000000
                for seed in self.plates:
                    #get forward distance
                    dist = Utilities.Utilities.getPythagoreanDistance(seed.center,acre.pos)
                    if  dist < closestVal:
                        closestVal = dist
                        closest = seed

                    x = abs(seed.center[0] - acre.pos[0])
                    y = abs(seed.center[1] - acre.pos[1])
                    xPrime = SIZEX - x
                    yPrime = SIZEY - y
                    xMin, yMin = 0, 0
                    if x > xPrime:
                        xMin = xPrime
                    else:
                        xMin = x
                    
                    if y > yPrime:
                        yMin = yPrime
                    else:
                        yMin = y
                    
                    rtwDist = (xMin**2 + yMin**2)**0.5
                    if rtwDist < closestVal:
                        closestVal = rtwDist
                        closest = seed
                    #print("P1:P2 - {Pa}:{Pb} | FDist : {dist} RtWDist : {rtwDist}".format(Pa=acre.pos,Pb=seed.center,dist=dist,rtwDist=rtwDist))
                acre.setRegion(closest)


class MapAcre():
    '''Class that defines the smallest unit of the map'''
    def __init__(self,pos) -> None:
        self.pos = pos
        self.region = None

    def setRegion(self,region):
        self.region = region

    def getColor(self):
        if self.region.center == self.pos:
            return (255,255,255)
        return self.region.color
    
    def isOwned(self):
        return self.region == None

    def getClosestRegion(self,regions):
        closest = None
        closestVal = 10000000
        for seed in regions:
            #get rtw distance
            dist = Utilities.getPythagoreanDistance(self.pos,seed.center)
            if  dist < closestVal:
                closestVal = dist
                closest = seed

        self.setRegion(closest)

class MapRegion():
    '''Class that splits the map into polygon regions'''
    def __init__(self,center,world,color = None) -> None:
        self.center = center
        self.acres = []
        self.frontier = self.getEligibileNeighbors(center,world)
        if color == None:
            self.color = tuple(np.random.choice(range(256), size=3))

    def distanceToPoint(self,pos):
        Utilities.getPythagoreanDistance(self.center,pos)
    

    def getEligibileNeighbors(self,pos,world):
        neighbors = []
        for dir in CARDINAL:
            newPos = tuple(sum(x) for x in zip(pos, dir))
            if Utilities.Utilities.coordsOnScreen(SIZEX,SIZEY,newPos):
                if world[newPos].region == None:
                    neighbors.append(world[newPos])
        return neighbors
                    


    def getRandomFrontier(self,world):
        #if there's no Frontier, just pass
        if len(self.frontier) == 0:
            return None
        #get a random unowned frontier acre
        randomAcre = random.choice(self.frontier)
        while randomAcre.region != None:
            self.frontier.remove(randomAcre)
            if len(self.frontier) == 0:
                return None
            else:
                randomAcre = random.choice(self.frontier)
        #add the acre to the region
        randomAcre.setRegion(self)
        self.acres.append(randomAcre)
        self.frontier.remove(randomAcre)
        #add the new neighbors to the frontier
        newNeighbors = self.getEligibileNeighbors(randomAcre.pos,world)
        if len(newNeighbors) > 0:
            self.frontier.extend(newNeighbors)
        return randomAcre
        
        

class MapPlate():
    '''simulates Tectonic plates'''
    def __init__(self, center,color = None) -> None:
        self.center = center
        #Representative color
        if color == None:
            self.color = tuple(np.random.choice(range(256), size=3))

    def addAcre(self,acreCoords):
        self.acres.append(acreCoords)




