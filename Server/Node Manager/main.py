import sys
import os
from os.path import dirname
sys.path.append(dirname(dirname(sys.executable)))
from config import main

if __name__ == "__main__":
    
    main()