################################################# SPACEY Initiation GUI Wizard #############################################
# Author: Looi Kai Wen                                                                                                     #
# Last edited: 11/07/2020                                                                                                  #
# Summary:                                                                                                                 #
#   For use by BLE network administrators to configure their database with invariant information,                          #
#   eg. relative coordinates of the sensor mote, cluster level, etc.                                                       #
############################################################################################################################



import config as cfg
from imagegen import *
import os
from os.path import dirname as dir, splitext, basename, join, abspath
import sys
import base64
import res_info as res
import random
import time
import redis


# Need to choose depending on running from exe or py. Should point to /Server
# root = dir(dir(dir(sys.executable)))
_root = dir(dir(abspath(__file__)))
# print(_root)

# To extract database interface functions
sys.path.append(join(_root, "Redis"))
import redisDB
# Relevant file directories

# Image Assets
image_folder = os.path.join(_root, "images")
image_asset_folder = os.path.join(image_folder, "assets")
image_output_graphic_folder = os.path.join(image_folder, "output graphic")
nodeOn_path = os.path.join(image_asset_folder, "unoccupied_nodes.png")
nodeOff_path = os.path.join(image_asset_folder, "occupied_nodes.png")


# Database information

remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
port = '13969'
"""
remote_host = 'localhost'
password = None
port = '6379'
"""


available_restaurants_name = None
nodeOn = None
nodeOff = None
restaurants = None
cfg.database = redisDB.redis_database(
    _root, cfg.remote_host, cfg.port, cfg.password)
interrupt = ""

# Serializes image from png to string


def json_serialize_image(image_file):
    with open(image_file, mode='rb') as file:
        img = file.read()
    # picture to bytes, then to string
    return base64.b64encode(img).decode("utf-8")

# Deserializes image from string to png, then save it in the specified file directory


def json_deserialize_image(encoded_str, image_file):
    result = encoded_str.encode("utf-8")
    result = base64.b64decode(result)
    # create a writable image and write the decoding result
    image_result = open(image_file, 'wb')
    image_result.write(result)
    # Return filename of the new output graphic


def get_output_graphic_path(name):
    result = os.path.join(image_output_graphic_folder, "output_"+name+".png")
    return result


class ResServer(object):
    def __init__(self, userID):
        self.userID = userID
        self.available_restaurants_name = cfg.database.get_all_restaurant_from_user(
            userID)
        self.restaurants = {}
        self.remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
        self.port = '13969'
        self.password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'

        for i in self.available_restaurants_name:
            occupancy = {}
            coord = {}

            full_name = self.userID + "_" + i
            full_name_occupancy = full_name + "_occupancy"
            full_name_coord = full_name + "_coord"
            occupancy = cfg.database.client.hgetall(full_name_occupancy)
            coord = cfg.database.client.hgetall(full_name_coord)
            cfg.json_deserialize_image(
                coord["processed_img"], cfg.get_output_graphic_path(full_name))
            self.box_len = int(coord["box_len"])
            del coord["processed_img"]
            del coord["box_len"]
            

            # self.restaurants.append(res.restaurant_info(
            #     full_name, occupancy, coord, cfg.get_output_graphic_path(full_name), self.box_len))
            self.restaurants[i] = res.restaurant_info(full_name, occupancy, coord, cfg.get_output_graphic_path(full_name), self.box_len)
            

    def scan_update(self):
        """
        print(self.userID)
        """

        client = redis.Redis(host=self.remote_host, port=self.port,
                             db=0, password=self.password, decode_responses=True)
            
        for i in range(len(self.available_restaurants_name)):
            
            occupancy = {}
            full_name = self.userID + "_" + self.available_restaurants_name[i]
            full_name_occupancy = full_name + "_occupancy"

            # occupancy = cfg.database.client.hgetall(full_name_occupancy)
            occupancy = client.hgetall(full_name_occupancy)
            if self.restaurants[i].occupancy != occupancy:
                imageupdate(self.restaurants[i], occupancy)
            # You can change update frequency from here. The scan is asynchronous
    def get_info(self):    
        client = redis.Redis(host=self.remote_host, port=self.port,
                             db=0, password=self.password, decode_responses=True)        
        return self.restaurants
 


    def randomize(self):
    
        # print("hi")
        for i in range(len(self.available_restaurants_name)):
            # print(self.available_restaurants_name[i])
            occupancy = {}
            new_occupancy = {}
            full_name = self.userID + "_" + self.available_restaurants_name[i]
            full_name_occupancy = full_name + "_occupancy"

            occupancy = cfg.database.client.hgetall(full_name_occupancy)
            for i in occupancy.keys():
                new_occupancy[i] = random.randint(0, 1)

            cfg.database.client.hmset(full_name_occupancy, new_occupancy)



def main():
    userID = 'NUS'
    cfg.database.timeout()
    x = ResServer(userID)
    
  
if __name__ == '__main__':
    main()

  


