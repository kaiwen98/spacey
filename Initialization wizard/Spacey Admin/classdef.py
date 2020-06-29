################################################# SPACEY Initiation GUI Wizard #############################################
# Author: Looi Kai Wen                                                                                                     #
# Last edited: 28/06/2020                                                                                                  #
# Summary:                                                                                                                 #
#   For use by BLE network administrators to configure their database with invariant information,                          #
#   eg. relative coordinates of the sensor mote, cluster level, etc.                                                       #
#   
############################################################################################################################

from tkinter import * 
import tkinter as tk
from tkinter import filedialog
import config as cfg
from sensor_data import *
from functools import partial



class CanvasGridFrame(object):
    def __init__(self,canvas, num):
        self.xpos, self.ypos, self.xlen, self.ylen = 0, 0, 1500, 1500
        self.canvas = canvas
        self.deviceID = 0
        self.bg = canvas.create_rectangle(self.xpos, self.ypos, self.xpos + self.xlen, self.ypos+self.ylen, fill="SteelBlue1", width = 0)
        self.grid = self.createGrid(num)
      


    def createGrid(self,num):
        step = self.xlen / num
        cfg.x_list.clear()
        cfg.y_list.clear()
        for i in range(num+1):
            cfg.x_list.append(round(self.xpos+i*step))
            cfg.y_list.append(round(self.ypos+i*step))
            cfg.canvas_line_obj.append(self.canvas.create_line(self.xpos+i*step, self.ypos, self.xpos+i*step, self.ypos + self.ylen, fill = "sky blue", width = 5))
            cfg.canvas_line_obj.append(self.canvas.create_line(self.xpos, self.ypos+i*step, self.xpos+self.xlen, self.ypos+i*step, fill = "sky blue", width = 5))

 
        num_coordinates_max = (cfg.canvas_w/step-1) * (cfg.canvas_h/step-1)
   
        self.drawBoundary(step)
    
    def drawBoundary(self, step):
        x1 = cfg.x_list[0]
        x2 = cfg.x_list[1]
        _x1 = cfg.x_list[int(cfg.canvas_w/step)]
        _x2 = cfg.x_list[int(cfg.canvas_w/step)-5]

        y1 = cfg.y_list[0]
        y2 = cfg.y_list[1]
        _y1 = cfg.y_list[int(cfg.canvas_h/step)]
        _y2 = cfg.y_list[int(cfg.canvas_h/step)-5]
        cfg.canvas_rec_obj.append(self.canvas.create_rectangle(x1,y1,_x1,y2, fill = "black"))        
        cfg.canvas_rec_obj.append(self.canvas.create_rectangle(x1,_y2,_x1,_y1, fill = "black"))
        cfg.canvas_rec_obj.append(self.canvas.create_rectangle(x1,y2,x2,_y2, fill = "black"))
        cfg.canvas_rec_obj.append(self.canvas.create_rectangle(_x2,y2,_x1,_y2, fill = "black"))


    def refresh(self,_num):
        for x in cfg.canvas_line_obj:
            self.canvas.delete(x) 
        for y in cfg.canvas_line_obj:
            self.canvas.delete(y)
        self.grid = self.createGrid(_num)

class Node(object):
    def __init__(self, canvas, xpos, ypos):
        print("init")
        self.canvas = canvas
        self.xlen, self.ylen = 10, 10 #size of node
        self.obj = canvas.create_rectangle(xpos, ypos,xpos+self.xlen, ypos+self.ylen, fill = "blue")
        cfg.canvas_rec_obj.append(self.obj)
    

class CursorNode(object):
    def __init__(self, canvas, xpos, ypos, restaurant):
        self.canvas = canvas
        self.nodeCount = 0
        self.xpos, self.ypos = xpos, ypos
        self.xlen, self.ylen = 10, 10 #size of node
        self.x_mid, self.y_mid = self.xpos + self.xlen/2, self.ypos + self.ylen/2
        self.obj= canvas.create_rectangle(xpos, ypos,xpos+self.xlen, ypos+self.ylen, fill = "red")
        canvas.tag_bind(self.obj, '<B1-Motion>', self.move)
        canvas.tag_bind(self.obj, '<ButtonRelease-1>', self.release)
        canvas.tag_bind(self.obj, '<Button-3>', self.deposit)
        self.restaurant = restaurant
        self.move_flag = False
    
    def setCallback(self, cb):
        self.callBack = cb
        



    def deposit(self, event):
        print("enter registered")
        self.nodeCount += 1
        node = Node(self.canvas, self.x_mid-self.xlen/2, self.y_mid - self.ylen/2)
        self.restaurant.registerNode(self.x_mid, self.y_mid, 1,1,1,node)
        self.restaurant.printMoteAt(self.x_mid, self.y_mid)
        self.nodeDetectCallback()
    

 
    def estimate(self,x,_list):

        mid = round(len(_list)/2)
        if len(_list) is 1:
            return _list[0]
        elif len(_list) is 2:
            if abs(_list[0] - x) > abs(_list[1] - x):
                return _list[1]
            else:
                return _list[0] 
        else:
            if x > _list[mid]:
                x = x+1
                return self.estimate(x,_list[mid:])
            elif x < _list[mid]:
                x = x-1
                return self.estimate(x,_list[:mid])
            else:
                return x

    def move(self, event):
        if self.move_flag:
            new_xpos, new_ypos = event.x, event.y
            self.canvas.move(self.obj, new_xpos-self.mouse_xpos ,new_ypos-self.mouse_ypos)
            self.x_mid += new_xpos-self.mouse_xpos
            self.y_mid += new_ypos-self.mouse_ypos
            self.mouse_xpos = new_xpos
            self.mouse_ypos = new_ypos
        else:
            self.move_flag = True
            self.canvas.tag_raise(self.obj)
            self.mouse_xpos = event.x
            self.mouse_ypos = event.y

    def release(self, event):
        new_xpos, new_ypos = self.estimate(event.x,cfg.x_list), self.estimate(event.y,cfg.y_list)
        self.canvas.move(self.obj, new_xpos-self.x_mid ,new_ypos-self.y_mid)
        self.mouse_xpos = new_xpos
        self.mouse_ypos = new_ypos
        self.move_flag = False
        self.x_mid = new_xpos
        self.y_mid = new_ypos
        self.nodeDetectCallback()

    def nodeDetectCallback(self):
        if (self.x_mid, self.y_mid) in self.restaurant.dict_sensor_motes:
            text = self.restaurant.printMoteAt(self.x_mid, self.y_mid)
            self.callBack(text)
        else:
            return

        

