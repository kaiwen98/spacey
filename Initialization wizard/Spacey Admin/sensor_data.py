from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *

class myCanvasObject(object):
    def __init__(self,frame, width, height):
        self.canvas = Canvas(frame, width = width, height = height)
        self.dict_coord_rec = {}
    


class RestaurantSpace(object):
    def __init__(self):
        self.x_coord = []
        self.y_coord = []
        self.space_id = []
        self.device_cluster_level = []
        self.device_cluster_id = []
        self.size = 0
        self.dict_sensor_motes = {}
        self.obj = []

    def registerNode(self,x,y,space,level,id, obj):
        newMote = sensor_mote_data(self,x,y,space,level,id, obj)
        self.dict_sensor_motes[(x,y)] = newMote
        self.size += 1
    
    def deleteNode(self,x,y, canvas):
        if( self.dict_sensor_motes.pop((x,y), True)):
            print("Cannot delete!")
            return
        idx = self.dict_sensor_motes[(x,y)].idx
        del self.x_coord[idx]
        del self.y_coord[idx]
        del self.space_id[idx]
        del self.device_cluster_level[idx]
        del self.device_cluster_id[idx]
        self.size -= 1
        canvas.delete(self.obj)


    
    def printMoteAt(self,x, y):
        if (x,y) in self.dict_sensor_motes.keys():
            return(self.dict_sensor_motes[(x,y)].printMote())
        else:
            print("No mote here")
        
    
    

class sensor_mote_data(object):
    def __init__(self,res,x,y,space,level,id, obj):
        self.idx = len(res.x_coord)
        self.res = res
        res.x_coord.append(x)
        res.y_coord.append(y)
        res.space_id.append(space)
        res.device_cluster_level.append(level)
        res.device_cluster_id.append(id) 
        res.obj.append(obj)

    
    def printMote(self):
        return ("Mote x: " + str(self.res.x_coord[self.idx])
        + "\nMote y: " + str(self.res.y_coord[self.idx])
        + "\nMote space: " + str(self.res.space_id[self.idx])
        + "\nMote cluster level: " + str(self.res.device_cluster_level[self.idx])
        + "\nMote cluster id: " + str(self.res.device_cluster_id[self.idx]) 
        )


        