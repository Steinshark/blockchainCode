from BlockchainUtilities import *
import BlockTools
from BlockchainErrors import *
from json import dumps, loads
from os.path import isfile
import argparse
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN


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
    def format_parser(self):
        self.parser = argparse.ArgumentParser(description='Specify your own hostname and port',prefix_chars='-')
        self.parser.add_argument('--host',metavar='host',required=False, type=str,help='specify a hostname',default="http://cat")
        self.parser.add_argument('--port',metavar='port',required=False, type=str,help='specify a port',default='5000')
        self.args = self.parser.parse_args()


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
            self.blockchain_download = get_blockchain(self.host,self.port,caching=True,last_verified=self.last_hash,version=self.version)
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
            raise BlockChainRetrievalError(b)


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

    # Create an instance of the class
    instance = FetchService(host='cat',port=5002,version=1)

    # Format the arguments
    #instance.format_parser()

    # Try to download the blockchain and verify at the same time
    instance.check_for_head()
    instance.fetch_blockchain()

    # Print the newest chats
    instance.print_blockchain()
