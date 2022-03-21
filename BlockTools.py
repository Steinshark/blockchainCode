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
import subprocess
import random
from BlockchainUtilities import get_blockchain
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
def http_post(host,port,payload,timeout=5):
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
        return new_block

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

# fetches a block DICT by its hash
def grab_block_by_hash(block_hash):
    with open(f"cache/{block_hash}.json") as file:
        contents = file.read()
        block_dict = json.loads(contents)
        return block_dict

# find chain length from a hash
def iter_local_chain(block_hash,known_chains,version=0):
    length = 0
    seen = []
    i = 0
    while not block_hash == '':
        length += 1
        filename = f"cache/{block_hash}.json"
        if not block_hash in seen:
            seen.append(block_hash)
        else:
            print("found cycle")
            return
        try:
            with open(filename,'r') as file:
                block_string = file.read()
                block_dict = JSON_to_block(block_string)
                block_hash = block_dict['prev_hash']
                if block_hash in known_chains:
                    return known_chains[block_hash] + length
                #if version == 1 and not block_dict['version'] == 1:
                #    return length
        except FileNotFoundError:
            return length
    return length

# given a processed block (python dictionary), check the block for keys, then check
# key values using the named parameters
def check_block(block,block_string,allowed_versions=[0],allowed_hashes=[''],trust=False,diff=6,check_tx=True):
    block_hash = sha_256_hash(block_string.encode())

    if trust:
        return True

    # Ensure all proper fields are in the block
    if not 'version' in block:
        raise BlockChainVerifyError("missing version")
    if not 'payload' in block:
        raise BlockChainVerifyError("missing payload")
    if not block['prev_hash'] in allowed_hashes:
        raise BlockChainVerifyError(f"{block['prev_hash']} not in hashes")
    if not block['version'] in allowed_versions:
        raise BlockChainVerifyError(f"bad version-{block['version']} need {allowed_versions}")
    if not 'prev_hash' in block:
        raise BlockChainVerifyError("missing prev_hash")

    # Ensure all proper fields are in payload
    if not isinstance(block['payload'],dict):
        raise BlockChainVerifyError(f"payload needs to be dict, is {type(block['payload'])}")
    if 'chat' in block['payload'] and not isinstance(block['payload']['chat'], str):
        raise BlockChainVerifyError(f"payload of 'chat' must be str, is {type(block['payload'])}")
    if ("chatid" in block["payload"] and not "chatsig" in block["payload"]):
        raise BlockChainVerifyError("missing chatsig")
    if ("chatsig" in block["payload"] and not "chatid" in block["payload"]):
        raise BlockChainVerifyError("missing chatid")

    # Ensure block length req is met <= 1KB
    if len(block_to_JSON(block)) > 2024:
        raise BlockChainVerifyError(f"bad len: {len(block_to_JSON(block))}")

    # Make all V1 checks
    if (block['version'] == 1):

        # Check nonce and difficulty
        if (not 'nonce' in block):
            raise BlockChainVerifyError("nonce not in block")
        if (not block_hash[:diff] == '000000'):
            raise BlockChainVerifyError(f"hash not correct: '{block_hash}' ")

    # Check transaction fields
    if 'txns' in block['payload'] and check_tx:
        try:
            verify_transaction(block,block_hash)
        except TransactionVerifyError as t:
            raise BlockChainVerifyError(t)

    # Check signatures of any blocks with a chatid
    if ("chatid" in block['payload']  and "chatsig" in block['payload']):
        # Check if signature verifies
        key_hex = block['payload']['chatid']
        sig_hex = block['payload']['chatsig']
        v_key = nacl.signing.VerifyKey(bytes.fromhex(key_hex))
        try:
            message = block["payload"]['chat']
            signature = bytes.fromhex(sig_hex)
            v_key.verify(message.encode(), signature)
        except nacl.exceptions.BadSignatureError:
            print("bad sig")
            raise BlockChainVerifyError("signature was not accepted")

    # Check all
    return True

# Sends a block containing to 'host' on 'port'
def send_block(json_encoded_block,host,port,version=1):

    #Specify all the URLs
    URL = { 'head' : f"http://{host}:{port}/head",
            'push' : f"http://{host}:{port}/push"}

    # Grab the current head hash
    head_hash = requests.get(URL['head']).content.decode()
    print(f"\t{host} is broadcasting head: '{head_hash[:10]}'")

    # Build format to send over HTTP
    push_data = {'block' : json_encoded_block}

    # Send it
    terminal.printc(f"\tSending block to {host}",terminal.TAN)
    try:
        post = http_post(host,port,push_data)
        code = post.status_code
        if post.status_code == 200:
            terminal.printc(f"\tBlock sent successfully",terminal.GREEN)
        else:
            terminal.printc(f"\tCode recieved: {code}",terminal.TAN)
            terminal.printc(f"\tServer said: {post.text}",terminal.TAN)
    except TypeError as t:
        terminal.printc(t,terminal.RED)
        terminal.printc(f"\tRecieved Null response...",terminal.TAN)
    return

# Mine a block to send out to other peers
def mine_block(block):
    block_string = block_to_JSON(block)
    mined_block = subprocess.run(['goatminer','24'],input=block_string,text=True,capture_output=True,check=True).stdout
    return mined_block

