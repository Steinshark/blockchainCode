#########################################################################################
####################################  NETWORK ERRORS  ###################################
#########################################################################################
class Color:
    self.HEADER = '\033[95m'
    self.OKBLUE = '\033[94m'
    self.OKCYAN = '\033[96m'
    self.OKGREEN = '\033[92m'
    self.WARNING = '\033[93m'
    self.FAIL = '\033[91m'
    self.ENDC = '\033[0m'
    self.BOLD = '\033[1m'
    self.UNDERLINE = '\033[4m'

    
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
