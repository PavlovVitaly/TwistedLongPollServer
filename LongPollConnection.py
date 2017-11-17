import pickle

from twisted.internet import protocol

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)


class LongPollConnection(protocol.Protocol):
    def __init__(self, long_poll_get):
        self.__long_poll_get = long_poll_get

    def dataReceived(self, data):
        request = pickle.loads(data)
        if request.get('key') != self.__long_poll_get.get('key'):
            self.transport.loseConnection()
            return
        result_dict = dict()
        result_dict['Goood'] = 'Luck'
        self.transport.write(pickle.dumps(result_dict))


class LongPollConnectionFactory(protocol.Factory):
    def __init__(self, key, ts):
        self.__long_poll_get = {'key': key, 'ts': ts}

    def buildProtocol(self, addr):
        return LongPollConnection(self.__long_poll_get)
