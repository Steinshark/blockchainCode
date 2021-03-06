import os
import sys
import nacl.signing 

try:
    filename = sys.argv[1]
except IndexError:
    print(f"usage: keygen.py filename")
    exit()

# Create file if not exists 
if not os.path.isfile(filename):
    print(f"Generating key")
    key = nacl.signing.SigningKey.generate()
    hex_priv_key = key.encode().hex()
    hex_pub_key  = key.verify_key.encode().hex()
    with open(filename,'w') as file:
        file.write(hex_priv_key)
    print(hex_pub_key)
else:
    with open(filename,'r') as file:
        priv_key = file.read()
        hex_pub_key = nacl.signing.SigningKey(bytes.fromhex(priv_key)).verify_key.encode().hex()
        print(hex_pub_key)
