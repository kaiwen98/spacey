################################################# Redis Database interface #################################################
# Author: Looi Kai Wen                                                                                                     #
# Last edited: 11/07/2020                                                                                                  #
# Summary:                                                                                                                 #
#   Currently using a free-to-use remote Redis database with max capacity of 30 MB. Includes methods to store and pose     #
#   query to the database.                                                                                                 #
############################################################################################################################

# The following is stored in the database:
# registered_users [set]
#   eg. Macdonalds Inc.
# registered restaurants [list]
#   eg. Woodlands branch
# users_private_key [hash]
#   inf. Ciphertext from SHA256 such that password of the user cannot be leaked from database
# Restaurant data [hash]
#   -occupancy
#   -config


import redis
import json
import os
from os.path import dirname as dir, realpath, join, splitext, basename
import sys
import base64
import multiprocessing
import time
from redis.exceptions import TimeoutError
# File directory
root = dir(dir(realpath(__file__)))

# get session name


class redis_database(object):
    def __init__(self, root,remote_host, port, password):
        self.remote_host = remote_host
        self.port = port
        self.password = password
        self.root = root
        self.client = None
        self.res_list = []
        self.test = 3
        self.user = ""
    
    def timeout(self):      
        self.client = redis.Redis(host = self.remote_host, port = self.port, db = 0, password = self.password, decode_responses= True, socket_timeout= 10)

    
    def login_user(self, name, key):
        try: 
            self.client.keys()
        except TimeoutError as err:
            return 2

        if self.client.sismember("registered_users", name) is False: 
            print(self.client.sismember("registered_users", name))
            return 0
        authenticate = self.client.hget("users_private_key", name)
        if str(authenticate) == str(key):
            print("yup")
            print("auth: ",str(authenticate))
            print("key: ",str(key))
            self.user = name
            return 1
        else:
            print("auth: ",str(authenticate))
            print("key: ",str(key))
            
            return 0

    def register_user(self, name, key):
        # if username exists, cannot register
        if self.client.sismember("registered_users", name): return False
        self.client.sadd("registered_users", name)
        self.client.hset("users_private_key", name, key)
        self.user = name
        return True


    def beginConnection(self):
        self.client = redis.Redis(host = self.remote_host, port = self.port, db = 0, password = self.password, decode_responses= True)
        return self.get_registered_restaurants()
        

    def getbasename(self, path):
        return splitext(basename(path))[0]
    
    def get_registered_restaurants(self):
        if len(self.res_list): self.res_list.clear()
        for i in range(0, self.client.llen("{}_registered_restaurants".format(self.user))):
            self.res_list.append(self.client.lindex("{}_registered_restaurants".format(self.user), i))
        #if not len(self.res_list): self.res_list.append("No restaurants stored")
        return self.res_list

    def clearDB(self, session_name):
        if session_name not in self.client.lrange(self.user + "_registered_restaurants", 0, -1): return "Invalid input! Restaurant is not yet registered with your account..."
        session_name = "NUS_" + session_name
        for i in ["_coord", "_config", "_hash", "_occupancy", "res_info"]:
            name = str(session_name) + i
            self.client.delete(name)
        print("name: ", name)
        name = session_name.split('_')[1]
        print("here:", name)
        if not self.client.lrem("{}_registered_restaurants".format(self.user), 1, name):
            return "Restaurant do not exist in database"
        else:
            return "Deleted "+ str(session_name)
       
        
        self.client.lrem("{}_registered_restaurants".format(self.user), 1, name)

    def clearUser(self, user):
        while self.client.llen("{}_registered_restaurants".format(user)):
            self.clearDB(self.user + '_' + self.client.lpop("{}_registered_restaurants".format(user)))
    
        self.client.srem("registered_users", user)
        self.client.hdel("users_private_key",user)


    # set relevant file directories pointing to the json files
    def configJsonDir(self, mode = 'client'):
        json_folder = join(self.root, 'json_files')
        json_file_config = join(json_folder, 'config')
        json_file_occupancy = join(json_folder, 'occupancy')
        json_file_hash = join(json_folder, 'hash')
        json_file_coord = join(json_folder, 'coord')
  
        return [json_file_config, json_file_occupancy, json_file_hash, json_file_coord]

    def setResInfo(self, name, res_info):
        full_name = name + "_"+"res_info"
        self.client.hmset(full_name, res_info)
        return True
    
    def getResInfo(self, name):
        full_name = name + "_"+"res_info"
        if len(self.client.hgetall(full_name)) == 0:
            print("here from DB")
            null_dict = {}
            res_info_op = ["res_lat", "res_lng", "res_addr", "res_occup_hr"]
            for i in res_info_op:
                null_dict[i] = "-"

            self.client.hmset(full_name,null_dict)
        return self.client.hgetall(full_name)

    # connects to remote database and stores json information there
    def exportToDB(self, session_name, import_from_script = None, reset = True):

        res_name = (session_name.split('_'))[1]
        print(res_name)
        if res_name in self.get_registered_restaurants() and reset == True: 
            self.clearDB(session_name)
            print("Cleared duplicate")
            print(self.client.keys())

        json_list = self.configJsonDir()
        # Each restaurant will have 4 json files associated with it. 
        # Iterate over every instance and store into database.
        for i in json_list:
            data = {}
            name = session_name + "_" + self.getbasename(i)
    
            if import_from_script is None:
                path = os.path.join(i, session_name+".json")
                with open(path,"r") as infile:
                    data = json.load(infile)
            else:
                data = import_from_script[json_list.index(i)]
                
            self.client.hmset(name, data)
            res_name = session_name.split('_')[1]
        self.client.lpush('{}_registered_restaurants'.format(self.user), res_name)
  

    # extracts information from database
    # export_to_local -> list passed as arg, export directly to script without referencing any files on hard drive
    def importFromDB(self, session_name, export_to_script = None, mode = 'client'):
        json_list = self.configJsonDir()
        export_limit = 0
        if export_to_script is not None: export_limit = len(export_to_script)
        for i in json_list:
            data = {}
            name = session_name + "_" + self.getbasename(i)
            print(name)
            data = self.client.hgetall(name)
            if export_to_script is None:
                path = os.path.join(i, session_name+".json")
                with open(path, "w") as outfile:
                    json.dump(data, outfile)
            else: 
          
                export_to_script[json_list.index(i)] = data
                export_limit -= 1
                if not export_limit: return export_to_script

