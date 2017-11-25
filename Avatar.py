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

    def logout(self):
        pass
