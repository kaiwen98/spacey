################################################# SPACEY Initiation GUI Wizard #############################################
# Author: Looi Kai Wen                                                                                                     #
# Last edited: 07/07/2020                                                                                                  #
# Summary:                                                                                                                 #
#   For use by BLE network administrators to configure their database with invariant information,                          #
#   eg. relative coordinates of the sensor mote, cluster level, etc.                                                       #
############################################################################################################################




from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *
from functools import partial
from queue import Queue
import imgpro
import sys
from os.path import dirname as dir

from PIL import Image as p_Image, ImageEnhance as p_ImageEnhance, ImageOps as p_ImageOp, ImageTk as p_ImageTk
import os

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

def track(event):
    print("x: "+ str(event.x) + "\ny: " + str(event.y))

def quit(event):
    cfg.root.destroy()

def focus_toggle1(event, widget):
    cfg.toggle = 1- cfg.toggle
    if cfg.toggle:
        cfg.myCanvas.canvas.focus_set()
    else: 
        widget.focus_set()

def focus_toggle(mode, widget = None):
    if mode:
        cfg.myCanvas.canvas.focus_set()
    else: 
        widget.focus_set()
def focus_canvas():
    focus_toggle(mode = True)



### Initialization of window ###



def setup():
    cfg.root = Tk()
    global canvas_w, canvas_h, image_file
    #cfg.root.state('zoomed') # Full window view
    cfg.root.title('Spacey Node Manager') # Set title name
    cfg.root.configure(bg = "gray22") #Bg colour
    # Icon of the window
    cfg.root.iconbitmap(cfg.icon_path)
    #cfg.root.geometry('1280x720')  #size of w
    cfg.root.update_idletasks()
    factor = 1
    cfg.root.geometry(str(int(1366*factor)) + "x" + str(int(768*factor)))  #size of w
    cfg.root.resizable(0, 0)
    

    ### Creation of GUI map ###
    print(cfg.root.winfo_height())
    print(cfg.root.winfo_width())
    print(cfg.root.winfo_geometry())
    print(cfg.root.winfo_screenheight())
    print(cfg.root.winfo_screenwidth())

   

    ### Creation of GUI map ###
    min_screenwidth = 1366
    min_screenheight = 768
    cfg.canvas_w, cfg.canvas_h = 768, 768
    #cfg.canvas_w, cfg.canvas_h = 1200, 1000
    w, h = 1366/8*5, 1000
    
    frame_canvas = LabelFrame(cfg.root, text = "Map", width = cfg.canvas_w, height = cfg.canvas_h, bg = "gray40") # Set frame to embed canvas
    #frame_canvas.pack(padx = 20, pady = 20, side = RIGHT) # Align right with padding
    #frame_canvas.pack_propagate(False) # Fix frame size to dimensions


    cfg.myCanvas = spc.myCanvasObject(frame_canvas, cfg.canvas_w, cfg.canvas_h) # Set canvas within frame
    #cfg.myCanvas.canvas.pack(padx = 10, pady = 10) # Set padding
  
    cfg.res = RestaurantSpace(cfg.myCanvas.canvas)
    cursor = spc.CursorNode(cfg.myCanvas.canvas)  # Creates rectangle cursor (in red)
    cfg.grid = spc.CanvasGridFrame(cfg.myCanvas.canvas, cfg.scale) # Creates gridlines so that the boxes inserted will appear more organised
    
    
    
   
    ### Creation of Config menu ###
    
    _frame_menu = LabelFrame(cfg.root, text = "Configurations", width = int(w/1.8), height = h, bg = "gray40")
    _frame_menu.pack(padx = 20, pady = 20, side = LEFT, expand = 1, anchor = "w")
    _frame_menu.pack_propagate(False)
    
    menu_canvas = Canvas(_frame_menu, borderwidth=0, bg = "gray40", highlightbackground = "gray40")
    yscroll = Scrollbar(_frame_menu, orient = "vertical", command = menu_canvas.yview)

    yscroll.pack(padx = 2, pady = 2, side = LEFT, fill = Y)
    menu_canvas.pack(side = LEFT, expand = True, fill = "both")
    menu_canvas.configure(yscrollcommand = yscroll.set)
    frame_menu = Frame(menu_canvas, borderwidth=0, bg = "gray40")
    frame_menu.pack()
    menu_canvas.create_window((0,0), window=frame_menu, anchor="nw")
    frame_menu.bind("<Configure>", lambda event, canvas=menu_canvas: onFrameConfigure(canvas))


    frame_menu1 = LabelFrame(frame_menu, text = "Menu 1", width = w/4, height = h, bg = "gray40")
    frame_menu1.pack(side = LEFT, expand = 1, fill = X)
    frame_menu1.pack_propagate(False)

    help = spc.menu_help(frame_menu1, w, h)
    upload = spc.menu_upload(frame_menu1, w, h)
    dev_info = spc.menu_devinfo(frame_menu1, w, h)
    status = spc.menu_status(frame_menu1, w, h)
    cfg.error = spc.menu_debug(frame_menu1, w, h)
    
    
    
    # Set callbacks for cursor
    cursor.setCallback(status.updateText)
    cursor.setCallback(dev_info.highlightDeviceInfo)
    cursor.setCallback(lambda i: focus_toggle(i, dev_info.keyEntry))

    # Set callbacks for dev_info
    dev_info.setCallback(cursor.deposit)
    dev_info.setCallback(cursor.nodeDetectCallback)
    dev_info.setCallback(lambda i: focus_toggle(i, dev_info.keyEntry))
    dev_info.setCallback(focus_canvas)
    


    frame_menu2 = LabelFrame(frame_menu, text = "Menu 2", width = w/4, height = h, bg = "gray40")
    frame_menu2.pack(side = LEFT, expand = 1)
    frame_menu2.pack_propagate(False)

    nodescale = spc.node_scaleshift(frame_menu2, 3, w, h)
    #upload2 = spc.img_scaleshift(frame_menu2, 10)
    dev_info2 = spc.img_xyshift(frame_menu2, 10, w, h)
    maprefresh2 = spc.map_refresh(frame_menu2, 10, w, h)
    jsonview = spc.json_viewer(frame_menu2, w, h)

    
    frame_canvas.pack(padx = 20, pady = 20, side = RIGHT) # Align right with padding
    frame_canvas.pack_propagate(False) # Fix frame size to dimensions
    cfg.myCanvas.canvas.pack(padx = 10, pady = 10) # Set padding

    cfg.root.bind('<Escape>', lambda event: destroy(event, cfg.root))
    cfg.root.bind('<Control-z>', lambda event: focus_toggle1(event, dev_info.keyEntry))
    ##############################################################################
    #cfg.res.decompile('mc.bin')
    cfg.myCanvas.canvas.focus_set()

    cfg.root.mainloop()

def destroy(event, root):
    root.destroy()


def main():
    setup()
    

main()