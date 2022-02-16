#comment
import flask
from BlockTools import *
from BlockchainUtilities import *
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



# This Class isnt even used....

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
                    block_hash =sha_256_hash('hex',block.encode()).hexdigest()
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
            block_hash =sha_256_hash('hex',block.encode())
            self.blocks[block_hash] = block
            print(f"head is now {list(self.blocks.keys())[-1]}")
        else:
            block_hash =sha_256_hash('hex',gen_block.encode())
            self.blocks[block_hash] = gen_block
            print(f"head is now {list(self.blocks.keys())[-1]}")



        self.app.run(host=host,port=port)



# This Class is where its at

class DynamicServer:


################################################################################
#                                   Run Init
################################################################################

    def __init__(self):

        # Info
        printc(f"\tInitialize",TAN)
        self.app = flask.Flask(__name__)
        self.empty = True
        self.head_hash = ''                     # Keep track of whats in current
        self.longest_chain = 0                  # This will be used as a dynamic
                                                #                 'current.json'
        self.scan_chains()                      # Builds the initial chains list
        printc(f"\tInitialized, Starting server\n\n\n",GREEN)




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
            if not check_fields(block,allowed_versions = [0],allowed_hashes=['']+grab_cached_hashes()):
                printc(f"\trejected block - invalid",RED)
                return "bad block", 418

            # Check if the block checks out as valid
            # Write block if its valid, and update chains

            # Add the block if it is good
            else:

                # Back to JSON
                block_string = dumps(block)
                block_hash   =sha_256_hash(block_string.encode())

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
        if not isdir('cache'):
            mkdir('cache')

        # Make sure 'current.json' exists
        if not isfile('cache/current.json'):
            with open("cache/current.json", 'w') as file:
                file.write('{"head" : "", "length" : 0}')

        # Setup dictionaries
        possible_hashes         = grab_cached_hashes()  # list of all hashes found in 'cache'
        hashes_to_prev_hash     = {}                    # holds prev_hash of block
        hash_len                = {}                    # maps chains to their length

        # Get all hashes found in 'cache' and map them to their prev_hash
        for block_hash in grab_cached_hashes():
                with open(f"cache/{block_hash}.json",'r') as f:
                    prev_hash = loads(f.read().strip())['prev_hash']
                    hashes_to_prev_hash[hash] = prev_hash

        # From possible_hashes, remove all hashes that appeared as a prev_hash
        # This means that they are not the head of a chain
        for not_possible_end_hash in hashes_to_prev_hash.values():
            try:
                possible_hashes.remove(not_possible_end_hash)
            except ValueError:
                printc(f"\t\ttried to remove {not_possible_end_hash[:10]} from list\n\t\tbut it did not exists",RED)

        self.longest_chain = 0
        self.head_hash = ''

        # Find the longest chain
        for block_hash in possible_hashes:
            hash_len[block_hash] = iter_local_chain(block_hash)     # Runs through and grabs length of chain starting from 'hash'

            # Update as necessary
            if hash_len[hash] > self.longest_chain:
                self.longest_chain  = hash_len[block_hash]
                self.head_hash      = block_hash

        # Info
        printc(f"\t\tFound {len(possible_hashes)} chains",TAN)
        printc(f"\t\tLongest chain: {self.longest_chain} block",TAN)

        self.empty = not possible_hashes

        # If there were no chains
        if self.empty:
            hash_len[''] = 0

        # Write the longset chain
        self.write_current()

        # Info
        printc(f"\t\thead is now at {self.head_hash} of len {self.longest_chain}", GREEN)

        # Keep track of all chains
        self.all_chains = hash_len

################################################################################
#                  As server runs, update the current chains
################################################################################

    def update_chains(self,block):
        pp(self.all_chains)
        block_hash =sha_256_hash(dumps(block).encode())
        prev_hash = block['prev_hash']

        # This case we are adding to an existing chain
        if block['prev_hash'] in self.all_chains:

            # Info
            printc(f"pushed block into chain len {self.all_chains[prev_hash]}",TAN)

        # Get old chain length
            prev_len = self.all_chains[prev_hash]

        # Update the chain to have new head
            self.all_chains[block_hash] = prev_len + 1
            printc(f"updated {prev_hash[:10]} chain, now len {self.all_chains[block_hash]}",RED)

            # If this makes a new longest chain, update file
            if self.all_chains[block_hash] > self.longest_chain:
                self.head_hash = block_hash
                self.longest_chain = self.all_chains[block_hash]
                self.empty = False
                self.write_current()

        # This case we are creating a chain

        # This case, this is a new block
        else:

            # Info
            printc(f"pushed block not part of existing chain",TAN)

        # Make new chain
            self.all_chains[block_hash] = 1

        # Check if its the longest (Aka first block)
            if self.all_chains[block_hash] > self.longest_chain:
                self.head_hash = block_hash
                self.longest_chain = self.all_chains[block_hash]
                self.empty = False
                self.write_current()

################################################################################
#                Write the current.json with most recent chain data
################################################################################

    def write_current(self):
        with open('cache/current.json','w') as file:
            flock(file,LOCK_SH)
            info = {'length' : self.longest_chain, 'head' : self.head_hash}
            file.write(dumps(info))
            flock(file,LOCK_UN)

