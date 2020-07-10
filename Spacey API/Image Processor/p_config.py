
import os
import json
from os.path import dirname as dir, basename, splitext
from tkinter import font
from tkinter import *
import p_config as cfg
import base64

# step -> box_len 

"""
Load JSON procedure:
- place photo with padding: cfg
- correct grid adjustment: cfg.scale
- Node information              x
"""
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

path = dir(dir(__file__))
#path = dir(dir(dir(sys.executable)))
res = RestaurantSpace()


json_folder = os.path.join(path, "json_files")
json_path = os.path.join(json_folder, "lol.json")




nodeOff_path = os.path.join(path, "images", "assets","unoccupied_nodes.png")
nodeOn_path = os.path.join(path, "images", "assets", "occupied_nodes.png")
icon_path = os.path.join(path, "images", "assets", "spacey_icon.ico")
gif_path = os.path.join(path, "images", "assets", "spacey_icon.gif")

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



"""

path = dir(dir(__file__))
#path = dir(dir(dir(sys.executable)))

nodeOff_path = os.path.join(path, "images", "assets","unoccupied_nodes.png")
nodeOn_path = os.path.join(path, "images", "assets", "occupied_nodes.png")
icon_path = os.path.join(path, "images", "assets", "spacey_icon.ico")
gif_path = os.path.join(path, "images", "assets", "spacey_icon.gif")
image_folder = os.path.join(path, "images", "output graphic")
json_folder = os.path.join(path, "json_files")


json_coord = {}


def save_path():
    return os.path.join(image_folder, "output_"+cfg.sessionName+".png")


def getbasename(path):
    return splitext(basename(path))[0]


def json_serialize_image(image_file):
    with open(image_file, mode='rb') as file:
        img = file.read()
    return base64.b64encode(img).decode("utf-8") #picture to bytes, then to string 


def json_deserialize_image(encoded_str,image_file):
    result = encoded_str.encode("utf-8")
    result = base64.b64decode(result)
    image_result = open(image_file, 'wb') # create a writable image and write the decoding result
    image_result.write(result)



def decompile(root):
    coord_path = os.path.join(root, "coord", cfg.sessionName+".json")
    occupancy_path = os.path.join(root, "occupancy", cfg.sessionName+".json")

    with open(coord_path, 'r') as outfile:
        cfg.json_coord = json.load(outfile)
    
    with open(occupancy_path, 'r') as outfile:
        cfg.json_occupancy = json.load(outfile)

    cfg.processed_img = json_coord.get("processed_img")
    json_deserialize_image(cfg.processed_img,cfg.save_path())
    cfg.box_len = json_coord.get("box_len")
    json_coord.pop("processed_img")
    json_coord.pop("box_len")
    
    cfg.occupancy = cfg.json_occupancy


