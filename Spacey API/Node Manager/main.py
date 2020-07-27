import sys
import os
import redis

from os.path import dirname as dir
_root = dir(dir(dir(sys.executable)))

#_root = dir(dir(dir(__file__))) 
sys.path.append(os.path.join(_root, "Node Manager"))
from admin_map_creator import main

if __name__ == "__main__":
    main()  