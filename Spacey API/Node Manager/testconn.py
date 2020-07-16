import urllib
from urllib.error import URLError
from urllib.request import urlopen

def internet_on():
    try:
        urlopen('http://216.58.192.142', timeout=1)
        return True
    except URLError as err: 
        return False

