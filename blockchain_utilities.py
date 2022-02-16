from hashlib import sha256, sha3_256
from json import loads, dumps
from requests import get, post

# hash functions initialized here
HASHER = {  'SHA256'    : sha256(),
            'SHA3_256'  : sha3_256()}

# imports a JSON file or text to dictionary
def import_JSON_dict(json_fname,format):
    json_text = json_fname
    if format == 'file':
        json_text = open(json_fname).read()
    return loads(json_text)

# converts a block to JSON format
def block_to_JSON(block):
    return dumps(block)

# hash function wrapper
def hash(alg,format,bytes):
    HASHER[alg].update(bytes)
    digest = HASHER[alg].digest()
    if format == 'hex':
        return digest.hex()
    elif format == 'bytes':
        return digest

# Wrapper function for get
def http_get(url):
    return get(url)

# Wrapper function for post
def http_post(url,payload):
    return post(url,payload)

# builds a block given the three fields and returns as JSON
def build_block(prev_hash,payload,ver):
    new_block = {   'prev_hash'     : prev_hash,
                    'payload'       : payload,
                    'version'       : ver}
    return block_to_JSON(new_block)
