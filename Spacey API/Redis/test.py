import redis
import json
import os
from os.path import dirname as dir, realpath, join, splitext, basename
from rejson import Client, Path
import sys
import base64
root = dir(dir(realpath(__file__)))
path = join(root, 'Redis', 'test')
sys.path.append(path)

_dump = {}
"""
_path = os.path.join(path, 'sample.json')
with open(_path, 'r') as outfile:
    _dump = json.load(outfile)
print(type(_dump))
"""

remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
port = '13969'

json_folder = join(root, 'json_files')
json_file_config = join(json_folder, 'config')
json_file_occupancy = join(json_folder, 'occupancy')
json_file_hash = join(json_folder, 'hash')

json_list = [json_file_config, json_file_occupancy, json_file_hash]

def getbasename(path):
    return splitext(basename(path))[0]

def clearAllDB(session_name):
    r.delete(session_name)

def configJsonDir(root):
    json_folder = join(root, 'json_files')
    json_file_config = join(json_folder, 'config')
    json_file_occupancy = join(json_folder, 'occupancy')
    json_file_hash = join(json_folder, 'hash')

    return [json_file_config, json_file_occupancy, json_file_hash]

def importToDB(r,session_name, root):
    json_list = configJsonDir(root)

    for i in json_list:
        data = {}
        path = os.path.join(i, session_name+".json")
        name = session_name + "_" +getbasename(i)
        print(path, name)
        with open(path,"r") as infile:
            data = json.load(infile)
        r.hmset(name, data)

def exportFromDB(r,session_name, root):
    json_list = configJsonDir(root)

    for i in json_list:
        data = {}
        path = os.path.join(i, session_name+".json")
        name = session_name + "_" +getbasename(i)
        data = r.hgetall(name)
        with open(path, "w") as outfile:
            json.dump(data, outfile)

def json_deserialize_image(encoded_str,image_file):
    result = encoded_str.encode("utf-8")
    result = base64.b64decode(result)
    image_result = open(image_file, 'wb') # create a writable image and write the decoding result
    image_result.write(result)

"""
def updateToDB(session_name):
    os.path.join(json_file_config, session_name+".json")
    os.path.join(json_file_config, session_name+".json")
    os.path.join(json_file_config, session_name+".json")
    config_name = session_name
    occupancy_name = session_name+"_occ"
    hash_name = session_name+"_hash"
    r = Client(host = remote_host, port = port, db = 0, password = password)
    with open(json_file_config, 'r') as infile:
        config = json.load(infile)
    with open(json_file_occupancy, 'r') as infile:
        occupancy = json.load(infile)
    with open(json_file_hash, 'r') as infile:
        hash = json.load(infile)
    
    r.hmset(config_name, config)
    r.hmset(occupancy_name, occupancy)
    r.hmset(hash_name, hash)
    print('-------')

    print(r.hmset('restaurant', _dump))
    #delete all keys from database
    r.flushdb()

    #r.delete('restaurant')
    #print(r.hget('restaurant', 'configinfo'))
    print(r.keys())
    print('-------')
"""
"""
r = Client(host = remote_host, port = port, db = 0, password = password, decode_responses= True)
#updateToDB('sample1')
#r.delete('sample_config')
test = {}
test = r.hgetall('sample1_config')
print(type(test.keys()))
print(test)
print(r.keys())
encoded_str = test['processed_img']
json_deserialize_image(encoded_str,"lol.png")
"""
if __name__ == "__main__":
    r = Client(host = remote_host, port = port, db = 0, password = password, decode_responses= True)
    exportFromDB(r, 'sample1', root)