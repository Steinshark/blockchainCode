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
