# Written by Daniel Edmond
# And Everett Stenberg


#########################################################################################
#######################################  IMPORTS  #######################################
#########################################################################################
from BlockchainErrors import *
import json
import requests
from os import mkdir, listdir
import sys
from Toolchain import terminal
import hashlib
import nacl.signing
#########################################################################################
############################ FUNCTIONS FOR PROCESSING BLOCKS ############################
#########################################################################################

# hash function wrapper
def sha_256_hash(bytes):
    hasher = hashlib.sha3_256()
    hasher.update(bytes)
    digest = hasher.digest()
    return digest.hex()

# Make a request to where the head hash should be
def retrieve_head_hash(host="cat",port="5000",timeout=3):
    url = f"http://{host}:{port}/head"

    try:
        return requests.get(url,timeout=timeout).content.decode()

    except requests.exceptions.Timeout:
        raise ConnectionException(f"{Color.RED}Error: timeout requesting response from {url}")
    except requests.exceptions.RequestException:
        raise ConnectionException(f"{Color.RED}{Color.BOLD}Error: something went wrong connecting to {url}{Color.END}")
    except requests.exceptions.ConnectionError:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")

# Convert JSON representation of a block to python dictionary representation of a block
def JSON_to_block(JSON_text):
    try:
        return json.loads(JSON_text)
    except JSONDecodeError:
        raise DecodeException(f"{Color.RED} json.dumpsding JSON: '{JSON_text[:50]}' as block{Color.END}")

# Convert python dictionary representation of a block to JSON representation of a block
def block_to_JSON(block):
    return json.dumps(block)

# Takes a hash and makes a request to the given URL to return the block with that hash
def retrieve_block(hash_decoded,host="cat",port="5000",timeout=3):
    url = f"http://{host}:{port}/fetch/{hash_decoded}"
    try:
        return requests.get(url,timeout=timeout).content.decode()
    except requests.exceptions.Timeout:
        raise ConnectionException(f"{Color.RED}Error: timeout requesting response from {url}{Color.END}")
    except requests.exceptions.RequestException:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")
    except requests.exceptions.ConnectionError:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")

# Wrapper function for post
def http_post(host,port,payload,timeout=2):
    try:
        url = f"http://{host}:{port}/push"
        return requests.post(url,data=payload,timeout=timeout)
    except requests.Timeout:
        raise ConnectionException(f"{Color.RED}error: timeout requesting response from {url}")
    except requests.RequestException:
        raise ConnectionException(f"{Color.RED}Error: something went wrong connecting to {url}{Color.END}")

# builds a block given the three fields and returns as JSON
def build_block(prev_hash,payload,ver):
    new_block = {   'prev_hash'     : prev_hash,
                    'payload'       : payload,
                    'version'       : ver}
    if ver == 1:
        new_block['nonce'] = 0
        new_block = mine_block(new_block)

    try:
        encoded_block = json.dumps(new_block)
        return encoded_block
    except JSONEncodeException as j:
        raise BlockCreationException(j)

# returns a list of all the allowed hashes
def grab_cached_hashes(cache_location='cache',version=0):
    allowed_hashes = ['']

    for fname in listdir(cache_location):

        fname               = fname.strip()
        block_hash          = fname.split('.')[0]
        block_ext           = fname.split('.')[-1]
        block_dictionary    = json.loads(open(f"{cache_location}/{fname}",'r').read())

        if version == 0:
            if not block_hash == 'current' and block_dictionary['version'] == 1:
                continue

        if not block_hash == 'current' and block_ext == 'json':
            allowed_hashes.append(block_hash)

    return allowed_hashes

# find chain length from a hash
def iter_local_chain(block_hash,version=0):
    length = 0

    while not block_hash == '':
        length += 1
        filename = f"cache/{block_hash}.json"
        with open(filename,'r') as file:
            block_as_JSON = file.read()
            block = JSON_to_block(block_as_JSON)
            block_hash = block['prev_hash']
            if version == 1 and not block['version'] == 1:
                return length

    return length