################################################################################
#                      Execute an instance of the server
################################################################################

    def run(self,host='lion',port=5002):

        # Info
        printc(f"SERVER STARTED ON PORT {port}",GREEN)

        # Start
        self.app.run(host=host,port=port)

class VersionOneServer:
################################################################################
#                                   Run Init
################################################################################
    def __init__(self):

        # Info
        printc(f"\tInitialize",TAN)
        self.app = flask.Flask(__name__)
        self.empty = True
        self.head_hash = ''                     # Keep track of whats in current
        self.longest_chain = 0                  # This will be used as a dynamic
                                                #                 'current.json'
        self.scan_chains()                      # Builds the initial chains list
        printc(f"\tInitialized, Starting server\n\n\n",GREEN)
################################################################################
#                    HANDLE HEAD REQUESTS
################################################################################
        @self.app.route('/head')
        def head():
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
            if not check_fields(block,allowed_versions = [1], allowed_hashes=['']+grab_cached_hashes(version=1)):
                printc(f"\trejected block - invalid",RED)
                return "bad block", 418

            # Check if the block checks out as valid
            # Write block if its valid, and update chains

            # Add the block if it is good
            else:

                # Back to JSON
                block_string = dumps(block)
                block_hash   =sha_256_hash(block_string.encode())
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
        if not isdir('cache'):
            mkdir('cache')

        # Make sure 'current.json' exists
        if not isfile('cache/current.json'):
            with open("cache/current.json", 'w') as file:
                file.write('{"head" : "", "length" : 0}')

        # Setup dictionaries
        possible_hashes         = grab_cached_hashes(version=1)  # list of all hashes found in 'cache'
        hashes_to_prev_hash     = {}                    # holds prev_hash of block
        hash_len                = {}                    # maps chains to their length

        # Get all hashes found in 'cache' and map them to their prev_hash
        for block_hash in possible_hashes:
                with open(f"cache/{hash}.json",'r') as f:
                    prev_hash = loads(f.read().strip())['prev_hash']
                    hashes_to_prev_hash[block_hash] = prev_hash

        # From possible_hashes, remove all hashes that appeared as a prev_hash
        # This means that they are not the head of a chain
        for not_possible_end_hash in hashes_to_prev_hash.values():
            try:
                possible_hashes.remove(not_possible_end_hash)
            except ValueError:
                printc(f"\t\ttried to remove {not_possible_end_hash[:10]} from list\n\t\tbut it did not exists",RED)

        self.longest_chain = 0
        self.head_hash = ''

        # Find the longest chain
        for block_hash in possible_hashes:
            hash_len[hash] = iter_local_chain(hash)     # Runs through and grabs length of chain starting from 'hash'

            # Update as necessary
            if hash_len[hash] > self.longest_chain:
                self.longest_chain  = hash_len[hash]
                self.head_hash      = block_hash

        # Info
        printc(f"\t\tFound {len(possible_hashes)} chains",TAN)
        printc(f"\t\tLongest chain: {self.longest_chain} block",TAN)

        self.empty = not possible_hashes

        # If there were no chains
        if self.empty:
            hash_len[''] = 0

        # Write the longset chain
        self.write_current()

        # Info
        printc(f"\t\thead is now at {self.head_hash} of len {self.longest_chain}", GREEN)

        # Keep track of all chains
        self.all_chains = hash_len
################################################################################
#                  As server runs, update the current chains
################################################################################
    def update_chains(self,block):
        block_hash =sha_256_hash(dumps(block).encode())
        prev_hash = block['prev_hash']

        # This case we are adding to an existing chain
        if block['prev_hash'] in self.all_chains:
            # Info
            printc(f"pushed block into chain len {self.all_chains[prev_hash]}",TAN)

        # Get old chain length
            prev_len = self.all_chains[prev_hash]

        # Update the chain to have new head
            self.all_chains[block_hash] = prev_len + 1

            # If this makes a new longest chain, update file
            if self.all_chains[block_hash] > self.longest_chain:
                self.head_hash = block_hash
                self.longest_chain = self.all_chains[block_hash]
                self.empty = False
                self.write_current()

        # This case we are creating a chain

        # This case, this is a new block
        else:

        # Make new chain
            self.all_chains[block_hash] = iter_local_chain(block_hash,version=1)

        # Check if its the longest (Aka first block)
            if self.all_chains[block_hash] > self.longest_chain:
                self.head_hash = block_hash
                self.longest_chain = self.all_chains[block_hash]
                self.empty = False
                self.write_current()
################################################################################
#                Write the current.json with most recent chain data
################################################################################

    def write_current(self):
        with open('cache/current.json','w') as file:
            flock(file,LOCK_SH)
            info = {'length' : self.longest_chain, 'head' : self.head_hash}
            file.write(dumps(info))
            flock(file,LOCK_UN)

################################################################################
#                      Execute an instance of the server
################################################################################

    def run(self,host='lion',port=5002):

        # Info
        printc(f"SERVER STARTED ON PORT {port}",GREEN)

        # Start
        self.app.run(host=host,port=port)

################################################################################
#                    Default Behavior: asks for user input to run
################################################################################

if __name__ == '__main__':

    # Ask for user input
    host = input('run on host: ').strip()
    port = input('run on port: ')

    # Build server
    s = DynamicServer()

    if not host and not port:
        s.run()
    else:
        s.run(host=host,port=int(port))
