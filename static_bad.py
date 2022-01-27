from server import *
from BlockTools import *

if __name__ == "__main__":
    s = Server()
    s.run(host='lion',port=5001,override=True)
    s.insert_block(build_block('',{'chat' : 'a bad server :o'},-4000000))
