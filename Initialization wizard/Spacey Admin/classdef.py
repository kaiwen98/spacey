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
from queue import Queue


class myCanvasObject(object):
    def __init__(self,frame, width, height):
        self.canvas = Canvas(frame, width = width, height = height)
        self.line_obj = []
        self.rec_obj = {}
        self.border_obj = []


class CanvasGridFrame(object):
    def __init__(self,canvas, num):
        self.xpos, self.ypos, self.xlen, self.ylen = 0, 0, 1500, 1500
        self.canvas = canvas
        self.deviceID = 0
        self.bg = canvas.create_rectangle(self.xpos, self.ypos, self.xpos + self.xlen, self.ypos+self.ylen, fill="SteelBlue1", width = 0)
        self.grid = self.createGrid(num)
      


    def createGrid(self,num):
        cfg.step = self.xlen / num
        cfg.x_list.clear()
        cfg.y_list.clear()
        for i in range(num+1):
            cfg.x_list.append(round(self.xpos+i*cfg.step))
            cfg.y_list.append(round(self.ypos+i*cfg.step))
            cfg.myCanvas.line_obj.append(self.canvas.create_line(self.xpos+i*cfg.step, self.ypos, self.xpos+i*cfg.step, self.ypos + self.ylen, fill = "sky blue", width = 5))
            cfg.myCanvas.line_obj.append(self.canvas.create_line(self.xpos, self.ypos+i*cfg.step, self.xpos+self.xlen, self.ypos+i*cfg.step, fill = "sky blue", width = 5))

 
        num_coordinates_max = (cfg.canvas_w/cfg.step-1) * (cfg.canvas_h/cfg.step-1)
   
        self.drawBoundary(cfg.step)
    
    def drawBoundary(self, step):
        x1 = cfg.x_list[0]
        x2 = cfg.x_list[1]
        _x1 = cfg.x_list[int(cfg.canvas_w/step)]
        _x2 = cfg.x_list[int(cfg.canvas_w/step)-5]

        y1 = cfg.y_list[0]
        y2 = cfg.y_list[1]
        _y1 = cfg.y_list[int(cfg.canvas_h/step)]
        _y2 = cfg.y_list[int(cfg.canvas_h/step)-5]
        cfg.myCanvas.border_obj.append(self.canvas.create_rectangle(x1,y1,_x1,y2, fill = "black"))        
        cfg.myCanvas.border_obj.append(self.canvas.create_rectangle(x1,_y2,_x1,_y1, fill = "black"))
        cfg.myCanvas.border_obj.append(self.canvas.create_rectangle(x1,y2,x2,_y2, fill = "black"))
        cfg.myCanvas.border_obj.append(self.canvas.create_rectangle(_x2,y2,_x1,_y2, fill = "black"))


    def refresh(self,_num):
        for x in cfg.myCanvas.line_obj:
            self.canvas.delete(x) 
        for y in cfg.myCanvas.line_obj:
            self.canvas.delete(y)
        self.grid = self.createGrid(_num)

class Node(object):
    def __init__(self, canvas, xpos, ypos):
        print("init")
        self.canvas = canvas
        self.xlen, self.ylen = 10, 10 #size of node
        cfg.node = canvas.create_rectangle(xpos, ypos,xpos+self.xlen, ypos+self.ylen, fill = "blue")
    

