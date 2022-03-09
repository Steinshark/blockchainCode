# Written by Daniel Edmond
# And Everett Stenberg


import BlockchainUtilities
import BlockTools
from BlockchainErrors import *
from json import dumps, loads
from os.path import isfile
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN
import sys
from Toolchain import terminal
import time 
CHECKPOINT_FILE = 'cache/current.json'


class FetchService:
    def __init__(self,host=None,port=-1,version=1):
        self.host = host
        self.port = port
        self.version = version
        self.blockchain_check = True
        self.last_hash = ''
        self.version = 1
        self.longest_chain = 0
        self.head_hash = ''
    

    def check_for_head(self):
        if isfile(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE) as file :
                flock(file,LOCK_SH)
                info = loads(file.read())
                self.blockchain_len = info['length']
                self.last_hash = info['head']
                flock(file,LOCK_UN)


    def fetch_blockchain(self,writing=True):
        try:
            t1 = time.time()
            # Download the blockchain and get info
            terminal.printc(f"checking host: {self.host} port: {self.port}",terminal.TAN,endl=' ')
            self.blockchain_download = BlockchainUtilities.get_blockchain(self.host,self.port,caching=True,last_verified=self.last_hash,version=self.version)
            blockchain_len = len(self.blockchain_download)
            if blockchain_len:
                head_hash = self.blockchain_download[0][0]
            else:
                raise BlockChainRetrievalError("no blockchain here: len was 0")
            # save info and write to file
            self.info = {   'head'  : head_hash,\
                            'length': blockchain_len}

            if writing and blockchain_len > self.longest_chain:
                self.longest_chain  = blockchain_len
                self.head_hash      = head_hash
            terminal.printc(f"-fetch took {(time.time()-t1):.3f} seconds",terminal.TAN)
        # done

        except BlockChainError as b:
            self.blockchain_download = None
            self.blockchain_check = False
            terminal.printc(f"{b}",terminal.RED)
            raise BlockChainRetrievalError(b)



    def print_blockchain(self):
        # Dont try to print an empty blockchain
        if self.blockchain_download is None:
            terminal.printc(f"this should not have happened.... im going to die now",terminal.RED)

        # Print the blockchain
        else:
            seen = False
            for hash,block in self.blockchain_download:
                if hash == self.last_hash:
                    seen = True
                    if not seen:
                        print(f"{block['payload']['chat']}")




if __name__ == '__main__':

    # Grab arguments
    try:
        h = sys.argv[1]
        p = int(sys.argv[2])
        v = int(sys.argv[3])
        instance = FetchService(host=h,port=p,version=v)
        instance.fetch_blockchain()
        instance.print_blockchain()

    except IndexError:
        terminal.printc("usage: python3 show_chat.py host port version",terminal.RED)
        exit(1)
    except ValueError:
        terminal.printc(f"i cant decode either port: {p} or version: {v} as an integer",terminal.RED)
        exit(1)
