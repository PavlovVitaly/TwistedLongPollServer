from zope.interface import Interface, implementer


class IProtocolAvatar(Interface):
    def logout():
        """
        Clean up per-login resources allocated to this avatar.
        """


@implementer(IProtocolAvatar)
class EchoAvatar(object):
    def logout(self):
        pass
