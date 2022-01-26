from blockchain_utilities import *
from BlockchainErrors import *

hosts = [line.strip() for line in open('hosts.txt').readlines()]
ports = ["5000","5001"]

for host in hosts:
    print(f"{Color.BLUE}attempting to access host: {host}{Color.END}")
    for port in ports:
        print(f"on port {port}")
        try:
            blockchain_download = get_blockchain(host,port)
        except BlockChainError as b:
            print(b)
            print(f"Error Downloading Blockchain: Terminated\n")
            continue


        try:
            verify_blockchain(blockchain_download)
            print(f"{Color.GREEN}blockchain verified!{Color.END}")
        except BlockChainVerifyError as b:
            print(b)
            continue
    print("\n\n")
