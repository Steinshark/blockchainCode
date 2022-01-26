#########################################################################################
###############################  ERROR MESSAGE FORMATTING  ##############################
#########################################################################################
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'
    TAN = '\033[93m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



#########################################################################################
####################################  NETWORK ERRORS  ###################################
#########################################################################################
class ConnectionException(Exception):
    def __init__(self,msg):
        l = super()
        l.__init__(msg)



#########################################################################################
################################  BLOCK FUNCTION ERRORS  ################################
#########################################################################################
class DecodeException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class HashRetrievalException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class JSONEncodeException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class BlockCreationException(Exception):
    def __init__(self,msg):
        super().__init__(msg)


#########################################################################################
###################################  BLOCKCHAIN ERRORS  #################################
#########################################################################################
class BlockChainError(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class BlockChainVerifyError(BlockChainError):
    def __init__(self,msg):
        super().__init__(msg)

class BlockChainRetrievalError(BlockChainError):
    def __init__(self,msg):
        super().__init__(msg)
