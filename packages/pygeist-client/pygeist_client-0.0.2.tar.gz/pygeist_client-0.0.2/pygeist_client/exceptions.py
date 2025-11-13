class ZeitgeistClientException(Exception):
    pass

class FailedConnection(ZeitgeistClientException):
    pass

class NotConnected(ZeitgeistClientException):
    pass

class InternalZeitgeistClientException(ZeitgeistClientException):
    pass

class FailedResponseProcess(InternalZeitgeistClientException):
    pass
