from BlockchainUtilities import *
from BlockchainErrors import *

hosts = [line.strip() for line in open('hosts.txt').readlines()]
ports = ["5000","5001","5002"]

for host in hosts:
    print(f"{Color.BLUE}attempting to access host: {host}{Color.END}")
    for port in ports:
        print(f"{Color.TAN}on port {port}{Color.END}")
        try:
            blockchain_download = get_blockchain(host,port)
            size = len(blockchain_download)
            print(f"{Color.GREEN}blockchain verified!\n{size} blocks in chain{Color.END}\n")


        except BlockChainVerifyError as b:
            print(b)

            print(f"Error Verifying Blockchain\n\n")

        except BlockChainError as b:
            print(f"Error Downloading Blockchain: Terminated\n\n")
            continue
