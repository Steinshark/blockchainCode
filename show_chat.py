from BlockchainUtilities import *
from BlockchainErrors import *
import argparse

class ChatService:
    def __init__(self):
        self.format_parser()
        self.host = self.args.host
        self.port = self.args.port
        self.blockchain_check = True

    def format_parser(self):
        self.parser = argparse.ArgumentParser(description='Specify your own hostname and port',prefix_chars='-')
        self.parser.add_argument('--host',metavar='host',required=False, type=str,help='specify a hostname',default="http://cat")
        self.parser.add_argument('--port',metavar='port',required=False, type=str,help='specify a port',default='5000')
        self.args = self.parser.parse_args()


    def download_blockchain(self):
        try:
            self.blockchain_download = get_blockchain(self.host,self.port)
        except BlockChainError as b:
            print(b)
            print(f"{Color.RED}Error Downloading Blockchain: Terminated{Color.END}")
            self.blockchain_download = None
            self.blockchain_check = False


    def print_blockchain(self):
        if self.blockchain_download is None:
            print("no blockain")
            return

        for block,hash in self.blockchain_download:
            print(f"{block['payload']['chat'][:20]}")




if __name__ == '__main__':

    # Create an instance of the class
    instance = ChatService()

    # Format the arguments
    instance.format_parser()

    # Try to download the blockchain and verify at the same time
    instance.download_blockchain()

    instance.print_blockchain()
