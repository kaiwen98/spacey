import p_config as cfg
import json

class RestaurantSpace(object):
    def __init__(self):
        self.idxList = []
        self.x_coord = {}
        self.y_coord = {}
        self.space_id = {}
        self.device_cluster_level = {}
        self.device_cluster_id = {}
        self.size = 0
        self.dict_sensor_motes = {}
        self.devinfo = ["x_coord", "y_coord", "space_id", "device_cluster_level", "device_cluster_id", "idxList"]
        self.occupied = {}
    def unpackFromJson(self):
        for idx in self.idxList:
            self.size += 1

        print(self.x_coord)

        for i in self.idxList:
            if int(i)%2: self.occupied[i] = True
            else       : self.occupied[i] = False
            
            self.x_coord[i] = self.x_coord[i] - (cfg.x_bb1 + cfg.box_len)
            self.y_coord[i] = self.y_coord[i] - (cfg.y_bb1 + cfg.box_len)

        print(self.x_coord)
        