class menu_upload(object):
    def __init__(self, frame):
        self.frame = frame
        #self.frame = Frame(frame)
        #self.frame.grid(row = 0, column = 0, sticky = E+W)
        self.labelFrame = LabelFrame(self.frame, text = "Upload: "+ str(cfg.filename), padx = 20, pady = 20, bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 40, padx = 10)
        self.obj = Button(self.labelFrame, text = "Upload", command = self.fileupload)
        self.obj.pack(ipadx = 10, ipady = 10)

    def fileupload(self):
        filename = filedialog.askopenfilename(initialdir = "/", title = "Select File", filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        self.label = Label(self.labelFrame, text = "Uploaded: "+ str(filename))
        self.label.pack(fill = X)

class map_refresh(object):
    def __init__(self, frame, canvasGridFrame, newGrid, cursor):
        self.frame = frame
        #self.frame = Frame(frame)
        #self.frame.grid(row = 0, column = 0, sticky = E+W)
        self.labelFrame = LabelFrame(self.frame, text = "Upload: "+ str(cfg.filename), padx = 20, pady = 20, bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 40, padx = 10)
        self.num = newGrid
        self.map = canvasGridFrame
        self.but1 = Button(self.labelFrame, text = "Scale up", command = self.updateUp)
        self.but1.pack(ipadx = 10, ipady = 10, fill = X)
        self.but2 = Button(self.labelFrame, text = "Scale down", command = self.updateDown)
        self.but2.pack(ipadx = 10, ipady = 10, fill = X)
        self.cursor = cursor

        


    def updateUp(self):
        self.num += 2
        
        print("refreshedup")
        for i in cfg.canvas_rec_obj:
            self.map.canvas.delete(i)
        refresh = self.map.refresh(self.num)
        #self.cursor = CursorNode(self.map.canvas,xpos = 513,ypos = 392)

    def updateDown(self):
        self.num -= 2
        if self.num <=0:
            return
        
        print("refresheddown")
        for i in cfg.canvas_rec_obj:
            self.map.canvas.delete(i)
        refresh = self.map.refresh(self.num)
        #self.cursor = CursorNode(self.map.canvas,xpos = 513,ypos = 392)
      
        

class menu_devinfo(object):
    def __init__(self, frame):
        self.frame = frame
        #self.frame = Frame(frame, bg = "red")
        #self.frame.grid(row = 1, column = 0, sticky = E+W)
        self.labelFrame = LabelFrame(self.frame, text = "Set Sensor ID", padx = 20, pady = 20, bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 40, padx = 10)

        self.idFlag = True
        self.entry = Entry(self.labelFrame, bd = 5)
        self.entry.grid(row = 1)
        self.devUpdate = [0 for i in range(100)]
        self.devUpdateID = 3
        self.entry.bind('<Return>', self.enter)

    def idEntry(self):
        if self.idFlag is True:
            self.obj = Label(self.labelFrame,text = "Please select device...")
            self.obj.grid(row = 2)


    def enter(self, event):
        print("Yup")
        if self.entry.get().isnumeric() is True: 
            self.devUpdate[self.devUpdateID] = int(self.entry.get())

        self.entry.delete(0, 100)

class menu_status(object):
    def __init__(self, frame):
        self.frame = frame
        #self.frame = Frame(frame, bg = "red")
        #self.frame.grid(row = 1, column = 0, sticky = E+W)
        self.labelFrame = LabelFrame(self.frame, text = "Status bar", bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 40, padx = 10)
        self.obj = Label(self.labelFrame,text = "Update complete: ID: 02 Cluster: 02 Seat: 245", bd = 100)
        self.obj.grid(stick ="")
    def updateText(self, _text):
        self.obj.configure(text = _text)
        self.obj.update()

