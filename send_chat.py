from BlockTools import *
from BlockchainErrors import *
from json import dumps
from show_chat import FetchService
from requests import get
from requests.exceptions import ConnectionError, ReadTimeout
import sys

# Package import to work on windows and linux
# Allows for nice text writing
try:
    sys.path.append("C:\classes")
    sys.path.append("D:\classes")
    sys.path.append("/home/m226252/classes")
    from Toolchain.terminal import *
except ModuleNotFoundError:
    print("Module import failed for Toolchain")


class Node:

    # Init
    def __init__(self):

        # Fetch a list of peer names (hostnames)
        self.peers = list(  map(    lambda x : x.strip(),   open("hosts.txt",'r').readlines()   ))

        # Create a dict for each host holding relevant information
        self.peer_nodes = {
            host :   {
                'length' : 0,
                'host' : None,
                'fetcher' : None,
                'head' : None}
            for host in self.peers
        }

        # The peer who's chain is the best - init as the first peer
        self.top_peer = self.peers[0]

        # Scan all peer's nodes for most recent data
        #self.check_peer_servers()

    # Scan all peer nodes to get node info
    def check_peer_servers(self):

        # Info
        printc(f"Checking Peer Nodes",BLUE)

        # Scan every peer
        for host in self.peers:

            # Info
            printc(f"\tTrying to connect to host: {host}", TAN)

            # Attempt to get the head hash that the peer is on
            try:

                # Port is assumed to be 5002
                url = f"http://{host}:5002/head"
                head_hash = get(url,timeout=3).content.decode()

                # Update the peer's information
                self.peer_nodes[host]['head'] = head_hash

            # Catches everything
            except ConnectionRefusedError:
                printc(f"\tError retreiving {host}'s' head_hash: ConectionRefused\n\n",RED)
                continue
            except ReadTimeout:
                printc(f"\tError retreiving {host}'s' head_hash: Timeout\n\n",RED)
                continue
            except ConnectionError:
                printc(f"\tError retreiving {host}'s' head_hash: ConnectionError\n\n",RED)
                continue
            except:
                printc(f"\tError retreiving {host}'s' head_hash: unknown reason\n\n",RED)
                continue

            # Attempt to fetch the blockchain of that node
            try:
                # Grab the blockchain
                node_fetcher = FetchService(host=host,port=5002,version=1)
                node_fetcher.fetch_blockchain()

                # Assign the fetcher to the node
                self.peer_nodes[host]['fetcher'] = node_fetcher

                # Get info on this peer's chain
                node_chain_len = node_fetcher.info['length']
                self.peer_nodes[host]['length'] = node_chain_len

                # Info
                printc(f"\tConnection to {host} succeeded! Chain of length {node_chain_len} found\n\n",GREEN)

                # Update global chain tracker if this is the longest
                if node_chain_len > self.peer_nodes[self.top_peer]['length']:
                    self.top_peer = host

            # Catch the BlockChainRetrievalError that fetch_blockchain might raise
            except BlockChainRetrievalError as b:
                printc(f"\t{b}",TAN)
                printc(f"\tError in fetch blockchain on host {host}\n\n", RED)
                continue

        printc(f"longest chain is len: {self.peer_nodes[self.top_peer]['length']} on host {self.top_peer}",BLUE)

    # Update peer nodes that do not have the current longest chain
    def update_peers(self):

        for peer in self.peers:

            peer_len    = self.peer_nodes[peer]['length']
            longest_len = self.peer_nodes[self.top_peer]['length']

            if peer_len < longest_len:

                # Info
                printc(f"Updating peer {peer}",TAN)

                # Update the peer node to the longest chain found
                full_blockchain = self.peer_nodes[self.top_peer]['fetcher'].blockchain_download
                self.update_peer_node_iterative(peer,full_blockchain)

    # Recursively bring the peer up to date
    def update_peer_node_iterative(self,peer,full_blockchain):

        # Keep track of which blocks need to be pushed
        stack = []

        # Try pushing blocks until we peer accepts one
        for (block_hash,block) in full_blockchain:

            # Create the payload
            payload = {'block' : block_to_JSON(block)}

            # Attempt to give it to the peer
            try:
                return_code = http_post(peer, 5002, payload)

            # If their server isn't up, then forget it
            except ConnectionException:
                return

            # If this block worked, head back up the stack
            # (this is super inefficient I realize, but I
            # dont have the time to rewrite)
            if return_code.status_code == 200:
                printc(f"Block accepted! Sending stack!",GREEN)
                break
            else:
                stack.insert(0,block)

        # Try pushing the rest of the blocks in reverse order
        for block in stack:
            # Create the payload
            payload = {'block' : block_to_JSON(block)}

            # Attempt to give it to the peer
            try:
                return_code = http_post(peer, 5002, payload)

            # If their server isn't up, then forget it
            except ConnectionException:
                return

        printc(f"Finished trying to push chain",TAN)
    # Recursively bring the peer up to date

    def update_peer_node_iterative_On(self,peer,full_blockchain,stack,recursing_up):

        if recursing_up:

            # Create the payload
            payload = {'block' : block_to_JSON(stack.pop(0)[1])}

            # Attempt to give it to the peer
            try:
                return_code = http_post(peer, 5002, payload)

            # If their server isn't up, then forget it
            except ConnectionException:
                return

            if not stack:
                return

            self.update_peer_node_iterative(peer,full_blockchain,stack,True)


   # NEED TO FIX
        else:
            # Iteratively try to push each block in the blockchain
            for (block_hash,block) in full_blockchain:

                # Create the payload
                payload = {'block' : block_to_JSON(block)}

                # Attempt to give it to the peer
                try:
                    return_code = http_post(peer, 5002, payload)

                # If their server isn't up, then forget it
                except ConnectionException:
                    return

                # If this block worked, head back up the stack
                # (this is super inefficient I realize, but I
                # dont have the time to rewrite)
                if return_code.status_code == 200:
                    self.update_peer_node_iterative(peer,stack,full_blockchain,True)
                    printc(f"Block accepted! Trying next block in current chain",GREEN)
                else:
                    printc(f"{block_hash[:5]}->{return_code},  ",TAN,endl='')
                    continue

        printc(f"Finished trying to push chain",TAN)


if __name__ == "__main__":
    n = Node()
    try:
        if sys.argv[1] == 'c':
            BlockTools.send_chat(input("msg: "), input("host: "), 5002,version=1)
            n.update_peers()
    except IndexError:
        msg = input("msg: ")
        host = input("host: ")
        port = 5002
        n.update_peers()
