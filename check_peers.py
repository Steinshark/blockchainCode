from BlockchainUtilities import *
from BlockchainErrors import *

# Package import to work on windows and linux
try:
    sys.path.append("C:\classes")
    sys.path.append("D:\classes")
    from Toolchain.terminal import *
except ModuleNotFoundError:
    sys.path.append("/home/m226252/classes")
    from Toolchain.terminal import *


hosts = [line.strip() for line in open('hosts.txt').readlines()]
ports = ["5000","5001","5002"]

for host in hosts:
    printc(f"attempting conneciton to {host} on port ",BLUE)
    for port in ports:
        printc(f"{port}",BLUE)
        try:
            blockchain_download = get_blockchain(host,port,version=1)
            size = len(blockchain_download)
            printc(f"blockchain verified!\n{size} blocks in chain\n",GREEN)


        except BlockChainVerifyError as b:
            printc(b,RED)

            printc(f"Error Verifying Blockchain\n\n",RED)

        except BlockChainError as b:
            printc(f"Error Downloading Blockchain: Terminated\n\n",RED)
            continue