class CursorNode(object):
    def __init__(self, canvas, xpos, ypos):
        self.canvas = canvas
        self.xpos, self.ypos = xpos, ypos
        self.xlen, self.ylen = 10, 10 #size of node
        self.x_mid, self.y_mid = self.xpos + self.xlen/2, self.ypos + self.ylen/2
        self.obj= canvas.create_rectangle(xpos, ypos,xpos+self.xlen, ypos+self.ylen, fill = "red")

        canvas.tag_bind(self.obj, '<B1-Motion>', self.move)
        canvas.bind('<ButtonRelease-1>', self.release)
        canvas.bind('<Button-3>', self.deleteNode)

        canvas.bind('<Up>', lambda event: self.move_unit(event, 'W') )
        canvas.bind('<Left>', lambda event: self.move_unit(event, 'A') )
        canvas.bind('<Down>', lambda event: self.move_unit(event, 'S') )
        canvas.bind('<Right>', lambda event: self.move_unit(event, 'D') )
        canvas.bind('<ButtonRelease-1>', self.release)
        canvas.bind('<KeyRelease-Up>', self.release_unit)
        canvas.bind('<KeyRelease-Down>', self.release_unit)
        canvas.bind('<KeyRelease-Left>', self.release_unit)
        canvas.bind('<KeyRelease-Right>', self.release_unit)
        canvas.bind('<Return>', self.enter)
        canvas.bind('<Button-3>', self.deleteNode)
        canvas.bind('<Control-x>', self.deleteNode)


        self.restaurant = cfg.res
        self.move_flag = False
        self.callBack = []
    
    def deleteNode(self, event):
        if (self.x_mid, self.y_mid) in self.restaurant.dict_sensor_motes:
            print("deleted")
            self.callBack[0]("Node deleted.")
            self.restaurant.deleteNode(self.x_mid, self.y_mid)
            return
        else:
            print("Invalid")
            return

    
    def setCallback(self, cb):
        self.callBack.append(cb)
        
    def deposit(self):
        print("enter registered")
        if cfg.deposit_flag is True:
            node = Node(self.canvas, self.x_mid-self.xlen/2, self.y_mid - self.ylen/2)
            cfg.x = self.x_mid
            cfg.y = self.y_mid
            self.nodeDetectCallback()
            cfg.deposit_flag = False
        else:
            return
    

 
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

    def move_unit(self, event, dir):
        self.move_flag = True
        print("lol")
        if dir is "W":
            self.canvas.move(self.obj, 0 , -cfg.step)
            self.y_mid -= cfg.step
        elif dir is "A":
            self.canvas.move(self.obj, -cfg.step, 0)
            self.x_mid -= cfg.step
        elif dir is "S":
            self.canvas.move(self.obj, 0 , cfg.step)
            self.y_mid += cfg.step
        elif dir is "D":
            self.canvas.move(self.obj, cfg.step, 0)
            self.x_mid += cfg.step
        self.canvas.tag_raise(self.obj)

    def release(self, event):
        new_xpos, new_ypos = self.estimate(event.x,cfg.x_list), self.estimate(event.y,cfg.y_list)
        self.canvas.move(self.obj, new_xpos-self.x_mid ,new_ypos-self.y_mid)
        self.mouse_xpos = new_xpos
        self.mouse_ypos = new_ypos
        self.move_flag = False
        self.x_mid = new_xpos
        self.y_mid = new_ypos
        cfg.x = self.x_mid
        cfg.y = self.y_mid
        cfg.initflag = True
        self.nodeDetectCallback()
        self.canvas.tag_raise(self.obj)
        

    def release_unit(self, event):
        self.move_flag = False
        cfg.x = self.x_mid
        cfg.y = self.y_mid
        self.nodeDetectCallback()
        self.canvas.tag_raise(self.obj)
    
    def enter(self, event):
        cfg.initflag = True
        self.nodeDetectCallback()

        

    def nodeDetectCallback(self):

        if (self.x_mid, self.y_mid) in self.restaurant.dict_sensor_motes:
            text = self.restaurant.printMoteAt(self.x_mid, self.y_mid)
            self.callBack[1]("lawn green")
            self.callBack[0](text) # Print text on status label

        else:   
            cfg.deposit_flag = False
            self.callBack[0]("No node information") # Print text on status label
            self.callBack[1]("yellow")
            



            
            

        

class menu_upload(object):
    def __init__(self, frame):
        self.frame = frame
        self.labelFrame = LabelFrame(self.frame, text = "Upload: "+ str(cfg.filename), height = 150, width = 550, bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 20, padx = 10)
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
        self.labelFrame = LabelFrame(self.frame, text = "Upload: "+ str(cfg.filename), height = 150, width = 550, bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 20, padx = 10)
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
        cfg.res.deleteAllNodes()
        for j in cfg.myCanvas.border_obj:
            cfg.myCanvas.canvas.delete(j)
        refresh = self.map.refresh(self.num)
        self.cursor.canvas.tag_raise(self.cursor.obj)

    def updateDown(self):
        self.num -= 2
        if self.num <=0:
            return
        
        print("refresheddown")
        cfg.res.deleteAllNodes()
        for j in cfg.myCanvas.border_obj:
            cfg.myCanvas.canvas.delete(j)
        refresh = self.map.refresh(self.num)
        self.cursor.canvas.tag_raise(self.cursor.obj)
      
        

