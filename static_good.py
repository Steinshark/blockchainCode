from ServerSource import *
from BlockTools import *
if __name__ == "__main__":
    s = StaticServer()
    s.run(host='lion',port=5000,gen_block=build_block('',{'chat' : 'a good server indeed'},0))
