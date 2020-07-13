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
        p = multiprocessing.Process(target = self.beginConnection)
        p.start()
        p.join(10)
        if p.is_alive(): 
            p.terminate()
            p.join()
            return False
        
        self.client = redis.Redis(host = self.remote_host, port = self.port, db = 0, password = self.password, decode_responses= True)
    
    def login_user(self, name, key):
        if self.client.sismember("registered_users", name) is False: 
            print(self.client.sismember("registered_users", name))
            return False
        authenticate = self.client.hget("users_private_key", name)
        if str(authenticate) == str(key):
            print("yup")
            print("auth: ",str(authenticate))
            print("key: ",str(key))
            self.user = name
            return True
        else:
            print("auth: ",str(authenticate))
            print("key: ",str(key))
            
            return False

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
        self.res_list.clear()
        for i in range(0, self.client.llen("{}_registered_restaurants".format(self.user))):
            self.res_list.append(self.client.lindex("{}_registered_restaurants".format(self.user), i))
        #if not len(self.res_list): self.res_list.append("No restaurants stored")
        return self.res_list

    def clearDB(self, session_name):
        session_name = self.user + "_" + session_name
        for i in ["_coord", "_config", "_hash", "_occupancy"]:
            name = str(session_name) + i
            self.client.delete(name)

        if not self.client.lrem("registered_restaurants", 1, session_name):
            return "Restaurant do not exist in database"
        else:
            return "Deleted "+ str(session_name)
        
        self.client.lrem("registered_restaurants", 1,session_name)

    def clearUser(self, user):
        while self.client.llen("{}_registered_restaurants".format(user)):
            self.clearDB(self.client.lpop("{}_registered_restaurants".format(user)))
    
        self.client.srem("registered_users", user)
        self.client.hdel("users_private_key",user)


    # set relevant file directories pointing to the json files
    def configJsonDir(self):
        json_folder = join(self.root, 'json_files')
        json_file_config = join(json_folder, 'config')
        json_file_occupancy = join(json_folder, 'occupancy')
        json_file_hash = join(json_folder, 'hash')
        json_file_coord = join(json_folder, 'coord')
        return [json_file_config, json_file_occupancy, json_file_hash, json_file_coord]

    # connects to remote database and stores json information there
    def exportToDB(self, res_name, import_from_script = None, reset = True):
        
        if res_name in self.get_registered_restaurants() and reset == True: 
            self.clearDB(res_name)

        session_name = self.user + "_" + res_name
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
        self.client.lpush('{}_registered_restaurants'.format(self.user), res_name)
  

    # extracts information from database
    # export_to_local -> list passed as arg, export directly to script without referencing any files on hard drive
    def importFromDB(self, res_name, export_to_script = None):
        session_name = self.user + "_" + res_name
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
                print(data)
                export_to_script[json_list.index(i)] = data
                export_limit -= 1
                if not export_limit: return export_to_script

    def get_all_restaurant_from_user(self,user):
        self.user = user
        attr_name = user + "_registered_restaurants"
        print(attr_name)
        len_res = self.client.llen(attr_name)-1
        return self.client.lrange(attr_name, 0, len_res)



if __name__ == "__main__":
    #remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
    #password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
    password = None
    #port = '13969'
    remote_host = 'localhost'
    port = '6379'
    #port = '3'
    r = redis_database(root,remote_host, port, password)
    r.timeout()
    
    r.user = 'NUS'
    #r.clearUser('Macdonalds')
    print(r.client.lindex("Macdonalds_registered_restaurants", 0))
    print(r.client.keys())
    print(r.client.hgetall('users_private_key'))
    print(r.client.smembers('registered_users'))
    print(r.get_registered_restaurants())
    print(r.get_all_restaurant_from_user('NUS'))
    #r.client.flushdb()
    #print(r.client.smembers('registered_users'))

