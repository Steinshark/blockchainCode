# Written by Daniel Edmond
# And Everett Stenberg

from ServerSource import *
from BlockTools import *
import sys

if __name__ == "__main__":
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        s = StaticServer()
        s.run(host='lion',port=5001,gen_block=build_block('',{'chat' : 'a BAD server >:('},-4000000))
    except IndexError:
        print("usage:python3 static_bad.py host port ")
    except ValueError:
        print(f"i couldnt convert {sys.argv[2]} to an int")
