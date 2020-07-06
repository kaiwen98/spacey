from p_sensor_data import *
import os
import json

# step -> box_len 

"""
Load JSON procedure:
- place photo with padding: cfg
- correct grid adjustment: cfg.scale
- Node information              x
"""
res = RestaurantSpace()
scale = 0 
x_bb1, y_bb1 = 0,0 #Bounding box coordinates of active canva region (blue)
x_bb2, y_bb2 = 0,0
cursor = None #glb cursor
box_len = 0 #length of node
prepimgpath = None #path of image
postimgpath = None
img_x_bb1, img_y_bb1 = 0,0 #img bb box corner
canvas_xlen = 0
canvas_ylen = 0
img_padding = 0


config_op = ["x_bb1", "x_bb2", "y_bb1", "y_bb2", "img_x_bb1", "img_y_bb1", "box_len", "prepimgpath", "scale", "box_len", "postimgpath", "img_padding"]

devinfo = {} #json purpose
configinfo = {}
zipinfo = {}

def decompile(path):
    with open(path, 'r') as outfile:
        zipinfo = json.load(outfile)
    configinfo = zipinfo.get("configinfo")
    devinfo = zipinfo.get("devinfo")
    print(devinfo)
    for i in config_op:
        globals()[i] = configinfo[i]
    
    for i in res.devinfo:
        setattr(res, i, devinfo[i])
    
    cfg.canvas_xlen = x_bb2 - x_bb1
    cfg.canvas_ylen = y_bb2 - y_bb1
    cfg.img_x_bb1 -= x_bb1
    cfg.img_y_bb1 -= y_bb1
    #cfg.box_len *= 2
    res.unpackFromJson()

def base(filename): 
    print(filename)
    return os.path.basename(filename)