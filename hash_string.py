from blockchain_utilities import hash

# asks for one line input and encodes that to bytes
def getString():
    raw_string = input("please enter a single-line message: ")
    string_as_bytes = raw_string.encode()
    return string_as_bytes

# run
if __name__ == '__main__':
    r = getString()
    print(hash('SHA3_256','hex',r))
