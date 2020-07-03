from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *


    


class RestaurantSpace(object):
    def __init__(self, canvas):
        self.x_coord = {}
        self.y_coord = {}
        self.space_id = {}
        self.device_cluster_level = {}
        self.device_cluster_id = {}
        self.size = 0
        self.dict_sensor_motes = {}
        self.canvas = canvas
        

    def registerNode(self,x,y,space,level,id, obj):
        
        newMote = sensor_mote_data(self,x,y,space,level,id, obj)
        self.dict_sensor_motes[(x,y)] = newMote
        self.size += 1
        print("added")
        print(self.device_cluster_id)
        print(self.device_cluster_level)
        print(self.space_id)
        print(self.x_coord)
        print(self.y_coord)
    
    def deleteNode(self,x,y):
        idx = self.dict_sensor_motes[(x,y)].idx
        
        print(idx)
        del self.x_coord[idx]
        del self.y_coord[idx]
        del self.space_id[idx]
        del self.device_cluster_level[idx]
        del self.device_cluster_id[idx]
        self.size -= 1

        self.canvas.delete(cfg.myCanvas.rec_obj[idx])
        del self.dict_sensor_motes[(x,y)]
        print(self.device_cluster_id)
        print(self.device_cluster_level)
        print(self.space_id)
        print(self.x_coord)
        print(self.y_coord)

    def deleteAllNodes(self):
        print("delete all")
        for idx in range(self.size):
            self.deleteNode(self.x_coord[idx], self.y_coord[idx])
    
    def printMoteAt(self,x, y):
        if (x,y) in self.dict_sensor_motes.keys():
            return(self.dict_sensor_motes[(x,y)].printMote())
        else:
            print("No mote here")
        
    
    

class sensor_mote_data(object):
    def __init__(self,res,x,y,space,level,id, obj):
        self.idx = len(res.x_coord)
        self.res = res
        res.x_coord[self.idx] = x
        res.y_coord[self.idx] = y
        res.space_id[self.idx] = space
        res.device_cluster_level[self.idx] = level
        res.device_cluster_id[self.idx] = id 
        cfg.myCanvas.rec_obj[self.idx] = obj

    
    def printMote(self):
        return ("Mote x: " + str(self.res.x_coord[self.idx])
        + "\nMote y: " + str(self.res.y_coord[self.idx])
        + "\nMote space: " + str(self.res.space_id[self.idx])
        + "\nMote cluster level: " + str(self.res.device_cluster_level[self.idx])
        + "\nMote cluster id: " + str(self.res.device_cluster_id[self.idx]) 
        )


        