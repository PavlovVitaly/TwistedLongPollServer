from twisted.cred import portal
from zope.interface import implementer

from Avatar import IProtocolAvatar, ClientAvatar


@implementer(portal.IRealm)
class Realm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IProtocolAvatar in interfaces:
            avatar = ClientAvatar()
            return IProtocolAvatar, avatar, avatar.logout
        raise NotImplementedError("This realm only supports the IProtocolAvatar interface.")
