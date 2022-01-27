import flask
from collections import OrderedDict
from BlockTools import build_block
from BlockchainUtilities import hash

class Server:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.blocks = OrderedDict()


    # Maps a block hash to the block itself

    @app.route('/head')
    def head():
        return list(self.blocks.values())[-1]

    @app.route('/fetch/<digest>')
    def fetch(digest):
        try:
            return self.blocks[digest]

        except KeyError:
            # HTTP code 400 indicates a bad request error
            return 'hash digest not found', 400

    @app.route('/<command>')
    def maintain(command):
        # Grab the commands
        arguments = [c.strip() for c in command.split(" ")]

        # Allow for block addition
        if arguments[0] == "add":
            if arguments[1] == "block":
                block = arguments[2]
                block_hash = hash('hex',block.encode())
                self.blocks[block_hash] = block

        # Allow for block removal
        elif arguments[0] == "remove":
            if arguments[1] == "head":
                self.blocks.popitem()

        # Error case
        else:
            return f'command {command} not understood by server', 269




    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=1234)