if __name__ == "__main__":
    remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
    password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
    port = '13969'
    """
    remote_host = 'localhost'
    password = None
    port = '6379'
    """

    r = redis_database(root,remote_host, port, password)
    r.timeout()
    r.user = 'NUS'
    #r.clearUser('Macdonalds')
    #print(r.clearDB('NUSKFC'))
    print(r.client.lrange("NUS_registered_restaurants", 0,-1))
    print(r.client.keys())
    print(r.client.hgetall('users_private_key'))
    print(r.client.smembers('registered_users'))
    print(r.get_registered_restaurants())
    print(r.client.hgetall('NUS_Macdonalds_hash'))
    #r.client.delete('NEWTEST1', 'NEWTEST', 'fool')
    print(r.client.hgetall('NUS_Macdonalds_occupancy'))
    #print(r.client.lrange("NUS" + "_registered_restaurants", 0, -1))
    print(r.client.hgetall('NUS_KFC_coord'))
    # Life Hax
    #r.client.hmset('users_private_key',{'NUS': 'ec9193f8f25777fc0dbd511fdd617feee807ca9c4de6b51045b9cf98c535bcac'})
    #r.client.flushdb()
    #print(r.client.smembers('registered_users'))
    
    #r.client.delete("NUSSpacey_res_info")