################################################# SPACEY Initiation GUI Wizard #############################################
# Author: Looi Kai Wen                                                                                                     #
# Last edited: 28/06/2020                                                                                                  #
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

scaleNum = 50

def uploadimage(filename):
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select File", filetypes = (("jpeg files","*.jpg"),("all files","*.*")))

def track(event):
    print("x: "+ str(event.x) + "\ny: " + str(event.y))

def quit(event):
    exit()

### Initialization of window ###



def setup(root):
    global canvas_w, canvas_h
    root.state('zoomed') # Full window view
    root.title('Title') # Set title name
    root.configure(bg = "gray22") #Bg colour
    # Icon of the window
    # root.iconbitmap('')
    #root.geometry('1200x1200')  #size of w

    ### Creation of GUI map ###

    cfg.canvas_w, cfg.canvas_h = 1200, 1000
    w, h = 1200, 1000
    print("from main: " + str(cfg.canvas_w))
    frame_canvas = LabelFrame(root, text = "Map", width = w, height = h, bg = "gray40") # Set frame to embed canvas
    frame_canvas.pack(padx = 20, pady = 20, side = RIGHT) # Align right with padding
    frame_canvas.pack_propagate(False) # Fix frame size to dimensions


    canvas_obj = myCanvasObject(frame_canvas, width = w, height = h) # Set canvas within frame
    canvas_obj.canvas.pack(fill = "both", expand = 1, padx = 10, pady = 10) # Set padding
    my_canvas = canvas_obj.canvas
    
    grid = spc.CanvasGridFrame(my_canvas, scaleNum) # Creates gridlines so that the boxes inserted will appear more organised
    cursor = spc.CursorNode(my_canvas,xpos = 513,ypos = 392)  # Creates rectangle cursor (in red)


    ### Creation of Config menu ###

    frame_menu = frame_menu1 = LabelFrame(root, text = "Configurations", width = w/2, height = h, bg = "gray40")
    frame_menu.pack(padx = 20, pady = 20, side = LEFT, expand = 1)
    frame_menu.pack_propagate(False)

    frame_menu1 = LabelFrame(frame_menu, text = "Configurations", width = w/3, height = h, bg = "gray40")
    frame_menu1.pack(side = LEFT, expand = 1)
    frame_menu1.pack_propagate(False)

    upload = spc.menu_upload(frame_menu1)
    dev_info = spc.menu_devinfo(frame_menu1)
    dev_info.setCallback(cursor.deposit)
    status = spc.menu_status(frame_menu1)
    cursor.setCallback(status.updateText)
    cursor.setCallback(dev_info.highlight_dev_info)

    #cursor.setDevInfo(dev_info)

    frame_menu2 = LabelFrame(frame_menu, text = "Configurations", width = w/4, height = h, bg = "gray40")
    frame_menu2.pack(side = LEFT, expand = 1)
    frame_menu2.pack_propagate(False)

    upload2 = spc.menu_upload(frame_menu2)
    dev_info2 = spc.menu_devinfo(frame_menu2)
    maprefresh2 = spc.map_refresh(frame_menu2, grid, scaleNum, cursor)

    #displayco1 = Label(frame, text = "", bg = "yellow")
    #displayco1.grid(row = 0,column = 0, sticky = W)
    #displayco2 = Label(frame, text = "", bg = "yellow")
    #displayco2.grid(row = 1,column = 0, sticky = W)
    #displayco3 = Label(frame, text = "", bg = "yellow")
    #displayco3.grid(row = 2,column = 0, sticky = W)
    #displayco.pack(side = BOTTOM, pady = 0)


    root.bind('<Escape>', quit)

    my_canvas.bind('<Button-1>', track)
    my_canvas.bind('<Button-1>', cursor.move)
    my_canvas.bind('<ButtonRelease-1>', cursor.release)
    my_canvas.bind('<Button-3>', cursor.deposit)
    #root.bind('<Return>', rec.deposit)

    # my_canvas.bind('<ButtonRelease-1>', rec.release)


if __name__ == "__main__":
    root = Tk()
    setup(root)
    root.mainloop()



#dev bind_root(root):

#dev bind_canvas(canvas):
"""my_canvas.create_rectangle(200, 100, 700, 600, fill="#B5F3FA", width = 0)
my_canvas.create_line(50, 100, 250, 200, fill="red", width=10)
for i in range(10):
    my_canvas.create_line(50 * i, 0, 50 * i, 400)
    my_canvas.create_line(0, 50 * i, 400, 50 * i) """
"""
img = PhotoImage(file = "C:/Users/Looi Kai Wen/Desktop/Spacey/gui experiment/dcspirte_back.png")
#my_image = my_canvas.create_image(50,50,anchor = NW, image = img)
my_box = my_canvas.create_rectangle(x, y, x+50, y+50,fill = "red", width = 1.0)
help(my_canvas.create_image)

def callback(t):
    my_box = my_canvas.create_rectangle(t.x, t.y, t.x+50, t.y+50,fill = "red", width = 1.0)

def move(e):
    global img
    #img = PhotoImage(file = "C:/Users/Looi Kai Wen/Desktop/Spacey/gui experiment/dcspirte_back.png")
    my_box = my_canvas.create_rectangle(e.x, e.y, e.x+50, e.y+50,fill = "red", width = 1.0)
    # my_image = my_canvas.create_image(e.x,e.y,image=img)
    my_label.config(text="Coordinates x: "+str(e.x)+ "y: "+str(e.y))

my_label = Label(root,text="")
my_label.pack(pady = 20)

my_canvas.bind('<B1-Motion>', move)
my_canvas.bind('<Button-1>', callback)
"""