# given a processed block (python dictionary), check the block for keys, then check
# key values using the named parameters
def check_fields(block,allowed_versions=[0],allowed_hashes=[''],trust=False):
    if trust:
        return True

    if not 'version' in block:
        raise BlockChainVerifyError("missing version")

    if not block['version'] in allowed_versions:
        raise BlockChainVerifyError(f"bad version-{block['version']} need {allowed_versions}")

    if not 'prev_hash' in block:
        raise BlockChainVerifyError("missing prev_hash")

    if not block['prev_hash'] in allowed_hashes:
        raise BlockChainVerifyError(f"{block['prev_hash']} not in hashes")

    if not 'payload' in block:
        raise BlockChainVerifyError("missing payload")

    if not isinstance(block['payload'],dict):
        raise BlockChainVerifyError(f"payload needs to be dict, is {type(block['payload'])}")

    if 'chat' in block['payload'] and not isinstance(block['payload']['chat'], str):
        raise BlockChainVerifyError(f"payload of 'chat' must be str, is {type(block['payload'])}")

    # Ensure block length req is met <= 1KB
    if len(block_to_JSON(block)) > 1024:
        raise BlockChainVerifyError(f"bad len: {len(block_to_JSON(block))}")

    # Make all V1 checks
    if (block['version'] == 1):
        
        # Check for nonce 
        if (not 'nonce' in block):
            raise BlockChainVerifyError("nonce not in block")
        
        # Check for correct difficulty
        block_hash = sha_256_hash(json.dumps(block).encode())
        if (not block_hash[:6] == '000000'):
            raise BlockChainVerifyError(f"hash not correct: '{block_hash}' ")
        
        # Check for chatid
        if (not "chatid" in block['payload']):
            raise BlockChainVerifyError(f"chatid not in block")
        
        # Check for chatsig
        if (not "chatsig" in block['payload']):
            raise BlockChainVerifyError(f"chatsig not in block")
    
    # Check signatures of any blocks with a chatid 
    if ("chatid" in block['payload']  and "chatsig" in block['payload']):
        # Check if signature verifies 
        key_hex = nacl.signing.SigningKey(block['payload']['chatid'])
        signature = block['payload']['chatsig']
        input(f"checking key {key_hex}\nagainst sig {signature}")
        v_key = nacl.signing.VerifyKey(key_hex)
        try:
            v_key.verify(json.dumps(block), signature)
        except nacl.exceptions.BadSignatureError:
            raise BlockChainVerifyError("signature was not accepted")
    else:
        input("not found in block")
    return True

# Sends a block containing 'msg' to 'host' on 'port'
def send_chat(msg,host,port,version=0):
    #Specify all the URLs
    URL = { 'head' : f"http://{host}:{port}/head",
            'push' : f"http://{host}:{port}/push"}

    # Grab the current head hash
    head_hash = requests.get(URL['head']).content.decode()
    print(f"host {host} is broadcasting head: {head_hash}")
    # Create the block
    json_encoded_block = build_block(head_hash,{'chat' : msg},version)

    # Build format to send over HTTP
    push_data = {'block' : json_encoded_block}

    # Send it
    terminal.printc(f"\tSending block to {host}",terminal.TAN)
    try:
        post = http_post(host,5002,push_data)
        if post.status_code == 200:
            terminal.printc(f"\tBlock sent successfully",terminal.GREEN)
        else:
            terminal.printc(f"\tCode recieved: {post} of type {type(post)}",terminal.TAN)
    except TypeError as t:
        terminal.printc(t,terminal.RED)
        terminal.printc(f"\tRecieved Null response...",terminal.TAN)


def mine_block(block):
    block_hash = '111111'
    while not block_hash[:6] == '000000':
        block['nonce'] += 1
        block_hash  = sha_256_hash(block_to_JSON(block).encode())
    input(f"found block {block}")
    input(f"kicking back block with hash {sha_256_hash(block_to_JSON(block).encode())}")
    return block
