#########################################################################################
####################################  NETWORK ERRORS  ###################################
#########################################################################################
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
