from hashlib import sha256, sha3_256
from json import loads, dumps, JSONDecodeError
from requests import get, post, Timeout, RequestException, ConnectionError
from BlockTools import *
from BlockchainErrors import *



# hash function wrapper
def hash(format,bytes):
    hasher = sha3_256()
    hasher.update(bytes)
    digest = hasher.digest()
    if format == 'hex':
        return digest.hex()
    elif format == 'bytes':
        return digest



# builds a block given the three fields and returns as JSON
def build_block(prev_hash,payload,ver):
    new_block = {   'prev_hash'     : prev_hash,
                    'payload'       : payload,
                    'version'       : ver}
    return block_to_JSON(new_block)



# encodes the blockchain found at a given hostname and port into a list
# of tuples: (hash, blockAsPythonDict)
def get_blockchain(hostname='cat',port='5000'):
    blockchain = []

    try:
        hash_to_next_block = retrieve_head_hash(host=hostname,port=port)
    except ConnectionException as c:
        raise BlockChainRetrievalError(str(c))


    # Continue grabbing new blocks until the genesis block is reached
    while not hash_to_next_block == '':
        try:
            next_block_as_JSON = retrieve_block(hash_to_next_block,host=hostname,port=port)
        except ConnectionException as c:
            print(c)
            return
        try:
            next_block = JSON_to_block(next_block_as_JSON)
        except DecodeException as d:
            print(d)
            print(f"Blockchain download failed")
            return
        blockchain.insert(0,(hash_to_next_block,next_block))
        try:
            hash_to_next_block = retrieve_block_hash(next_block_as_JSON)
        except HashRetrievalException as h:
            print(h)
            print(f"Blockchain download failed")
            return
    return blockchain



# Used to verify the entire blockchain at once. 'blockchain' is
# a list of tuples starting with the genesis block
def verify_blockchain(blockchain):
    if not isinstance(blockchain,list):
        raise BlockChainVerifyError(f"Error: improper encoding of blockchain: expected list, got: {type(blockchain)}")
        return
    blockchain = list(reversed(blockchain))
    dinq_list = []

    # Check all blocks
    for index, block in enumerate(blockchain):
        # Define the current block and the prev_hash (or empty hash for genesis block)
        block = block[1]

        if index == len(blockchain) - 1:
            prev_hash = ''
        else:
            prev_hash = hash('hex',block_to_JSON(blockchain[index+1][1]).encode())

        # Add any blocks that do not validate to the dinq_list
        if not check_fields(block,allowed_hashes=[prev_hash]):
            dinq_list.append(block)

    # If the dinq_list is not empty, then the blockain verification went wrong
    if dinq_list:
        print(f"found {len(dinq_list)} bad blocks")
        return False

    return dinq_list



if __name__ == '__main__':
    try:
        bl = get_blockchain()
    except BlockChainRetrievalError as b:
        print(b)
        exit()
    try:
        v = verify_blockchain(bl)
    except BlockChainVerifyError as b:
        print(b)
        exit()
        hmm
