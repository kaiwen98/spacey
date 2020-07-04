from tkinter import *
import classdef as spc
from tkinter import filedialog
import config as cfg
from sensor_data import *
from functools import partial
from queue import Queue

from PIL import Image as p_Image, ImageEnhance as p_ImageEnhance, ImageOps as p_ImageOp, ImageTk as p_ImageTk
import os

class floorPlan(object):
    def __init__(self, path, canvas):
        self.canvas = canvas
        self.path = path
        cfg.imgpath = path
        self.img = self.preprocess()
        self.padding = 0
        self.resize()
        self.x_mid = int(cfg.x_bb1 + (cfg.x_bb2 - cfg.x_bb1)/2)
        self.y_mid = int(cfg.y_bb1 + (cfg.y_bb2 - cfg.y_bb1)/2)
        


    def preprocess(self):
        img = p_Image.open(self.path)
        img = img.convert("RGBA")
        enhancer = p_ImageEnhance.Contrast(img)
        img = enhancer.enhance(10)
        enhancer = p_ImageEnhance.Sharpness(img)
        img = enhancer.enhance(10)
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] < 5 and item[1] < 5 and item[2] < 5 and item[3] != 0:
                newData.append((0,0,0,255))
            else:
                newData.append((255, 255, 255, 0))
        img.putdata(newData)
        return img

    def resize(self):
        print("length = " + str(cfg.x_bb2 - cfg.x_bb1))
        print("x_bb1 = " + str(cfg.x_bb1))
        print("y_bb1 = " + str(cfg.y_bb1))

        if cfg.myCanvas.floorplan_obj is not None: self.canvas.delete(cfg.myCanvas.floorplan_obj)

        self.x_mid = int(cfg.x_bb1 + (cfg.x_bb2 - cfg.x_bb1)/2)
        self.y_mid = int(cfg.y_bb1 + (cfg.y_bb2 - cfg.y_bb1)/2)
        width_r = cfg.x_bb2 - cfg.x_bb1 - self.padding
        height_r = cfg.y_bb2 - cfg.y_bb1 - self.padding

        factor_w = width_r / float(self.img.size[0])
        factor_h = height_r / float(self.img.size[1])
        if factor_w > factor_h: factor = factor_h
        else                  : factor = factor_w
        height_r = int((float(self.img.size[1])) * float(factor))
        self.img = self.img.resize((width_r, height_r), p_Image.ANTIALIAS)

        path = os.path.dirname(self.path)
        cfg.imgpath = os.path.join(path, "processed_img.png")
        self.img.save(cfg.imgpath, "PNG")
        self.photoimg = p_ImageTk.PhotoImage(self.img)
        #cfg.myCanvas.floorplan_obj = self.canvas.create_image(self.x_mid,self.y_mid, anchor = "center", image = self.photoimg)
        cfg.myCanvas.floorplan_obj = self.canvas.create_image(cfg.x_bb1,cfg.y_bb1, anchor = "nw", image = self.photoimg)
        for i in cfg.myCanvas.rec_obj:
            cfg.myCanvas.canvas.tag_raise(i)

    