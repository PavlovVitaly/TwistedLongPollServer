import pickle

from twisted.internet import protocol

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

EVENT_MSG_HEAD = 'event'
CASHED_EVENTS_MSG_HEAD = 'cashed_events'


class LongPollConnection(protocol.Protocol):
    def __init__(self, client_avatar, long_poll_get):
        self.__client_avatar = client_avatar
        self.__long_poll_get = long_poll_get

    def dataReceived(self, data):
        request = pickle.loads(data)
        if request.get('key') != self.__long_poll_get.get('key'):
            self.transport.loseConnection()
            return
        self.__client_avatar.ts = request.get('ts')
        self.__client_avatar.client.add_callback_for_add_event(self.__transmit_event)
        self.__client_avatar.server.add_callback_for_add_event(self.__transmit_event)
        self.__transmit_cashed_events()

    def __transmit_event(self, event):
        request = self.__make_msg_from_event(event)
        self.transport.write(request)

    def __make_msg_from_event(self, event):
        msg = list()
        msg.append(EVENT_MSG_HEAD)
        msg.append(event)
        return pickle.dumps(msg)

    def __transmit_cashed_events(self):
        client_events = self.__client_avatar.client.get_events_after(self.__client_avatar.ts)
        server_events = self.__client_avatar.server.get_events_after(self.__client_avatar.ts)
        events = client_events + server_events
        if events is None:
            return
        # events = events.sort()
        request = self.__make_msg_cashed_events(events)
        self.transport.write(request)

    def __make_msg_cashed_events(self, events):
        msg = list()
        msg.append(CASHED_EVENTS_MSG_HEAD)
        msg.append(events)
        return pickle.dumps(msg)


class LongPollConnectionFactory(protocol.Factory):
    def __init__(self, client_avatar, key, ts):
        self.__client_avatar = client_avatar
        self.__long_poll_get = {'key': key, 'ts': ts}

    def buildProtocol(self, addr):
        return LongPollConnection(self.__client_avatar, self.__long_poll_get)
