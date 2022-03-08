# Witten by Everett Stenberg

df 
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
def get_blockchain(hostname='cat',port='5000',caching=False,cache_location='cache', last_verified='',version=0,verbose=False):

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

    # Continue grabbing new blocks until the genesis block is reached
    index = 0
    while not block_hash== '':
        if verbose:
            terminal.printc(f"{block_hash[:10]}->",terminal.TAN)
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
                block_string = file.read()
                block_dict = BlockTools.JSON_to_block(block_string)
                flock(file,LOCK_UN)

        else:
            try:
                block_string    = BlockTools.retrieve_block(block_hash,host=hostname,port=port)
                block_dict      = loads(block_string)
            except JSONDecodeError as j:
                raise BlockChainError(j)
            except HashRetrievalException as h:
                print(h)
                raise BlockChainError(h)

        # verify the block
        try:
            next_block_string  =   BlockTools.retrieve_block(block_dict['prev_hash'],host=hostname,port=port)
            hashed_to   =   BlockTools.sha_256_hash(next_block_string.encode())

        except HashRetrievalException as h:
            raise BlockChainError(h)
        except KeyError as k:
            raise BlockChainError(k)

        try:
            BlockTools.check_fields(block_dict,block_string,allowed_versions=[0,version],allowed_hashes=['',hashed_to],trust=trust)
            # add it to the chain
            blockchain.insert(0,(block_hash,block_dict))
            #if not already, write the block to file
            if not block_exists:
                with open(block_filename,'w') as file:
                    flock(file,LOCK_EX)
                    file.write(block_string)
                    flock(file,LOCK_UN)

        except BlockChainVerifyError as b:
            raise BlockChainVerifyError(f"\tbad block at position {index}:\n\t{b}")




        block_hash = block_dict['prev_hash']


    return blockchain
