import flask
from BlockTools import build_block
from BlockchainUtilities import hash
from os.path import isfile
from fcntl import flock, LOCK_SH,LOCK_EX

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
            with open('cache/current.json') as file :
                flock(file,LOCK_SH)
                info = loads(file.read())
                self.blockchain_len = info['length']
                self.head_hash = info['head']
                flock(file,LOCK_UN)

            return self.head_hash

        @self.app.route('/fetch/<digest>')
        def fetch(digest):
            filename = f'cache/{digest}.json'
            if not isfile(filename):
                return f'{filename} not found in cache', 400
            else:
                with open(filename) as file:
                    flock(file,LOCK_SH)
                    block = file.read()
                    flock(file,LOCK_UN)
                    return block, 200


    def run(self,host='lion',port=5002):
        self.app.run(host=host,port=port)

if __name__ == '__main__':
    host = input('run on host: ').strip()
    port = input('run on port: ')
    s = Server()
    if not host and not port:
        s.run()
    else:
        s.run(host=host,port=int(port))
