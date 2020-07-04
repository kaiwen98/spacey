from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *

# step -> box_len 

"""
Load JSON procedure:
- place photo with padding
- correct grid adjustment
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
cfg.hlcolor = "yellow" #glb highlight color
cursor = None #glb cursor
box_len = step #length of node
scale = 50 #num of grid lines along x axis
bg = None #backgroun sky blue
devinfo = {} #json purpose
imgpath = None #path of image
pady = 10 #padding for widget format
padx = 10
grid = None
filename = ""

img_x_bb1 = 0 #img bb box corner
img_y_bb1 = 0

config_op = ["x_bb1", "x_bb2", "y_bb1", "y_bb2", "img_x_bb1", "img_y_bb1", "box_len", "imgpath"]
configinfo = {}


def compile(path):
    for i in config_op:
        configinfo[i] = globals()[i] 
    # print(json.dumps(cfg.devinfo))
    with open(path, 'w') as outfile:
        json.dump(configinfo, outfile)
    with open(path) as infile:
        data = json.loads(infile.read())
    return json.dumps(data, indent=1)

def decompile(path):
    with open(path, 'r') as outfile:
        configinfo = json.load(outfile)
        # print(cfg.devinfo)
    for i in config_op:
        globals()[i] = configinfo[i]
    return json.dumps(configinfo, indent=1)