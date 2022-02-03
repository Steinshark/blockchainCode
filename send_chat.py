from blockchain_utilities import http_get, http_post, build_block
from json import dumps

if __name__ == "__main__":
    URL = 'http://lion:5002'

    # Get user message
    message = input("message: ")

    # Get the head blocks hash
    request_url = URL+'/head'
    head_hash = http_get(request_url).content

    # Build a new block and send it to the blockchain
    json_encoded_block = build_block(head_hash.decode(),{'chat' : message},0)
    print(f"{type(json_encoded_block)}")
    push_data = {'block' : json_encoded_block}
    print(f"sending {push_data} of type {type(push_data)}")
    post = http_post(URL+'/push',push_data)
    print(post.status_code)
