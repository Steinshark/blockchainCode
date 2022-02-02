#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from hashlib import sha256, sha3_256
from json import loads, dumps, JSONDecodeError
from requests import get, post, Timeout, RequestException, ConnectionError
from BlockTools import *
from BlockchainErrors import *
from os.path import *
from os import *

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
def get_blockchain(hostname='cat',port='5000',caching=False,cache_location='cache'):
    if caching:
        if not isdir(cache_location):
            mkdir(cache_location)


    blockchain = []
    this_block = None
    next_block = None
    this_hash = None
    next_hash = None
    try:
        this_hash = retrieve_head_hash(host=hostname,port=port)
    except ConnectionException as c:
        raise BlockChainRetrievalError(f"Error retrieving head hash\n{c}")


    # Continue grabbing new blocks until the genesis block is reached
    index = 0
    while not this_hash == '':
        index += 1
        block_filename = f"{this_hash}.json"
        file_exists = isfile(block_filename)
        # try the whole thing
        try:
            # Acquire the necessary items
            if not file_exists:
                this_block_as_JSON = retrieve_block(this_hash,host=hostname,port=port)
            else:
                with open(filename,'r') as file:
                    this_block_as_JSON = file.read()

            this_block = JSON_to_block(this_block_as_JSON)
            next_hash = retrieve_prev_hash(this_block_as_JSON)


            if next_hash == '':
                if check_fields(this_block,allowed_hashes=['',next_hash]):
                    if not file_exists:
                        with open(filename,'w') as file:
                            file.write(this_block_as_JSON)
                    blockchain.insert(0,(this_hash,this_block))
                    return blockchain
                else:
                    print(f"bad block")
                    raise BlockChainVerifyError(f"{Color.RED}Error: bad block found in position {index}{Color.END}")

            next_block = JSON_to_block(retrieve_block(next_hash,host=hostname,port=port))

            # Ensure that this block is valid
            if not check_fields(this_block,allowed_hashes=['',next_hash]):
                print(f"bad block")
                raise BlockChainVerifyError(f"{Color.RED}Error: bad block found in position {index}{Color.END}")

            # If everything checks out, then add this block and continue
            if (this_hash,this_block) in blockchain:
                raise BlockChainVerifyError(f"{Color.RED}Error: duplicate block found in position {index}{Color.END}")

            if not file_exists:
                with open(filename,'w') as file:
                    file.write(this_block_as_JSON)
            blockchain.insert(0,(this_hash,this_block))
            this_hash = next_hash


        except ConnectionException as c:
            raise BlockChainRetrievalError(str(c))
        except DecodeException as d:
            raise BlockChainRetrievalError(str(d))
        except HashRetrievalException as h:
            raise BlockChainRetrievalError(str(h))

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
