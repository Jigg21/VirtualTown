
from PIL import Image
import os
import sys
root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)
from ConfigReader import ConfigData as config
import random
import CONST

class WorldObj():
    def __init__(self) -> None:
        self.map = Image.new(mode="RGB",size=(int(config["WORLDGEN"]["WORLDSIZE"]),int(config["WORLDGEN"]["WORLDSIZE"]))) # create the pixel map
        self.mapObj = dict()
        #self.map = self.map.convert("RGB")
        seeds = dict()

        #generate a given number of biome seeds
        for biome in range(int(config["WORLDGEN"]["BIOMECOUNT"])+1):
            pos = (random.randrange(0,int(config["WORLDGEN"]["WORLDSIZE"])), random.randrange(0,int(config["WORLDGEN"]["WORLDSIZE"])))
            biomeChoice = random.choice(list(CONST.Biomes))
            seeds[pos] = biomeChoice
            print("{BIOME} centered at {POS}".format(BIOME=biomeChoice,POS=pos))

        newImage = []
        i=0
        #for each biome on the world map
        for x in range(0,int(config["WORLDGEN"]["WORLDSIZE"])):
            for y in range(0,int(config["WORLDGEN"]["WORLDSIZE"])):
                biome = None
                if (x,y) not in seeds:
                    closest = getClosestSeed((x,y),seeds)
                    self.mapObj[(x,y)] = MapAcre((x,y),seeds[closest])
                    biome = seeds[closest]
                else:
                    self.mapObj[(x,y)] = MapAcre((x,y),seeds[(x,y)])
                    biome = seeds[(x,y)]
                if biome == CONST.Biomes.DESERT:
                    newImage.append((196, 193, 100))
                elif biome == CONST.Biomes.FORREST:
                    newImage.append((9, 189, 81))
                elif biome == CONST.Biomes.LAKE:
                    newImage.append((0, 0, 200))
                elif biome == CONST.Biomes.PLAINS:
                    newImage.append((93, 158, 89))
                else:
                    newImage.append((0,0,0))
                

        print(len(newImage))
        self.map.putdata(newImage)
        self.map.save("Map.png")


class MapAcre():
    def __init__(self,pos,biome) -> None:
        self.pos = pos
        self.biome = biome

def getClosestSeed(pos,seeds):
    closest = None
    closestVal = 10000000
    for seed in seeds.keys():
        dist = getPythagoreanDistance(pos,seed)
        if  dist < closestVal:
            closestVal = dist
            closest = seed

    return closest


def getPythagoreanDistance(pos1,pos2):
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**.5

def main():
    WorldObj()

if __name__ == "__main__":
    main()