from server import *
from BlockTools import *
if __name__ == "__main__":
    s = Server()
    s.run(host='lion',port=5000,override=True)
    s.insert_block(build_block('',{'chat' : 'a good server indeed'},0))
