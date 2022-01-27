#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from BlockchainErrors import *
from json import loads, dumps, JSONDecodeError
from requests import get, post,Timeout, RequestException



#########################################################################################
############################ FUNCTIONS FOR PROCESSING BLOCKS ############################
#########################################################################################

# Make a request to where the head hash should be
def retrieve_head_hash(host="cat",port="5000",timeout=5):
    url = f"http://{host}:{port}/head"

    try:
        if host == 'lion':
            print(f"askign for {url}")
            print(f"got {get(url,timeout=timeout).content}")
        return get(url,timeout=timeout).content.decode()
        #print(f"recieved {}")
    except Timeout:
        raise ConnectionException(f"{Color.RED}Error: timeout requesting response from {url}")
    except RequestException:
        raise ConnectionException(f"{Color.RED}{Color.BOLD}Error: something went wrong connecting to {url}{Color.END}")
    except ConnectionError:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")


# Yields a block's 'prev_hash' field, given a block in JSON format
def retrieve_block_hash(block_as_JSON):
    try:
        block = JSON_to_block(block_as_JSON)
    except DecodeException as d:
        print(d)
        raise HashRetrievalException(f"{Color.RED}Error: JSON decode of '{block['prev_hash'][:70]}' unsuccessful{Color.END}")
        return

    # Check length requirements - can be 64 or 0 (for genesis block)
    try:
        if not len(block['prev_hash']) in [0,64]:
            raise HashRetrievalException(f"{Color.RED}Error: JSON decode of '{block['prev_hash'][:70]}'... not a valid hash'{Color.END}")
    except KeyError:
        raise HashRetrievalException(f"{Color.RED}Error: JSON decode of '{str(block)[:70]}...' uninterpretable as valid block'{Color.END}")
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
def retrieve_block(hash_decoded,host="cat",port="5000",timeout=5):
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
def http_post(url,payload,timeout=5000):
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

# given a processed block (python dictionary), check the block for keys, then check
# key values using the named parameters
def check_fields(block,allowed_versions=[0],allowed_hashes=['']):
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
