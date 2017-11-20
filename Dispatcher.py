import pickle
import random

from twisted.cred import credentials, portal
from twisted.internet import reactor, endpoints, protocol
from zope.interface import implementer

from Avatar import IProtocolAvatar, EchoAvatar
from LongPollConnection import LongPollConnectionFactory
from Packman import unpack_request_to_dict
from generator_of_password import password_generator

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

LENGTH_OF_PASSWORD = 15



class Dispatcher(protocol.Protocol):
    def __init__(self):
        self.__unavailable_address = (DISPATCHER_ADDRESS,)
        self.__portal = None
        self.__avatar = None
        self.__logout = None

    def set_portal(self, portal):
        self.__portal = portal

    def connectionMade(self):
        pass

    def dataReceived(self, data):
        if not self.__avatar:
            data = unpack_request_to_dict(data)
            login, password = data.get('login'), data.get('password')
            self.tryLogin(login, password)

    def tryLogin(self, username, password):
        d = self.__portal.login(credentials.UsernamePassword(username, password), None, IProtocolAvatar)
        d.addCallbacks(self._cbLogin, self._ebLogin)
        d.addErrback(print)

    def _cbLogin(self, interface_avatar_logout):
        _, self.__avatar, self.__logout = interface_avatar_logout
        result_dict = dict()
        result_dict['server'], port = self.__generate_available_address()
        result_dict['key'] = str(next(password_generator(LENGTH_OF_PASSWORD)))
        result_dict['ts'] = '0'
        endpoints.serverFromString(reactor, "tcp:" + str(port)).listen(
            LongPollConnectionFactory(result_dict.get('key'), result_dict.get('ts')))
        self.transport.write(pickle.dumps(result_dict))

    def _ebLogin(self, failure):
        self.transport.write(pickle.dumps({'msg': 'Error'}))
        self.transport.loseConnection()

    def __generate_available_address(self):
        port = random.randint(DISPATCHER_PORT + 1, LAST_PORT)
        address = DISPATCHER_IP + ':' + str(port)
        while address in self.__unavailable_address:
            port = random.randint(DISPATCHER_PORT + 1, LAST_PORT)
            address = DISPATCHER_IP + ':' + str(port)
        return address, port

    def connectionLost(self, reason):
        if self.__logout:
            self.__logout()
            self.__avatar = None
            self.__logout = None


class DispatcherFactory(protocol.Factory):
    def __init__(self, portal):
        self.portal = portal
        self.proto = None

    def buildProtocol(self, addr):
        self.proto = Dispatcher()
        self.proto.set_portal(self.portal)
        return self.proto


@implementer(portal.IRealm)
class Realm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IProtocolAvatar in interfaces:
            avatar = EchoAvatar()
            return IProtocolAvatar, avatar, avatar.logout
        raise NotImplementedError("This realm only supports the IProtocolAvatar interface.")