class menu_devinfo(object):
    def __init__(self, frame):
        self.frame = frame
        self.getFlag = False
        self.entryList = []
        self.callBack = []
        self.hold = []
        self.text = []
        for i in range(3):
            self.hold.append(IntVar())
            self.text.append(StringVar())
     

        self.labelFrame = LabelFrame(self.frame, text = "Set Sensor ID", height = 500, width = 550, bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 20, padx = 10)

        self.nodeEntry = [-1, -1, -1]
        self.prevEntry = [-1, -1, -1]

        self.idFlag = True

        self.frame1 = Frame(self.labelFrame,bg = "gray55")
        self.frame1.pack(side = TOP, fill = X, padx = 10, pady = 5)
        self.entry1_label = Label(self.frame1, text = "Level ID", bd = 5, width = 20)
        self.entry1_label.pack(side = LEFT)
        self.entryList.append(Entry(self.frame1, bd = 5, textvariable = self.text[0]))
        self.entryList[0].pack(side = LEFT)
        self.radio1 = Checkbutton(self.frame1, text = "Hold", variable = self.hold[0], command = partial(self.restoreprev, 0), bg = "gray55", )
        self.radio1.pack(side = LEFT)

        self.frame2 = Frame(self.labelFrame, bg = "gray55")
        self.frame2.pack(side = TOP, fill = X, padx = 10, pady = 5)
        self.entry2_label = Label(self.frame2, text = "Cluster ID", bd = 5, width = 20)
        self.entry2_label.pack(side = LEFT)
        self.entryList.append(Entry(self.frame2, bd = 5, textvariable = self.text[1]))
        self.entryList[1].pack(side = LEFT)
        self.radio2 = Checkbutton(self.frame2, text = "Hold", variable = self.hold[1], command = partial(self.restoreprev, 1), bg = "gray55")
        self.radio2.pack(side = LEFT)

        self.frame3 = Frame(self.labelFrame, bg = "gray55")
        self.frame3.pack(side = TOP, fill = X, padx = 10, pady = 5)
        self.entry3_label = Label(self.frame3, text = "Sensor ID", bd = 5, width = 20)
        self.entry3_label.pack(side = LEFT)
        self.entryList.append(Entry(self.frame3, bd = 5, textvariable = self.text[2]))
        self.entryList[2].pack(side = LEFT)
        self.radio3 = Checkbutton(self.frame3, text = "Hold", variable = self.hold[2], command = partial(self.restoreprev, 2), bg = "gray55")
        self.radio3.pack(side = LEFT)

        self.entryList[0].bind('<Return>', lambda event : self.enter(event, 0))
        self.entryList[1].bind('<Return>', lambda event : self.enter(event, 1))
        self.entryList[2].bind('<Return>', lambda event : self.enter(event, 2))
        for i in range(10):
            self.entryList[0].bind(str(i), lambda event : self.enter(event, 0))
            self.entryList[1].bind(str(i), lambda event : self.enter(event, 1))
            self.entryList[2].bind(str(i), lambda event : self.enter(event, 2))
        
        self.keyEntry = None
        self.needCorrect = [False, False, False]
    
    def restoreprev(self, i):
        if self.hold[i].get():
            if self.entryList[i].get() is "":
                self.text[i].set(self.prevEntry[i])
            else:
                self.text[i].set(self.entryList[i].get())
            self.entryList[i].config(state = DISABLED, disabledbackground= "sky blue")
        else:
            self.text[i].set("")
            self.entryList[i].config(state = NORMAL)

    def setCallback(self, cb):
        self.callBack.append(cb)

    def highlight_dev_info(self, _bg):
        print("highlight: " + str(_bg))
        for i in self.entryList:
            i.config(bg = _bg)
        self.keyEntry = self.entryList[0]
        if cfg.initflag: 
            self.keyEntry.focus()
            cfg.initflag = False
   
    def enter(self, event, id):
        for i in range(len(self.entryList)):
            if (self.entryList[i].get()).isnumeric():
                if int(self.entryList[i].get()) >=0:
                    print("-2")
                    self.nodeEntry[i] = int(self.entryList[i].get())
                    self.prevEntry[i] = self.nodeEntry[i]
                    self.entryList[i].config(bg = "lawn green")
                    self.needCorrect[i] = False
                else:
                    self.entryList[i].config(bg = "red")
                    self.needCorrect[i] = True

            else:
                print("-3")
                self.entryList[i].config(bg = "red")
                self.needCorrect[i] = True
        
        sum = 0
        for i in self.needCorrect:
            sum += i 

        if sum: 
            print(self.needCorrect)
            self.keyEntry = self.entryList[self.needCorrect.index(True)]
            self.keyEntry.focus()
            return

        
        print(self.nodeEntry)

        for i in range(len(self.entryList)):
            if not self.hold[i].get():
                self.entryList[i].delete(0, END)

        x = self.nodeEntry
        
        cfg.deposit_flag = True
        self.callBack[0]()
        cfg.res.registerNode(cfg.x, cfg.y, x[0], x[1], x[2], cfg.node)
        cfg.res.printMoteAt(cfg.x, cfg.y)
        self.nodeEntry = [-1,-1,-1]
        self.callBack[1]()  # Callback to deposit sensor node
        self.callBack[2](1) # Callback to give up focus back to canvas

class menu_status(object):
    def __init__(self, frame):
        self.frame = frame
        #self.frame = Frame(frame, bg = "red")
        #self.frame.grid(row = 1, column = 0, sticky = E+W)
        self.labelFrame = LabelFrame(self.frame, text = "Status bar", bg = "gray55", height = 300, width = 550)
        #self.labelFrame.pack(side = TOP, pady = 40, padx = 10)
        self.labelFrame.pack(fill = X, padx = 10, pady = 20, side = TOP)
        self.labelFrame.pack_propagate(0)
        self.obj = Label(self.labelFrame,text = "", bd = 100, height = 300, width = 550)
        self.obj.pack(padx = 10, pady = 10)
    def updateText(self, _text):
        self.obj.configure(text = _text)
        self.obj.update()

