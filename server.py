from ServerSource import *
from BlockTools import *
from json import dumps, loads
from os.path import isfile
import argparse
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN

if __name__ == "__main__":
    s = DynamicServer()
    s.run(host='lion',port=5002)
