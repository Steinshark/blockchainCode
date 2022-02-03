from ServerSource import *
from BlockTools import *

if __name__ == "__main__":
    s = Server()
    s.run(host='lion',port=5001,gen_block=build_block('',{'chat' : 'a BAD server >:('},-4000000))
