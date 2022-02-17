# Written by Daniel Edmond
# And Everett Stenberg


import BlockTools
import BlockchainErrors
import json
from show_chat import FetchService
import requests
import sys


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
        terminal.printc(f"Checking Peer Nodes",terminal.BLUE)

        # Scan every peer
        for host in self.peers:

            # Info
            terminal.printc(f"\tTrying to connect to host: {host}", terminal.TAN)

            # Attempt to get the head hash that the peer is on
            try:

                # Port is assumed to be 5002
                url = f"http://{host}:5002/head"
                head_hash = requests.get(url,timeout=3).content.decode()

                # Update the peer's information
                self.peer_nodes[host]['head'] = head_hash

            # Catches everything
            except requests.exceptions.ConnectionRefusedError:
                    printc(f"\tError retreiving {host}'s' head_hash: ConectionRefused\n\n",RED)
                    exit(1)
            except requests.exceptions.ReadTimeout:
                printc(f"\tError retreiving {host}'s' head_hash: Timeout\n\n",RED)
                exit(1)
            except requests.exceptions.ConnectionError:
                printc(f"\tError retreiving {host}'s' head_hash: ConnectionError\n\n",RED)
                exit(1)
            except:
                printc(f"\tError retreiving {host}'s' head_hash: unknown reason\n\n",RED)
                exit(1)

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
                terminal.printc(f"\tConnection to {host} succeeded! Chain of length {node_chain_len} found\n\n",terminal.GREEN)

                # Update global chain tracker if this is the longest
                if node_chain_len > self.peer_nodes[self.top_peer]['length']:
                    self.top_peer = host

            # Catch the BlockChainRetrievalError that fetch_blockchain might raise
            except BlockChainRetrievalError as b:
                terminal.printc(f"\t{b}",terminal.TAN)
                terminal.printc(f"\tError in fetch blockchain on host {host}\n\n", terminal.RED)
                continue

        terminal.printc(f"longest chain is len: {self.peer_nodes[self.top_peer]['length']} on host {self.top_peer}",terminal.BLUE)

    # Update peer nodes that do not have the current longest chain
    def update_peers(self):

        for peer in self.peers:

            peer_len    = self.peer_nodes[peer]['length']
            longest_len = self.peer_nodes[self.top_peer]['length']

            if peer_len < longest_len:

                # Info
                terminal.printc(f"Updating peer {peer}",terminal.TAN)

                # Update the peer node to the longest chain found
                full_blockchain = self.peer_nodes[self.top_peer]['fetcher'].blockchain_download
                self.update_peer_node_iterative(peer,full_blockchain)

    # Recursively bring the peer up to date
    def update_peer_node_iterative(self,peer,full_blockchain):

        # Keep track of which blocks need to be pushed
        #stack = []

        # Try pushing blocks until we peer accepts one
        #for (block_hash,block) in full_blockchain:

        #    # Create the payload
        #    payload = {'block' : BlockTools.block_to_JSON(block)}

        #    # Attempt texcept requests.exceptions.ConnectionRefusedError:
        #            printc(f"\tError retreiving {host}'s' head_hash: ConectionRefused\n\n",RED)
        #            exit(1)o give it to the peer
        #    try:
        #        return_code = BlockTools.http_post(peer, 5002, payload)

            # If their server isn't up, then forget it
        #except requests.exceptions.ConnectionException:
        #        return

            # If this block worked, head back up the stack
            # (this is super inefficient I realize, but I
            # dont have the time to rewrite)
        #    if return_code.status_code == 200:
        #        terminal.printc(f"Block accepted! Sending stack!",terminal.GREEN)
        #        break
        #    else:
        #        stack.insert(0,block)

        # Try pushing the rest of the blocks in reverse order
        for b_hash,block in reversed(full_blockchain[start_chain_from(peer,full_blockchain)]):
            # Create the payload
            payload = {'block' : block_to_JSON(block)}

            # Attempt to give it to the peer
            try:
                return_code = http_post(peer, 5002, payload)
                if return_code.status_code == 200:
                    printc(f"Block accepted! {len(stack)} left!",GREEN)

            # If their server isn't up, then forget it
            except ConnectionException:
                return

        printc(f"Finished trying to push chain",TAN)
    # Recursively bring the peer up to date

    #Binary Picker
    def start_chain_from(self,peer,full_blockchain):
        peer_head_hash = BlockTools.retrieve_head_hash(host=peer,port=5002)

        for i, tup in enumerate(full_blockchain):
            if i == tup[0]:
                return i


if __name__ == "__main__":
    n = Node()
    BlockTools.send_chat(input("msg: "), input("host: "), 5002,version=int(input("version: ")))
    n.check_peer_servers()
    n.update_peers()
