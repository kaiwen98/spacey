import redis
import json
import os
from os.path import dirname, realpath, join
from os.path import dirname as dir
from rejson import Client, Path
import sys
root = dir(dir(realpath(__file__)))
path = join(root, 'Redis', 'test')
sys.path.append(path)
import test1
print(root)
path = os.getcwd()
test1.boo()
_dump = {}
_path = os.path.join(path, 'sample.json')
with open(_path, 'r') as outfile:
    _dump = json.load(outfile)
print(type(_dump))

remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
port = '13969'

r = Client(host = remote_host, port = port, db = 0, password = password)
print('-------')

print(r.hmset('restaurant', _dump))
#delete all keys from database

print(r.hget('restaurant', 'configinfo'))
print('-------')

