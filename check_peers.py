from blockchain_utilities import *
from BlockchainErrors import *

hosts = [line.strip() for line in open('hosts.txt').readlines()]
ports = ["5000","5001"]

for host in hosts:
    print(f"{Color.OKBLUE}attempting to access host: {host}{Color.ENDC}")
    for port in ports:
        print(f"on port {port}")
        try:
            blockchain_download = get_blockchain(host,port)
        except BlockChainError as b:
            print(b)
            continue


        try:
            verify_blockchain(blockchain_download)
            print(f"{Colors.OKBLUE}blockchain verified!{Colors.ENDC}")
        except BlockChainVerifyError as b:
            print(b)
            continue
    print("\n\n")
