from PIL import Image
import os
import sys
root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)
from ConfigReader import ConfigData as config
import random
import CONST
import opensimplex
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt
from progress.bar import PixelBar

class WorldObj():
    def __init__(self) -> None:
        self.map = Image.new(mode="RGB",size=(int(config["WORLDGEN"]["WORLDSIZE"]),int(config["WORLDGEN"]["WORLDSIZE"]))) # create the pixel map
        #pos:mapacre dictionary
        self.mapObj = dict()
        #self.map = self.map.convert("RGB")
        regions = []
        #noise = PerlinNoise(octaves=12)
        
        for i in range(config["WORLDGEN"]["BIOMECOUNT"]):
            self.regions = MapRegion(random.randrange(0,config["WORLDGEN"]["WORLDSIZE"]))
        


        newImage=[]
        size = int(config["WORLDGEN"]["WORLDSIZE"])
        with PixelBar('Generating terrain',max=size**2) as bar:
            for i in range(size):
                for j in range(size):
                    newImage.append((int(opensimplex.noise2(i,j)*255),0,0))
                    bar.next()

        self.map.putdata(newImage)
        self.map.save("Map.png")


class MapAcre():
    '''Class that defines the smallest unit of the map'''
    def __init__(self,pos,biome) -> None:
        self.pos = pos
        self.biome = biome
        self.region = None
        self.Plate = None

    def setRegion(self,region):
        self.region = region

class MapRegion():
    '''Class that splits the map into polygon regions'''
    def __init__(self,center) -> None:
        self.center = center
        self.acres = []

    def distanceToPoint(self,pos):
        CONST.getPythagoreanDistance(self.center,self.pos)

def getClosestSeed(pos,seeds):
    closest = None
    closestVal = 10000000
    for seed in seeds.keys():
        dist = CONST.getPythagoreanDistance(pos,seed)
        if  dist < closestVal:
            closestVal = dist
            closest = seed

    return closest




def main():
    WorldObj()

if __name__ == "__main__":
    main()