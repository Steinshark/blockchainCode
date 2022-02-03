import flask
from BlockTools import *
from BlockchainUtilities import *
from os.path import isfile
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN
from json import dumps, loads
import argparse

class StaticServer:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.blocks = OrderedDict()


    # Maps a block hash to the block itself

        @self.app.route('/head')
        def head():
            return list(self.blocks.keys())[-1]

        @self.app.route('/fetch/<digest>')
        def fetch(digest):
            try:
                return self.blocks[digest]

            except KeyError:
                # HTTP code 400 indicates a bad request error
                return 'hash digest not found', 400

        @self.app.route('/<command>')
        def maintain(command):
            # Grab the commands
            arguments = [c.strip() for c in command.split(" ")]

            # Allow for block addition
            if arguments[0] == "add":
                if arguments[1] == "block":
                    block = arguments[2]
                    block_hash = hash('hex',block.encode()).hexdigest()
                    self.blocks[block_hash] = block

            # Allow for block removal
            elif arguments[0] == "remove":
                if arguments[1] == "head":
                    self.blocks.popitem()

            # Error case
            else:
                return f'command {command} not understood by server', 269

    def run(self,host='lion',port=5000,gen_block=None,override=True):
        if override:
            pass
        elif not self.blocks and gen_block is None:
            block = build_block('',{'chat' : 'my very own blockchain!'},0)
            block_hash = hash('hex',block.encode())
            self.blocks[block_hash] = block
            print(f"head is now {list(self.blocks.keys())[-1]}")
        else:
            block_hash = hash('hex',gen_block.encode())
            self.blocks[block_hash] = gen_block
            print(f"head is now {list(self.blocks.keys())[-1]}")



        self.app.run(host=host,port=port)

class DynamicServer:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.head_hash = None
    # Maps a block hash to the block itself

        @self.app.route('/head')
        def head():
            print(f"{Color.TAN}\thead request recieved\n\n\n{Color.END}")
            with open('cache/current.json') as file :
                flock(file,LOCK_SH)
                info = loads(file.read())
                self.blockchain_len = info['length']
                self.head_hash = info['head']
                flock(file,LOCK_UN)

            return self.head_hash

        @self.app.route('/fetch/<digest>')
        def fetch(digest):
            print(f"request made: {digest}")
            filename = f'cache/{digest}.json'
            if not isfile(filename):
                return f'{filename} not found in cache', 400
            else:
                with open(filename) as file:
                    flock(file,LOCK_SH)
                    block = file.read()
                    flock(file,LOCK_UN)
                    return block, 200

        @self.app.route('/push', methods=['POST'])
        def push_block():
            received_data = flask.request.form
            print(f"{Color.TAN}\trecieved '{str(received_data)[:35]} ... {str(received_data)[-20:]}'{Color.END}")

            # assuming block is JSON with 'block' key
            try:
                block = JSON_to_block(received_data['block'])
                print(f"{Color.TAN}\tdecoded to '{str(block)[:35]} ... {str(block)[-20:]}'{Color.END}")

            except JSONDecodeError as j:
                print(f"{Color.RED}\terror decoding sent block{Color.END}")


            if not check_fields(block,allowed_versions = [0],allowed_hashes=['']+grab_cached_hashes(cache_location='cache')):
                print(f"{Color.RED}\trejected block{Color.END}")
                print('\n\n\n')
                return f"{Color.RED}\tblock rejected!{Color.END}", 400

            else:
                print(f"{Color.GREEN}\taccepted block{Color.END}")
                print('\n\n\n')
                return f"{Color.GREEN}\tblock accepted!{Color.END}", 200

    def run(self,host='lion',port=5002):
        print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n{Color.GREEN}SERVER STARTED{Color.END}')
        self.app.run(host=host,port=port)

if __name__ == '__main__':
    host = input('run on host: ').strip()
    port = input('run on port: ')
    s = DynamicServer()
    if not host and not port:
        s.run()
    else:
        s.run(host=host,port=int(port))
