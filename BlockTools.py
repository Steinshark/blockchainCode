#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from BlockchainErrors import *
from json import loads, dumps, JSONDecodeError
from requests import get, post,Timeout, RequestException
from os.path import isfile, isdir, join
from os import mkdir


#########################################################################################
############################ FUNCTIONS FOR PROCESSING BLOCKS ############################
#########################################################################################

# Make a request to where the head hash should be
def retrieve_head_hash(host="cat",port="5000",timeout=3):
    url = f"http://{host}:{port}/head"

    try:
        return get(url,timeout=timeout).content.decode()
        #print(f"recieved {}")
    except Timeout:
        raise ConnectionException(f"{Color.RED}Error: timeout requesting response from {url}")
    except RequestException:
        raise ConnectionException(f"{Color.RED}{Color.BOLD}Error: something went wrong connecting to {url}{Color.END}")
    except ConnectionError:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")


# Yields a block's 'prev_hash' field, given a block
def retrieve_prev_hash(block):
    # Check length requirements - can be 64 or 0 (for genesis block)
    try:
        if not len(block['prev_hash']) in [0,64]:
            raise HashRetrievalException(f"{Color.RED}Error: fetching of '{block['prev_hash'][:70]}'... not a valid hash'{Color.END}")
    except KeyError:
        raise HashRetrievalException(f"{Color.RED}Error: fetching of '{str(block)[:70]}...' missing 'prev_hash' key'{Color.END}")
    return block['prev_hash']


# Convert JSON representation of a block to python dictionary representation of a block
def JSON_to_block(JSON_text):
    try:
        return loads(JSON_text)
    except JSONDecodeError:
        raise DecodeException(f"{Color.RED}Error Decoding JSON: '{JSON_text[:50]}' as block{Color.END}")


# Convert python dictionary representation of a block to JSON representation of a block
def block_to_JSON(block):
    return dumps(block)


# Takes a hash and makes a request to the given URL to return the block with that hash
def retrieve_block(hash_decoded,host="cat",port="5000",timeout=3):
    url = f"http://{host}:{port}/fetch/{hash_decoded}"
    try:
        return get(url,timeout=timeout).content.decode()
    except Timeout:
        raise ConnectionException(f"{Color.RED}Error: timeout requesting response from {url}{Color.END}")
    except RequestException:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")
    except ConnectionError:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")


# Wrapper function for post
def http_post(url,payload,timeout=5):
    try:
        post(url,payload,timeout=timeout)
    except Timeout:
        raise ConnectionException(f"{Color.RED}error: timeout requesting response from {url}")
    except RequestException:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")


# builds a block given the three fields and returns as JSON
def build_block(prev_hash,payload,ver):
    new_block = {   'prev_hash'     : prev_hash,
                    'payload'       : payload,
                    'version'       : ver}
    try:
        encoded_block = block_to_JSON(new_block)
        return encoded_block
    except JSONEncodeException as j:
        raise BlockCreationException(j)



#########################################################################################
########################## FUNCTIONS FOR PROCESSING BLOCKCHAIN ##########################
#########################################################################################



def verify_block(block,next_hash,trusting_blocks,allowed_versions=[0],allowed_hashes=[''],filename=None):
    # Check if we trust the blocks
    if trusting_blocks:
        # Check that the block was downloaded
        if not isfile(filename):
            with open(filename) as file:
                file.write(dumps(block))

    # Verify the block
    if next_hash == '':
        if check_fields(this_block,allowed_hashes=['']):
            if not file_exists:
                with open(filename,'w') as file:
                    file.write(this_block_as_JSON)
            return 0,(this_hash,this_block)
        else:
            raise BlockChainVerifyError(f"{Color.RED}Error: bad block found in position {index}{Color.END}")

    next_block = JSON_to_block(retrieve_block(next_hash,host=hostname,port=port))

    # Ensure that this block is valid
    if not check_fields(this_block,allowed_hashes=['',next_hash]):
        print(f"bad block")
        raise BlockChainVerifyError(f"{Color.RED}Error: bad block found in position {index}{Color.END}")



# given a processed block (python dictionary), check the block for keys, then check
# key values using the named parameters
def check_fields(block,hash,allowed_versions=[0],allowed_hashes=[''],trust=False):
    if trust:
        return True
    # Ensure 'version' field checks out
    if (not 'version' in block) or\
       (not block['version'] in allowed_versions):

        return False


    # Ensure 'prev_hash' field checks out
    elif (not 'prev_hash' in block) or\
         (not block['prev_hash'] in allowed_hashes):

        return False


    # Ensure the payload checks out
    elif (not 'payload' in block) or\
         (not isinstance(block['payload'],dict)) or\
         (('chat' in block['payload']) and (not isinstance(block['payload']['chat'],str))):

        return False


    # Ensure block length req is met <= 1KB
    elif (len(block_to_JSON(block)) > 1024):

        return False

    return True
