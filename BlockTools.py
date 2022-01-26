#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from BlockchainErrors import *
from json import loads, dumps, JSONDecodeError
from requests import get, post,Timeout


#########################################################################################
############################ FUNCTIONS FOR PROCESSING BLOCKS ############################
#########################################################################################


def retreive_head_hash(host="cat",port="5000",timeout=5):
    url = f"http://{host}:{port}/head"

    try:
        get(url,timeout=timeout).content.decode()
    except Timeout:
        raise ConnectionException(f"Error: timeout requesting response from {url}")
    except RequestException:
        raise ConnectionException(f"Error: something went wrong connecting to {url}")
    except ConnectionError:
        raise ConnectionException(f"Error: something went wrong connecting to {url}")


# yields a block's prev_hash field, given a block in JSON format
def retreive_block_hash(block_as_JSON):
    try:
        block = JSON_to_block(block_as_JSON)
    except DecodeException as d:
        return

    # Check length requirements - can be 64 or 0 (for genesis block)
    if not len(block['prev_hash']) in [0,64]:
        raise HashRetrievalException(f"Error: JSON decode of '{block['prev_hash'][:70]}'... not a valid hash'")
    return block['prev_hash']


# JSON representation of a block to python dictionary representation of a block
def JSON_to_block(JSON_text):
    try:
        return loads(JSON_text)
    except JSONDecodeError:
        raise DecodeException(f'Error Decoding JSON: "{JSON_text[:50]}" as block')


# python dictionary representation of a block to JSON representation of a block
def block_to_JSON(block):
    return dumps(block)


# Takes a hash and makes a request to the given URL to return the block with that hash
def retreive_block(hash_decoded,host="cat",port="5000",timeout=5):
    url = f"http://{host}:{port}/fetch/{hash_decoded}"
    try:
        return get(url,timeout=timeout).content.decode()
    except Timeout:
        raise ConnectionException(f"Error: timeout requesting response from {url}")
    except RequestException:
        raise ConnectionException(f"Error: something went wrong connecting to {url}")
    except ConnectionError:
        raise ConnectionException(f"Error: something went wrong connecting to {url}")


# Wrapper function for post
def http_post(url,payload,timeout=5000):
    try:
        post(url,payload,timeout=timeout)
    except Timeout:
        raise ConnectionException(f"error: timeout requesting response from {url}")
    except RequestException:
        raise ConnectionException(f"error: something went wrong connecting to {url}")



#########################################################################################
########################## FUNCTIONS FOR PROCESSING BLOCKCHAIN ##########################
#########################################################################################

# given a processed block (python dictionary), check the block for keys, then check
# key values using the named parameters
def check_fields(block,prev_hash,allowed_versions=[0],allowed_hashes=['']):
    # Check the genesis block:
    if (not 'version' in block) or\
       (not block['version'] in allowed_versions):

        return False

    elif (not 'prev_hash' in block) or\
         (not block['prev_hash'] in allowed_hashes):

        return False

    elif (not 'payload' in block) or\
         (not isinstance(block['payload'],dict)) or\
         (('chat' in block['payload']) and (not isinstance(block['payload']['chat'],str))):

        return False

    return True
