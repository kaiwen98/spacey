from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *
import imgpro
import os

# step -> box_len 

"""
Load JSON procedure:
- place photo with padding: cfg
- correct grid adjustment: cfg.scale
- Node information              x
"""

x_list = [] #list of all possible coordinates
y_list = []
img = None #image file 
num_coordinates_max = 0 #max num of coordinates
res = None #glb restaurant space
node = None #node pointer
x, y = 0, 0 #mid coords of the latest node placed
x_bb1, y_bb1 = 0,0 #Bounding box coordinates of active canva region (blue)
x_bb2, y_bb2 = 0,0
deposit_flag = True #If a node can be deposit on the spot
myCanvas = None #glb myCanvasObj
step = 3 #dist between each grid line
toggle = 0 #toggle btw entry[left] or canvas
initflag = 0 #detect correct user input
error = None #error obj
error_font = None #error font
json_font = None #json font
max_step = 200 #prevent grid line from scaling down to self collapse
hlcolor = "yellow" #glb highlight color
cursor = None #glb cursor
box_len = step #length of node
scale = 50 #num of grid lines along x axis
bg = None #backgroun sky blue
prepimgpath = None #path of image
postimgpath = None
pady = 10 #padding for widget format
padx = 10
grid = None
filename = ""

img_x_bb1 = 0 #img bb box corner
img_y_bb1 = 0

config_op = ["x_bb1", "x_bb2", "y_bb1", "y_bb2", "img_x_bb1", "img_y_bb1", "box_len", "prepimgpath", "scale", "box_len", "postimgpath"]

devinfo = {} #json purpose
configinfo = {}
zipinfo = {}


def compile(path):
    for i in config_op:
        configinfo[i] = globals()[i] 
  
    for i in res.devinfo:
        devinfo[i] = getattr(res, i) 

    zipinfo["configinfo"] = configinfo
    zipinfo["devinfo"] = devinfo

    with open(path, 'w') as outfile:
        json.dump(zipinfo, outfile)

    with open(path) as infile:
        data = json.loads(infile.read())
    return json.dumps(data, indent=1)


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

    
    unpackFromJson()
    res.unpackFromJson()

    return json.dumps(zipinfo, indent=1)

def unpackFromJson():
    global img
    img = imgpro.floorPlan(postimgpath, cfg.myCanvas.canvas, False)
    grid.refresh(delete = False, resize = False)
    cfg.myCanvas.restoreTagOrder()

def base(filename): 
    print(filename)
    return os.path.basename(filename)