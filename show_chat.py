from BlockchainUtilities import get_blockchain, verify_blockchain
import argparse

if __name__ == '__main__':
    #args
    parser = argparse.ArgumentParser(description='Specify your own hostname and port',prefix_chars='-')
    parser.add_argument('--host',metavar='host',required=False, type=str,help='specify a hostname',default="http://cat")
    parser.add_argument('--port',metavar='port',required=False, type=str,help='specify a port',default='5000')
    args = parser.parse_args()
    host,port = (args.host,args.port)

    # Download the blockchain and verify the blocks
    blockchain = get_blockchain(host,port)

    # Dont enter verify_blockchain if we had a connection error
    blockchain_failed = blockchain is None or not verify_blockchain(blockchain)

    # Print the chat log
    if blockchain_failed:
        exit()

    for hash,block in blockchain:
        print(block['payload']['chat'])