# Build the payload for a block
def build_payload(priv_key,txns,ver=None,coinbase_msg='anotha coin for everett',msg ="fake msg"):

    # generate keys
    signing_key = nacl.signing.SigningKey(bytes.fromhex(priv_key))
    public_key  = signing_key.verify_key.encode().hex()

    # Init empty payload
    payload = {'txns': []}

    # Add message if given
    if not msg is None and isinstance(msg,str):
        payload["chat"] = msg



    # Add the coinbase transaction
    coinbase_tj = {}
    coinbase_tj["input"] = sha_256_hash(str(random.randint(-69,420)).encode())
    coinbase_tj["output"] = public_key
    coinbase_tj["message"] = coinbase_msg
    coinbase_tj_json = json.dumps(coinbase_tj)

    coinbase_tx = {"tj":coinbase_tj_json,"sig":"coinbase"}
    payload['txns'].append(coinbase_tx)

    for transaction in txns:
        # Unpack tx values
        tx_input, tx_output, tx_msg = transaction

        # Create tj as dict, then convert to json string
        tj = {"input":tx_input, "output":tx_output, "msg": tx_msg}
        tj_json = json.dumps(tj)

        # Create sig as hex
        tx_sig = signing_key.sign(tj_json.encode()).signature.hex()

        new_transaction = {"tj":tj_json,"sig":tx_sig}
        payload["txns"].append(new_transaction)
    return payload

# Verify transactions on an incoming block
def verify_transaction(block_dict,block_hash):
    prev_hash = block_dict['prev_hash']
    transactions = block_dict['payload']['txns']

    for i, transaction in enumerate(transactions):

        # Ensure transaction is properly promatted
        if not "tj" in transaction or not "sig" in transaction:
            raise TransactionVerifyError(f"Missing tj or sig field in transaction\n{terminal.BLUE}{transaction}{terminal.END}")

        tj_dict = transaction['tj']



        # Ensure tj is formatted properly
        if not "input" in tj_dict or not "output" in tj_dict or not "message" in tj_dict:
            raise TransactionVerifyError(f"Improperly formatted tj field\n{tj_dict}")



        # Check coinbase
        if i == 0:
            if not transaction['sig'] == 'coinbase':
                raise TransactionVerifyError(f"First transaction not coinbase transaction")

        # Ensure the remaining transactions check out
        else:
            try:
                input_token = json.loads(transaction['tj'])['input']
                check_chain(prev_hash,input_token,transaction['sig'],transaction['tj'])
            except TransactionVerifyError as e:
                raise TransactionVerifyError(e)
    return True

# Helper function for 'verify_transaction'
def check_chain(prev_hash,input_token,sig,this_tj):
    found = False

    # Loop through the chain and perform transaction checks
    while not prev_hash == '':
        block_dict = grab_block_by_hash(prev_hash)

        # Ensure the block has transactions
        if 'txns' in block_dict['payload']:

            for this_transaction in block_dict['payload']['txns']:
                tj = this_transaction['tj']
                tj_hash = sha_256_hash(tj.encode())
                tj_dict = json.loads(tj)

                # Check for the corresponding transaction
                if input_token == tj_hash:
                    found = True

                    # Ensure the signature matches
                    try:
                        pub_key = tj_dict['output']
                        v_key = nacl.signing.VerifyKey(bytes.fromhex(pub_key))
                        v_key.verify(this_tj.encode(),bytes.fromhex(sig))
                    except nacl.exceptions.BadSignatureError:
                        raise TransactionVerifyError(f"bad signature\npub_key: {pub_key}\nsig: {sig}")

                # Check that coin is not double spent
                if input_token == tj_dict['input']:
                    raise TransactionVerifyError(f"input {input_token} double spent")


        prev_hash = block_dict['prev_hash']

    # if no coin found, then bad!
    if not found:
        raise TransactionVerifyError(f"no matching transaction for {input_token}")
    else:
        return


def add_transaction(pub_key,address):
    # Grab the current blockchain
    head_hash = json.loads(open("cache/current.json").read())['head']
    all_inputs = []
    all_hashes = []
    hash_candidates = []

    print(f"creating lists\npub_key={pub_key}")
    while not head_hash == '':

        block_dict = json.loads(open(f"cache/{head_hash}.json").read())
        if 'txns' in block_dict['payload']:
            for tx in block_dict['payload']['txns']:

                # Keep track of all hashes
                tj_string = tx['tj']
                if not isinstance(tj_string,str):
                    continue
                all_hashes.append(sha_256_hash(tj_string.encode()))

                # Keep track of all inputs
                tj_dict = json.loads(tj_string)
                all_inputs.append(tj_dict['input'])
                # Find a list of all coins that have ever gone to me
                if tj_dict['output'].strip() == pub_key.strip():
                    hash_candidates.append(all_hashes[-1])
        head_hash = block_dict['prev_hash']
    spendable_hash = None
    for h in hash_candidates:
        if not h in all_inputs:
            spendable_hash = h
            break

    if not spendable_hash is None:
        inp = spendable_hash
        output = address
        msg = "I sent this to myself"
        print(f"returning input as {inp}")
        return (inp, output, msg)
