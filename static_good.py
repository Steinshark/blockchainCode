# Written by Daniel Edmond
# And Everett Stenberg

from ServerSource import *
from BlockTools import *

if __name__ == "__main__":
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        s = StaticServer()
        s.run(host='lion',port=5000,gen_block=build_block('',{'chat' : 'a good server indeed'},0))
    except IndexError:
        print("usage:python3 static_bad.py host port ")
    except ValueError:
        print(f"i couldnt convert {sys.argv[2]} to an int")
