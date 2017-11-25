from zope.interface import Interface, implementer


class IProtocolAvatar(Interface):
    def logout(self):
        """
        Clean up per-login resources allocated to this avatar.
        """


@implementer(IProtocolAvatar)
class ClientAvatar(object):
    def __init__(self):
        super().__init__()
        self.__client = None
        self.__server = None
        self.__ts = None

    @property
    def client(self):
        return self.__client

    @client.setter
    def client(self, cl):
        self.__client = cl

    @property
    def server(self):
        return self.__server

    @server.setter
    def server(self, sr):
        self.__server = sr

    @property
    def ts(self):
        return self.__ts

    @ts.setter
    def ts(self, ts):
        self.__ts = ts

    def logout(self):
        pass
