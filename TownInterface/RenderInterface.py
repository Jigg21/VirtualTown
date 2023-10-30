from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d import core
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
        # Reparent the model to render.
        # Apply scale and position transforms on the model.
        planetTexture = self.loader.loadTexture("Resources/Map.png")
        planetHeight = self.loader.loadTexture("Resources/heightfield.png")
        self.shaderTerrain = core.ShaderTerrainMesh()
        self.shaderTerrain.setHeightfield(planetHeight)
        self.shaderTerrain.chunk_size = 64
        self.shaderTerrain.generate()

        #add terrain to stage
        self.shaderTerrain.update_enabled = True
        self.terrain = self.render.attach_new_node(self.shaderTerrain)


        #get terrain shader
        terrain_shader = core.Shader.load(core.Shader.SL_GLSL, "TownInterface/terrain.vert.glsl", "TownInterface/terrain.frag.glsl")
        self.terrain.set_shader(terrain_shader)
        self.terrain.set_shader_input("camera", self.camera)
        self.terrain.set_scale(25,25,2)
        self.terrain.set_pos(-10, -10, 0)



        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (math.pi / 180.0)
        self.camera.setPos(40 * math.sin(angleRadians), -40 * math.cos(angleRadians), 7)
        self.camera.setHpr(angleDegrees, -10, 0)
        return Task.cont

    def initialize(self):
        self.run()

