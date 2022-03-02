# Written by Daniel Edmond
# And Everett Stenberg


import flask
import BlockTools
from BlockchainErrors import *
import BlockchainUtilities
from os.path import isfile, isdir
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN
from json import dumps, loads
from os import listdir, mkdir
import argparse
import sys
from pprint import pp
from collections import OrderedDict
# Package import to work on windows and linux
# Allows for nice text writing
try:
    sys.path.append("C:\classes")
    sys.path.append("D:\classes")
    sys.path.append("/home/m226252/classes")
    from Toolchain.terminal import *
except ModuleNotFoundError:
    print("Module import failed for Toolchain")

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


################################################################################
#                                   Run Init
################################################################################

    def __init__(self,version=1):

        # Info
        printc(f"\tInitialize Server V.{version}",TAN)
        self.app        =   flask.Flask(__name__)
        self.empty      =   True
        self.version    =   version
        self.max_chain  =   {}
        self.scan_chains()                  # Builds the initial chains list
        printc(f"\tInitialized, Starting server V.{version}\n\n\n",GREEN)




################################################################################
#                    HANDLE HEAD REQUESTS
################################################################################

        @self.app.route('/head')
        def head():

            # Open, lock, read the head file, and send the info back
            with open('cache/current.json') as file :
                flock(file,LOCK_SH)
                info = loads(file.read())
                flock(file,LOCK_UN)


            head_hash = info['head']
            chain_len = info['length']

            # Some simple info code
            printc(f"\thead requested, sending '{head_hash[:10]}'",TAN)
            printc(f"\thead accounting for actual length {chain_len}",TAN)

            # Can't imagine how this would not return 200
            return head_hash, 200


################################################################################
#                    HANDLE HASH-FETCH REQUESTS
################################################################################

        @self.app.route('/fetch/<digest>')
        def fetch(digest):

            # Some simple debug code
            printc(f"request made: {digest}",TAN)

            # Make the (hopefully existing) filename
            filename = f'cache/{digest}.json'

            # Handle an error - 404 == not found here
            if not isfile(filename):    return f'{RED}{filename} not found in cache{RED}', 404

            # Open up that file up (with locks!) and shoot it back to them
            else:
                with open(filename) as file:
                    flock(file,LOCK_SH)
                    block = file.read()
                    flock(file,LOCK_UN)
                    return block, 200


################################################################################
#                    HANDLE PUSH REQUESTS TO THE SERVER
################################################################################

        @self.app.route('/push', methods=['POST'])
        def push_block():
            printc(f"\n\n\nPUSH REQUEST RECEIVED",GREEN)
            # Open, lock, read the head file, and send the info back
            with open('cache/current.json') as file :
                flock(file,LOCK_SH)
                info = loads(file.read())
                flock(file,LOCK_UN)


            head_hash = info['head']
            chain_len = info['length']


            # Get data from form
            received_data = flask.request.form
            printc(f"Head is '{head_hash[:10]}'",TAN)
            
            # Check if the data is JSON decodable
            try:
                block_dict      = loads(received_data['block'])
                block_string    = received_data['block']
                block_hash   = BlockTools.sha_256_hash( block_string.encode()   )
                printc(f"BLOCK IS:",TAN)
                printc(f"{block_string}\n",BLUE)
            except JSONDecodeError as j:
                printc(f"\terror decoding data",RED)
                return f"JSON error when decoding '{block}'", 418

            # Check if the block fields are valid
            accepting_ver       = [0,self.version]
            accepting_hashes    = BlockTools.grab_cached_hashes(version=self.version)
            
            printc(f"hashes initially to {BlockTools.sha_256_hash(block_string.encode())}",RED)
            # Check if valid
            try:
                BlockTools.check_fields(block_dict,
                                        block_string,allowed_versions = accepting_ver,
                                        allowed_hashes   = accepting_hashes)
            except BlockChainVerifyError as b:
                
                printc(f"\trejected block - invalid",RED)
                printc(f"\t{b}\n\n\n",TAN)
                return "bad block", 418

            


            # hash the block
            # Save file in cache folder
            with open(f'cache/{block_hash}.json','w') as file:
                file.write(block_string)

            printc(f"\taccepted block",GREEN)
            self.update_chains(block_dict,block_hash)
            return "Accepted!", 200


################################################################################
#                Before server starts, check which chain to use
################################################################################

    def scan_chains(self):

        # Info
        printc(f"\tFetching local chains",TAN)

        # Make sure 'cache' folder exists
        if not isdir('cache'):  mkdir('cache')

        # Make sure 'current.json' exists
        if not isfile('cache/current.json'):
            with open("cache/current.json", 'w') as file:
                file.write('{"head" : "", "length" : 0}')


        # Find all hashes that exist in 'cache'

        self.chains                 =       {h : 0 for h in BlockTools.grab_cached_hashes(version=1) + BlockTools.grab_cached_hashes(version=0)}
        self.chain_caching          =       {}
        self.max_chain['v0']        =       {'head' : '', 'length' : 0}
        if self.version == 1:
            self.chains_v1          =       {}
            self.max_chain['v1']    =       {'head' : '', 'length' : 0}
        
        # Find all previous hashes in 
        i = 0
        # make chains and max chains
        for local_hash in self.chains:
            print(i)
            i += 1
            # Add to chains regardless of version
            chain_len               = BlockTools.iter_local_chain(local_hash,self.chain_caching)
            self.chains[local_hash] = chain_len
            self.chain_caching[local_hash] = chain_len
            print(chain_len)
            # If valid version 1 hash, check for longest chain
            if self.version == 1 and local_hash[:6] == '000000':
                self.chains_v1[local_hash] = chain_len

                if chain_len > self.max_chain['v1']['length']:
                    self.max_chain['v1']['length']  = chain_len
                    self.max_chain['v1']['head']    = local_hash

            # If version 0 hash, check for longest version 0 chain
            if self.version == 0:
                if chain_len > self.max_chain['v0']['length']:
                    self.max_chain['v0']['length']  = chain_len
                    self.max_chain['v0']['head']    = local_hash

        self.write_current()

################################################################################
#                  This is assumed to be a good block
################################################################################

    def update_chains(self,block,block_hash):

        # Get the length of this chain
        block_chain_len = BlockTools.iter_local_chain(  block['prev_hash'], self.version)

        if self.version == 1:
            if block_chain_len > self.max_chain['v1']['length']:
                self.max_chain['v1']['length']  = block_chain_len
                self.max_chain['v1']['head']    = block_hash
            else:
                printc(f"pushed chain {block_chain_len} not longer than {self.max_chain['v1']['length']}",RED)

        elif self.version == 0:
            if block_chain_len > self.max_chain['v0']['length']:
                self.max_chain['v0']['length']  = block_chain_len
                self.max_chain['v0']['head']    = block_h

        self.write_current()


################################################################################
#                Write the current.json with most recent chain data
################################################################################

    def write_current(self):

        with open('cache/current.json','w') as file:
            flock(file,LOCK_SH)
            if self.version == 1:
                file.write(dumps(self.max_chain['v1']))
            elif self.version == 0:
                file.write(dumps(self.max_chain['v0']))
            flock(file,LOCK_UN)

################################################################################
#                      Execute an instance of the server
################################################################################

    def run(self,host='lion',port=5002,version=1):

        # Info
        printc(f"SERVER STARTED ON PORT {port}",GREEN)

        # Start
        self.app.run(host=host,port=port)
