
RESPONSE_OK = "OK"
RESPONSE_BAD_REQUEST = "Bad Request"
RESPONSE_NOT_FOUND = "Not Found"
RESPONSE_NOT_SUPPORTED = "P2P-CI Version Not Supported"


def getResponsePhrase(status):
    if(status==200):
        return RESPONSE_OK
    elif(status==404):
        return RESPONSE_NOT_FOUND
    elif(status==505):
        return RESPONSE_NOT_SUPPORTED
    else:
        return RESPONSE_BAD_REQUEST