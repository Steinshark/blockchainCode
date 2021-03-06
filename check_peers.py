# Written by Daniel Edmond
# And Everett Stenberg

import  BlockchainUtilities
from    BlockchainErrors import *
from    Toolchain import terminal
import sys 

# Check for command line arguments 
if sys.argv[1]:
    hosts = [sys.argv[1].strip()]

hosts = [line.strip() for line in open('hosts.txt').readlines()]
ports = ["5000","5001","5002"]

for host in hosts:

    terminal.printc(f"attempting connection to {host}",terminal.BLUE)
    for port in ports:
    
        terminal.printc(f"Port: {port}",terminal.BLUE)
        try:
            blockchain_download = BlockchainUtilities.get_blockchain(host,port,version=1)
            size = len(blockchain_download)
            terminal.printc(f"blockchain verified!\n{size} blocks in chain\n",terminal.GREEN)

        # Catches a verification Error 
        except BlockChainVerifyError as b:
            terminal.printc(b,terminal.RED)

            terminal.printc(f"Error Verifying Blockchain\n\n",terminal.RED)
        
        # Generally catches a Conenction Error 
        except BlockChainError as b:
            terminal.printc(f"Error Downloading Blockchain: Terminated\n\n",terminal.RED)
            continue
