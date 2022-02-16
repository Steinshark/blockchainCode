#comment
import flask
import BlockTools
import BlockchainUtilities
from os.path import isfile, isdir
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN
from json import dumps, loads
from os import listdir, mkdir
import argparse
import sys
from pprint import pp

# Package import to work on windows and linux
# Allows for nice text writing
try:
    sys.path.append("C:\classes")
    sys.path.append("D:\classes")
    sys.path.append("/home/m226252/classes")
    from Toolchain.terminal import *
except ModuleNotFoundError:
    print("Module import failed for Toolchain")

# This Class is where its at

class DynamicServer:


################################################################################
#                                   Run Init
################################################################################

    def __init__(self, version=1):

        # Info
        printc(f"\tInitialize Server V.{version}",TAN)
        self.app = flask.Flask(__name__)
        self.empty = True
        self.version = version
        self.scan_chains()                  # Builds the initial chains list
        printc(f"\tInitialized, Starting server V.{version}\n\n\n",GREEN)




################################################################################
#                    HANDLE HEAD REQUESTS
################################################################################

        @self.app.route('/head')
        def head():
            pp(self.all_chains)

            # Some simple debug code
            printc(f"\thead requested, sending {self.head_hash[:10]}",TAN)
            printc(f"\thead accounting for actual length {iter_local_chain(self.head_hash)}",TAN)

            # Open, lock, read the head file, and send the info back
            with open('cache/current.json') as file :
                flock(file,LOCK_SH)
                info = loads(file.read())
                flock(file,LOCK_UN)

            # Can't imagine how this would not return 200
            return info['head'], 200


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
            if not isfile(filename):
                return f'{RED}{filename} not found in cache{RED}', 404

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

            # Get data from form
            received_data = flask.request.form
            printc(f"\twhile head is {self.head_hash[:5]}",TAN,endl='')
            printc(f"\trecieved '{str(received_data)[:35]} ... {str(received_data)[-20:]}'",TAN)

            # Check if the data is JSON decodable
            try:
                block = JSON_to_block(received_data['block'])
                printc(f"\tdecoded to '{str(block)[:35]} ... {str(block)[-20:]}'",TAN)

            except JSONDecodeError as j:
                printc(f"\terror decoding data",RED)
                return f"JSON error when decoding '{block}'", 418

            # Check if the block fields are valid
            accepting_ver       = [0,self.version]
            accepting_hashes    = BlockTools.grab_cached_hashes(version=self.version)

            # Check if valid
            if not check_fields(    block,
                                    allowed_versions = accepting_ver,
                                    allowed_hashes   = accepting_hashes):

                printc(f"\trejected block - invalid",RED)
                return "bad block", 418

            # Add the block if it is good
            else:

                # Back to JSON
                block_string = dumps(block)

                # hash the block
                block_hash   = BlockTools.sha_256_hash( block_string.encode()   )

                # Save file in cache folder
                with open(f'cache/{block_hash}.json','w') as file:
                    file.write(block_string)

                printc(f"\taccepted block",GREEN)
                self.update_chains(block)
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
        self.max_chain['v0']        =       {'head' : '', 'length' : 0}

        if self.version == 1:
            self.chains_v1          =       {}
            self.max_chain['v1']    =       {'head' : '', 'length' : 0}

        # make chains and max chains
        for local_hash in self.chains:

            # Add to chains regardless of version
            chain_len               = iter_local_chain(local_hash)
            self.chains[local_hash] = chain_len

            # If valid version 1 hash, check for longest chain
            if version == 1 and local_hash[:6] == '000000':
                self.chains_v1[local_hash] = chain_len

                if chain_len > self.max_chain['v1']['length']:
                    self.max_chain['v1']['length']  = chain_len
                    self.max_chain['v1']['head']    = local_hash

            # If version 0 hash, check for longest version 0 chain
            if version == 0:
                if chain_len > self.max_chain['v0']['length']:
                    self.max_chain['v0']['length']  = chain_len
                    self.max_chain['v0']['head']    = local_hash

        self.write_current()

################################################################################
#                  This is assumed to be a good block
################################################################################

    def update_chains(self,block):

        # Get the length of this chain
        block_chain_len = BlockTools.iter_local_chain(  block['prev_hash'], self.version)
        block_hash      = BlockTools.sha_256_hash(      dumps(block).encode() )

        if self.version == 1:
            if block_chain_len > self.max_chain['v1']['length']:
                self.max_chain['v1']['length']  = block_chain_len
                self.max_chain['v1']['head']    = block_hash

        elif self.version == 0:
            if block_chain_len > self.max_chain['v0']['length']:
                self.max_chain['v0']['length']  = block_chain_len
                self.max_chain['v0']['head']    = block_h

        write_current()


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
        self.app.run(host=host,port=port,version=version)
