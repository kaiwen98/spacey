from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *



x_list = []
y_list = []
img = None
filename = ""
num_coordinates_max = 0
res = None
node = None
x, y = 0, 0
x_bb1, y_bb1 = 0,0
x_bb2, y_bb2 = 0,0
deposit_flag = True
myCanvas = None
step = 0
toggle = 0
initflag = 0
error = None
error_font = None
max_step = 200
num_coordinates_max = 0
cfg.hlcolor = "yellow"
cursor = None
box_len = step
scale = 0
bg = None