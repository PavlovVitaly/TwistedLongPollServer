import pickle

from twisted.internet import protocol

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

EVENT_MSG_HEAD = 'event'


class LongPollConnection(protocol.Protocol):
    def __init__(self, client_avatar, long_poll_get):
        self.__client_avatar = client_avatar
        self.__long_poll_get = long_poll_get

    def dataReceived(self, data):
        request = pickle.loads(data)
        if request.get('key') != self.__long_poll_get.get('key'):
            self.transport.loseConnection()
            return
        self.__client_avatar.client.add_callback_for_add_event(self.__transmit_event)
        self.__client_avatar.server.add_callback_for_add_event(self.__transmit_event)

    def __transmit_event(self, event):
        request = self.__make_msg_from_event(event)
        self.transport.write(request)

    def __make_msg_from_event(self, event):
        msg = list()
        msg.append(EVENT_MSG_HEAD)
        result_dict = dict()
        result_dict['ts'] = event.timestamp
        result_dict['description'] = event.description_of_event
        msg.append(result_dict)
        return pickle.dumps(msg)


class LongPollConnectionFactory(protocol.Factory):
    def __init__(self, client_avatar, key, ts):
        self.__client_avatar = client_avatar
        self.__long_poll_get = {'key': key, 'ts': ts}

    def buildProtocol(self, addr):
        return LongPollConnection(self.__client_avatar, self.__long_poll_get)
