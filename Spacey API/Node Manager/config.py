from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *
import imgpro
import os
from os.path import dirname as dir, splitext, basename
import sys
import base64


#
# step -> box_len 

"""
Load JSON procedure:
- place photo with padding: cfg
- correct grid adjustment: cfg.scale
- Node information              x
"""

#root = dir(dir(dir(sys.executable)))
_root = dir(dir(__file__))

icon_path = os.path.join(_root, "images", "assets", "spacey_icon.ico")
gif_path = os.path.join(_root, "images", "assets", "spacey_icon.gif")
floorplan_folder_input = os.path.join(_root, "floorplan_images", "input floorplan")
floorplan_folder_output = os.path.join(_root, "floorplan_images", "output floorplan")
json_folder = os.path.join(_root, "json_files")

nodeOff_path = os.path.join(_root, "images", "assets","unoccupied_nodes.png")
nodeOn_path = os.path.join(_root, "images", "assets", "occupied_nodes.png")

def getbasename(path):
    return str(splitext(basename(path))[0])

def shorten_path(json_path):
    return "output_"+cfg.sessionName+".png"

def save_path():
    result = os.path.join(_root, "images", "output graphic", shorten_path(cfg.json_path))
    return result


root = None
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
node_idx = None
prev_node_idx = None
step = 5 #dist between each grid line
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
pady = 5 #padding for widget format
padx = 5
grid = None
filename = ""
img_padding = 0
image_flag = False

img_x_bb1 = 0 #img bb box corner
img_y_bb1 = 0

config_op = ["image_flag", "x_bb1", "x_bb2", "y_bb1", "y_bb2", "img_x_bb1", "img_y_bb1", "box_len", "prepimgpath", "scale", "box_len", "postimgpath", "img_padding"]

configinfo = {}
devinfo = {}

json_zipinfo = {}
json_occupancy = {}
json_hash = {}

def json_serialize_image(image_file):
    with open(image_file, mode='rb') as file:
        img = file.read()
    return base64.b64encode(img).decode("utf-8") #picture to bytes, then to string 


def json_deserialize_image(encoded_str,image_file):
    result = encoded_str.encode("utf-8")
    result = base64.b64decode(result)
    image_result = open(image_file, 'wb') # create a writable image and write the decoding result
    image_result.write(result)


def compile(root):
    zipinfo_path = os.path.join(root, cfg.sessionName+".json")
    occupancy_path = os.path.join(root, "occupancy", cfg.sessionName+".json")
    hash_path = os.path.join(root, "hash", cfg.sessionName+".json")

    for i in config_op:
        configinfo[i] = globals()[i] 
  
    for i in res.devinfo:
        devinfo[i] = getattr(res, i) 

    json_zipinfo["configinfo"] = json.dumps(configinfo)
    json_zipinfo["devinfo"] = json.dumps(devinfo)
    json_zipinfo["processed_img"] = json_serialize_image(cfg.save_path())
    json_occupancy = cfg.res.occupancy
    json_hash = cfg.res.tuple_idx

    with open(zipinfo_path, 'w') as outfile:
        json.dump(json_zipinfo, outfile)

    with open(occupancy_path, 'w') as outfile:
        json.dump(json_occupancy, outfile)

    with open(hash_path, 'w') as outfile:
        json.dump(json_hash, outfile)

    # Confirms the json file's existence and prints contents on console.
    with open(zipinfo_path) as infile:
        data = json.loads(infile.read())
    return str(json.dumps(data["configinfo"], indent=1)) 
    json_zipinfo.clear()
    json_occupancy.clear()
    json_hash.clear()


def decompile(root):
    zipinfo_path = os.path.join(root, cfg.sessionName+".json")
    occupancy_path = os.path.join(root, "occupancy", cfg.sessionName+".json")
    hash_path = os.path.join(root, "hash", cfg.sessionName+".json")
    

    with open(zipinfo_path, 'r') as outfile:
        json_zipinfo = json.load(outfile)

    with open(occupancy_path, 'r') as outfile:
        json_occupancy = json.load(outfile)
    
    with open(hash_path, 'r') as outfile:
        json_hash = json.load(outfile)

    configinfo = json.loads(json_zipinfo.get("configinfo"))
    devinfo = json.loads(json_zipinfo.get("devinfo"))
    processed_img = json_zipinfo.get("processed_img")
    temp_path = os.path.join(dir(root), 'images', 'output graphic', 'test1.png')
    json_deserialize_image(processed_img, temp_path)
    devinfo["tuple_idx"] = json_hash
    devinfo["occupancy"] = json_occupancy

    for i in config_op:
        globals()[i] = configinfo[i]
    
    for i in res.devinfo:
        setattr(res, i, devinfo[i])

    unpackFromJson()
    res.unpackFromJson()

    return json.dumps(json_zipinfo["configinfo"], indent=1)

def unpackFromJson():
    global img
  
    if cfg.image_flag is True: img = imgpro.floorPlan(postimgpath, cfg.myCanvas.canvas, False)
    grid.refresh(delete = False, resize = False)
    cfg.myCanvas.restoreTagOrder()

def base(filename): 
    print(filename)
    return os.path.basename(filename)