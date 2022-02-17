# Written by Daniel Edmond
# And Everett Stenberg


import BlockchainUtilities
import BlockTools
from BlockchainErrors import *
from json import dumps, loads
from os.path import isfile
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN
import sys

CHECKPOINT_FILE = 'cache/current.json'


class FetchService:
    def __init__(self,host=None,port=-1,version=1):
        if (not host == None) and (not port == -1):
            self.host = host
            self.port = port
        else:
            self.host = self.args.host
            self.port = self.args.port
        self.blockchain_check = True
        self.last_hash = ''
        self.version = 1


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
            # Download the blockchain and get info
            self.blockchain_download = BlockchainUtilities.get_blockchain(self.host,self.port,caching=True,last_verified=self.last_hash,version=self.version)
            blockchain_len = len(self.blockchain_download)
            head_hash = self.blockchain_download[0][0]

            # save info and write to file
            self.info = {   'head'  : head_hash,\
                            'length': blockchain_len}

            if writing:
                with open('cache/current.json','w') as file:
                    file.write(dumps(self.info))


        # done
        except BlockChainError as b:
            self.blockchain_download = None
            self.blockchain_check = False
            printc(f"{b}",RED)


    def print_blockchain(self):
        # Dont try to print an empty blockchain
        if self.blockchain_download is None:
            print("no blockain")
            return

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

    except IndexError:
        printc("usage: python3 show_chat.py host port version",RED)
        exit(1)
    except ValueError:
        printc(f"i cant decode either port: {p} or version: {v} as an integer",RED)
        exit(1)

    # Create an instance of the class
    instance = FetchService(host='cat',port=5002,version=1)

    # Try to download the blockchain and verify at the same time
    instance.check_for_head()
    instance.fetch_blockchain()

    # Print the newest chats
    instance.print_blockchain()
