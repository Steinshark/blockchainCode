from blockchain_utilities import import_JSON_dict, build_block, hash, block_to_JSON

if __name__ == '__main__':
    prev_hash = input('hash digest: ')
    chat_msg = input('chat message: ')

    # make a block encoded in JSON format
    new_json_block = build_block(prev_hash,{'chat' : chat_msg},0)

    # hash the block
    block_hash = hash('SHA3_256','hex',new_json_block.encode())
    print(block_hash)
