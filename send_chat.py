from blockchain_utilities import http_get, http_post, build_block
if not __name__ == "__main__":
    URL = 'http://cat:5000'

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
    msg = 'The FitnessGram™ Pacer Test is a multistage aerobic capacity test that progressively gets more difficult as it continues. The 20 meter pacer test will begin in 30 seconds. Line up at the start. The running speed starts slowly, but gets faster each minute after you hear this signal. [beep] A single lap should be completed each time you hear this sound. [ding] Remember to run in a straight line, and run as long as possible. The second time you fail to complete a lap before the sound, your test is over. The test will begin on the word start. On your mark, get ready, start.'
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
