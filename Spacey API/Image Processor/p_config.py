from p_sensor_data import *
import os
import json
from os.path import dirname as dir, basename, splitext
from tkinter import font
from tkinter import *

# step -> box_len 

"""
Load JSON procedure:
- place photo with padding: cfg
- correct grid adjustment: cfg.scale
- Node information              x
"""
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

help_font = None

#path = dir(dir(__file__))
path = dir(os.path.dirname(sys.executable))
res = RestaurantSpace()


json_folder = os.path.join(path, "json_files")
json_path = os.path.join(json_folder, "lol.json")
save_path = os.path.join(path, "images", "output graphic", "output_"+str(splitext(basename(json_path))[0])+".png")
nodeOff_path = os.path.join(path, "images", "assets","unoccupied_nodes.png")
nodeOn_path = os.path.join(path, "images", "assets", "occupied_nodes.png")
icon_path = os.path.join(path, "images", "assets", "spacey_icon.ico")


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