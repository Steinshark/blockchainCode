#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from hashlib import sha256, sha3_256
from json import loads, dumps, JSONDecodeError
from requests import get, post, Timeout, RequestException, ConnectionError
from BlockTools import *
from BlockchainErrors import *
from os.path import isfile, isdir, join
from os import mkdir

#########################################################################################
############################### FUNCTIONS FOR CRYPTOGRAPHY ##############################
#########################################################################################

# hash function wrapper
def hash(format,bytes):
    hasher = sha3_256()
    hasher.update(bytes)
    digest = hasher.digest()
    if format == 'hex':
        return digest.hex()
    elif format == 'bytes':
        return digest


# encodes the blockchain found at a given hostname and port into a list
# of tuples: (hash, blockAsPythonDict)
def get_blockchain(hostname='cat',port='5000',caching=False,cache_location='cache', last_verified=''):

    # if caching, then check if the folder exists, and create if not
    if caching:
        if not isdir(cache_location):
            mkdir(cache_location)


    # init all variables we will use
    blockchain = []
    trust = False
    block_hash= None

    # Grab the hash
    try:
        block_hash= retrieve_head_hash(host=hostname,port=port)
        print(f"head block_hashis: {block_hash}")
    except ConnectionException as c:
        raise BlockChainRetrievalError(f"Error retrieving head hash\n{c}")


    # Continue grabbing new blocks until the genesis block is reached
    index = 0
    while not block_hash== '':
        # First check if this block has been verified
        if block_hash== last_verified:
            trust = True

        # check if this block exists in cache
        block_filename  = f"{cache_location}/{block_hash}.json"
        block_exists    = isfile(block_filename)

        # get the block in python form
        if block_exists:
            block = open(block_filename,'r').read()
            print(f"block : {block}")
            block = loads(block)
        else:
            block = retrieve_block(block_hash,host=hostname,port=port)
            print(f"block : {block}")
            block = loads(block)

        # verify the block
        print(f"checking {block_hash[:10]} on {block}")
        hashed_to = hash('hex',retrieve_block(retrieve_prev_hash(block),host=hostname,port=port).encode())
        print(f"hashed to {hashed_to}")
        check = check_fields(block,block_hash,allowed_versions=[0],allowed_hashes=['',hashed_to],trust=trust)
        if check:
            # add it to the chain
            print(f"added{(hash,block)}")
            blockchain.insert(0,(hash,block))
            #if not already, write the block to file
            if not block_exists:
                open(block_filename,'w').write(dumps(block))
            else:

        block_hash = retrieve_prev_hash(block)


    return blockchain


# Used to verify the entire blockchain at once. 'blockchain' is
# a list of tuples starting with the genesis block
def verify_blockchain(blockchain):
    if not isinstance(blockchain,list):
        raise BlockChainVerifyError(f"{Color.RED}Error: improper encoding of blockchain: expected list, got: {type(blockchain)}{Color.END}")
    blockchain = list(reversed(blockchain))

    # Check all blocks
    for index, block in enumerate(blockchain):
        # Define the current block and the prev_hash (or empty hash for genesis block)
        block = block[1]
        if index == len(blockchain) - 1:
            prev_hash = ''
        else:
            prev_hash = hash('hex',block_to_JSON(blockchain[index+1][1]).encode())

        # Check the fields of the block for errors
        if not check_fields(block,allowed_hashes=[prev_hash]):
            raise BlockChainVerifyError(f"{Color.RED}Error: bad block found in position {index}{Color.END}")
    return len(blockchain)
