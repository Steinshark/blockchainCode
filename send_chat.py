from blockchain_utilities import http_get, http_post, build_block


if not __name__ == "__main__":
    URL = 'http://lion:5002'

    # Get user message
    message = input("message: ")

    # Get the head blocks hash
    request_url = URL+'/head'
    head_hash = http_get(request_url).content

    # Build a new block and send it to the blockchain
    json_encoded_block = build_block(head_hash.decode(),{'chat' : message},0)
    push_data = {'block' : json_encoded_block}
    post = http_post(URL+'/push',push_data)
    print(post.status_code)


else:
    import textwrap
    msg = 'hello world'
    sends = textwrap.wrap(msg, 50)


    URL = 'http://cat:5000'

    # Get user message
    for m in sends:
        message = m

        # Get the head blocks hash
        request_url = URL+'/head'
        head_hash = http_get(request_url).content

        # Build a new block and send it to the blockchain
        json_encoded_block = build_block(head_hash.decode(),{'chat' : message},0)
        push_data = {'block' : json_encoded_block}
        post = http_post(URL+'/push',push_data)
        print(post.status_code)
