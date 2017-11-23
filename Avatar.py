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

    @property
    def client(self):
        return self.__client

    @client.setter
    def client(self, cl):
        self.__client = cl

    def logout(self):
        pass
