# Written by Daniel Edmond
# And Everett Stenberg


#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from hashlib import sha256, sha3_256
from json import loads, dumps, JSONDecodeError
from requests import get, post, Timeout
import BlockTools
from BlockchainErrors import *
from os.path import isfile, isdir, join
from os import mkdir
from fcntl import flock, LOCK_SH,LOCK_EX, LOCK_UN
from Toolchain import terminal
#########################################################################################
############################### FUNCTIONS FOR CRYPTOGRAPHY ##############################
#########################################################################################



# encodes the blockchain found at a given hostname and port into a list
# of tuples: (hash, blockAsPythonDict)
def get_blockchain(hostname='cat',port='5000',caching=False,cache_location='cache', last_verified='',version=0):

    # if caching, then check if the folder exists, and create if not
    if caching:
        if not isdir(cache_location):
            mkdir(cache_location)


    # init all variables we will use
    blockchain = []
    block_hash= None
    trust = False
    # Grab the hash
    try:
        block_hash= BlockTools.retrieve_head_hash(host=hostname,port=port)
    except ConnectionException as c:
        raise BlockChainRetrievalError(f"Error retrieving head hash\n{c}")

    index = 0
    # Continue grabbing new blocks until the genesis block is reached
    index = 0
    while not block_hash== '':
        index += 1

        # Trust blocks we have verified already
        if block_hash == last_verified:
            trust = True

        # check if this block exists in cache
        block_filename  = f"{cache_location}/{block_hash}.json"
        block_exists    = isfile(block_filename)

        # get the block in python form
        if block_exists:
            with open(block_filename, 'r') as file:
                flock(file,LOCK_SH)
                block = BlockTools.JSON_to_block(file.read())
                flock(file,LOCK_UN)

        else:
            try:
                block = BlockTools.retrieve_block(block_hash,host=hostname,port=port)
                block = loads(block)
            except JSONDecodeError as j:
                raise BlockChainError(f"{Color.RED}Error decoding JSON text fetched from server: {block[:30]}{Color.END}")
            except HashRetrievalException as h:
                print(h)
                raise BlockChainError(h)

        # verify the block
        try:
            next_block  =   BlockTools.retrieve_block(block['prev_hash'],host=hostname,port=port)
            hashed_to   =   BlockTools.sha_256_hash(next_block.encode())

        except HashRetrievalException as h:
            raise BlockChainError(h)

        try:
            BlockTools.check_fields(block,allowed_versions=[version],allowed_hashes=['',hashed_to],trust=False)
        except BlockChainVerifyError as b:
            raise BlockChainVerifyError(f"bad block at position {index}:\n\t{b}")



        if check:
            # add it to the chain
            blockchain.insert(0,(block_hash,block))
            #if not already, write the block to file
            if not block_exists:
                with open(block_filename,'w') as file:
                    flock(file,LOCK_EX)
                    file.write(dumps(block))
                    flock(file,LOCK_UN)
        else:
            raise BlockChainVerifyError(f"bad block at position {index}")
        block_hash = block['prev_hash']
        print(block_hash)


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
            prev_hash = BlockTools.sha_256_hash(BlockTools.block_to_JSON(blockchain[index+1][1]).encode())

        # Check the fields of the block for errors
        if not BlockToosl.check_fields(block,allowed_hashes=[prev_hash]):
            raise BlockChainVerifyError(f"{Color.RED}Error: bad block found in position {index}{Color.END}")
    return len(blockchain)
