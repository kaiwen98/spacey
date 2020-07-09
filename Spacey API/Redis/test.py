import redis
import json
import os
from os.path import dirname as dir

path = os.getcwd()


_path = os.path.join(path, 'sample.json')
with open(_path, 'r') as outfile:
    parsed_json = json.load(outfile)
dump = json.dumps(parsed_json, indent=1, sort_keys=True)
print(dump)
remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
port = '13969'
r = redis.Redis(host=remote_host, port=port, db=0, password = password)
print('hello')
print(r.get('lol'))
print('hello')