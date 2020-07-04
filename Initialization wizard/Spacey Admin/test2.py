from tkinter import *  
from PIL import ImageTk as p_ImageTk, Image as p_Image
import os
import config as cfg
import classdef as spc
from sensor_data import *
path = os.path.dirname(os.getcwd())

scaleNum = 50

image_path = os.path.join(path, "images")
print(image_path)

image_file = os.path.join(image_path, "image_edited.png")

"""
canvas = Canvas(root, width = 1200, height = 1200)  
canvas.pack()  
img = ImageTk.PhotoImage(Image.open(image_file))  
canvas.create_image(0, 0, anchor=NW, image=img) 
root.mainloop() 
"""

def setup():
    root = Tk()
    root.state('zoomed') 
    root.title('Title') 
    root.configure(bg = "gray22") 


    cfg.canvas_w, cfg.canvas_h = 1200, 1000
    w, h = 1200, 1000
    print("from main: " + str(cfg.canvas_w))
    frame_canvas = LabelFrame(root, text = "Map", width = w, height = h, bg = "gray40") # Set frame to embed canvas
    frame_canvas.pack(padx = 20, pady = 20, side = RIGHT) # Align right with padding
    frame_canvas.pack_propagate(False) # Fix frame size to dimensions


    cfg.myCanvas = spc.myCanvasObject(frame_canvas, width = w, height = h) # Set canvas within frame
    #cfg.myCanvas.canvas.pack(fill = "both", expand = 1, padx = 10, pady = 10) # Set padding
    cfg.myCanvas.canvas.pack()


    cfg.res = RestaurantSpace(cfg.myCanvas.canvas)

    grid = spc.CanvasGridFrame(cfg.myCanvas.canvas, scaleNum) # Creates gridlines so that the boxes inserted will appear more organised
    
    img = p_Image.open(image_file)

    width_r = cfg.canvas_w-100
    factor = width_r / float(img.size[0])
    height_r = int((float(img.size[1])) * float(factor))
    print(factor)

    img = img.resize((width_r, height_r), p_Image.ANTIALIAS)


    imga = p_ImageTk.PhotoImage(img)
    
    
    cfg.myCanvas.canvas.create_image((600,500), anchor = "center", image = imga)
    cursor = spc.CursorNode(cfg.myCanvas.canvas , xpos = 513 , ypos = 392)
    root.mainloop()





if __name__ == "__main__":
    
    setup()
    