from ServerSource import *
from BlockTools import *
import sys 

if __name__ == "__main__":
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
    except IndexError:
        print("usage: server.py host port")
    s = VersionOneServer()
    s.run(host=host,port=port)
