from direct.showbase.ShowBase import ShowBase
import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
import math
import sys
from Utilities import CONST

PI = math.pi

def removeInfintessimals(value):
    if value < sys.float_info.epsilon*2:
        return 0
    else:
        return value

def generateSphereCloud(resLon,resLat):
    cloud = []
    #get the coordinate at all lats and longs 
    for t in range(1,resLon+2):
        for s in range(1,resLat+2):
            x = math.cos((2*PI)/t) * math.cos((2*PI)/s) 
            y = math.sin((2*PI)/t) * math.cos((2*PI)/s) 
            z = math.sin((2*PI)/s)
            x = removeInfintessimals(x)
            y = removeInfintessimals(y)
            z = removeInfintessimals(z)

            cloud.append("{x} {y} {z}\n".format(x=x,y=y,z=z))
    return cloud


class planetRender():
    def __init__(self,resLon,resLat):
        pass



class Renderer(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # pointCloud = generateSphereCloud(10,10)
        # with open("points.xyz",'w') as f:
        #     for point in pointCloud:
        #         f.write(point)
        #         print(point)
        # points = np.loadtxt('points.xyz')
        # cloud = pv.PolyData(points)
        # mesh = cloud.delaunay_2d()
        # mesh.save('mesh.ply')
        # Load the environment model.
        self.scene = self.loader.loadModel("Resources/plane.fbx")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.1, 0.1, 0.1)
        self.scene.setPos(-8, 42, 0)
        self.scene.setHpr(0,0,0)
        planetTexture = self.loader.loadTexture("Resources/Map.png")
        self.scene.setTexture(planetTexture)

    def initialize(self):
        self.run()

