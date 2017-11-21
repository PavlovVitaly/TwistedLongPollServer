from twisted.cred import portal
from zope.interface import implementer

from Avatar import IProtocolAvatar, EchoAvatar


@implementer(portal.IRealm)
class Realm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IProtocolAvatar in interfaces:
            avatar = EchoAvatar()
            return IProtocolAvatar, avatar, avatar.logout
        raise NotImplementedError("This realm only supports the IProtocolAvatar interface.")
