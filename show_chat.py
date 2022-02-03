from BlockchainUtilities import *
from BlockchainErrors import *
from json import dumps, loads
from os.path import isfile
import argparse
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN


CHECKPOINT_FILE = 'cache/current.json'


class ChatService:
    def __init__(self):
        self.format_parser()
        self.host = self.args.host
        self.port = self.args.port
        self.blockchain_check = True
        self.last_hash = ''

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


    def fetch_blockchain(self):
        try:
            # Download the blockchain and get info
            self.blockchain_download = get_blockchain(self.host,self.port,caching=True,last_verified=self.last_hash)
            blockchain_len = len(self.blockchain_download)
            head_hash = self.blockchain_download[0][0]

            # save info and write to file
            self.info = {   'head'  : head_hash,\
                            'length': blockchain_len}
            with open('cache/current.json','w') as file:
                file.write(dumps(self.info))


        # done
        except BlockChainError as b:
            print(b)
            print(f"{Color.RED}Error Downloading Blockchain: Terminated{Color.END}")
            self.blockchain_download = None
            self.blockchain_check = False


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
    instance = ChatService()

    # Format the arguments
    instance.format_parser()

    # Try to download the blockchain and verify at the same time
    instance.check_for_head()
    instance.fetch_blockchain()

    # Print the newest chats
    instance.print_blockchain()
