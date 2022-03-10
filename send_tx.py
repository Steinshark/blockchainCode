# Written by Daniel Edmond
# And Everett Stenberg


from tabnanny import check
import BlockTools
from BlockchainErrors import *
import json
from show_chat import FetchService
import requests
import sys
from Toolchain import terminal
import subprocess
import nacl.signing 

class Node:

    # Init
    def __init__(self):

        # get keys
        if not sys.argv[1]:
            terminal.printc(f"usage: python3 send_tx.py fname",terminal.RED)
            exit()

        fname = sys.argv[1]
        self.pub_key = subprocess.run(["python3", "keygen.py", fname],text=True,capture_output=True,check=True).stdout
        self.priv_key = open(fname,"r").read()
        print(f"pub: {self.pub_key}\npriv: {self.priv_key}")


        # Fetch the list of peer names (hostnames)
        self.peers = list(  map(    lambda x : x.strip(),   open("hosts.txt",'r').readlines()   ))

        # Create a dict for each host holding relevant information
        self.peer_nodes = {
            host :   {
                        'length' : 0,
                        'host' : None,
                        'fetcher' : None,
                        'head' : None}
            for host in self.peers}

        # Track the peer who's chain is the best (assume first peer at first)
        self.top_peer = self.peers[0]


    def check_peer_servers(self):

        # Info
        terminal.printc(f"Checking Peer Nodes\n",terminal.BLUE)

        for host in self.peers:

            # Info
            terminal.printc(f"Trying host: {host}", terminal.TAN)

            # Attempt to get the head hash that the peer is on
            try:

                # Port is assumed to be 5002
                url = f"http://{host}:5002/head"
                head_hash = requests.get(url,timeout=3).content.decode()
                self.peer_nodes[host]['head'] = head_hash

            # Catches everything
            except requests.exceptions.ReadTimeout:
                terminal.printc(f"\tError retreiving {host}'s' head_hash: Timeout\n\n",terminal.RED)
                continue
            except ConnectionError:
                terminal.printc(f"\tError retreiving {host}'s' head_hash: ConnectionError\n\n",terminal.RED)
                continue
            except:
                terminal.printc(f"\tError retreiving {host}'s' head_hash: unknown reason\n\n",terminal.RED)
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
                terminal.printc(f"\tConnected to {host}! Chain len {node_chain_len} found\n\n",terminal.GREEN)

                # Update global chain tracker if this is the longest
                if node_chain_len > self.peer_nodes[self.top_peer]['length']:
                    self.top_peer = host

            # Catch the BlockChainRetrievalError that fetch_blockchain might raise
            except BlockChainRetrievalError as b:
                terminal.printc(f"\t{b}",terminal.TAN)
                terminal.printc(f"\tError in fetch blockchain on host {host}\n\n", terminal.RED)
                continue

        terminal.printc(f"longest chain is {self.peer_nodes[self.top_peer]['length']} on host {self.top_peer}",terminal.BLUE)


    # Update peer nodes that do not have the current longest chain
    def update_peers(self):
        terminal.printc(f"UPDATING",terminal.BLUE)
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
        for b_hash,block in reversed(full_blockchain[start_chain_from(peer,full_blockchain,0,len(full_blockchain))]):
            # Create the payload
            payload = {'block' : block_to_JSON(block)}

            # Attempt to give it to the peer
            try:
                return_code = http_post(peer, 5002, payload)
                if return_code.status_code == 200:
                   terminal.printc(f"Block accepted! {len(stack)} left!",terminal.GREEN)

            # If their server isn't up, then forget it
            except ConnectionException:
                continue
        terminal.printc(f"Finished trying to push chain",TAN)
    

    #Binary Picker
    def start_chain_from(self,peer,full_blockchain,low,high):
        print(f"({low},{high})")
        # Check base case
        if high >= low:

            mid = (high + low) // 2

            # Try mid block
            payload = {'block' : BlockTools.block_to_JSON(full_blockchain[mid][0])}

            # Attempt texcept requests.exceptions.ConnectionRefusedError:
            try:
                return_code = BlockTools.http_post(peer, 5002, payload)

            # If their server isn't up, then forget it
            except ConnectionException:
                terminal.printc(f"\tError retreiving {peer}'s' head_hash: ConectionRefused\n\n",terminal.RED)
                return

            # If this block worked, head back up the stack
            # (this is super inefficient I realize, but I
            # dont have the time to rewrite)
            if return_code.status_code == 200 and mid == low:
                terminal.printc(f"Block accepted! Sending the rest from {mid}!",terminal.GREEN)
                return mid


            # If element is smaller than mid, then it can only
            # be present in left subarray
            elif return_code.status_code == 200:
                return binary_search(arr, low, mid - 1, x)
        else:
            # Element is not present in the array
            print("not found")
            return -1


    def broadcast_block(self):

        msg     = "hi freinds, its everett"
        ver = 1
        for host in n.peers:
            try:
                terminal.printc(f"\ntrying peer {host}",terminal.BLUE)
                head_hash = BlockTools.retrieve_head_hash(host=host,port=5002,timeout=3)
                payload   = BlockTools.build_payload(msg,self.signing_key,ver)
                new_block = BlockTools.build_block(head_hash,payload,ver)
                BlockTools.send_block(new_block,host,5002,version=ver)
            except ConnectionException as ce:
                print(ce)
if __name__ == "__main__":

    # Get everyone up to date
    n = Node()
    #n.check_peer_servers()
    #n.update_peers()

    # Prepare and send our block (finally!)
    n.broadcast_block()
