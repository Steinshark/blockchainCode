from ServerSource import *
from BlockTools import *
import sys

if __name__ == "__main__":
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        ver  = int(sys.argv[3])
        s = DynamicServer()
        s.run(host=host,port=port,version=ver)

    except IndexError:
        print("usage: server.py host port ver")
    except ValueError:
        print("I cant decypher either the port or ver as an int")
