import pickle
import random
from datetime import datetime

from twisted.cred import credentials
from twisted.internet import reactor, endpoints, protocol

from Avatar import IProtocolAvatar
from Client import Client
from LongPollConnection import LongPollConnectionFactory
from Packman import unpack_request_to_dict
from generator_of_password import password_generator

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

LENGTH_OF_PASSWORD = 15

GET_RESPONSE_MSG_HEAD = 'get'
AUTHENTICATION_IS_FAULT_MSG_HEAD = 'error'
AUTHENTICATION_IS_FAULT_MSG = 'authentication is fault'


class Dispatcher(protocol.Protocol):
    def __init__(self, clients_cash):
        self.__unavailable_address = (DISPATCHER_ADDRESS,)
        self.__portal = None
        self.__avatar = None
        self.__logout = None
        self.__login = None
        self.__clients_cash = clients_cash

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
        d = self.__portal.login(credentials.UsernameHashedPassword(username, password), None, IProtocolAvatar)
        d.addCallbacks(self._cbLogin, self._ebLogin)

    def _cbLogin(self, interface_avatar_logout):
        _, self.__avatar, self.__logout = interface_avatar_logout
        response, port = self.__make_get_response()
        self.__avatar.client = Client(self.__login)
        endpoints.serverFromString(reactor, "tcp:" + str(port)).listen(
            LongPollConnectionFactory(self.__avatar, response[1].get('key'), response[1].get('ts')))
        self.transport.write(pickle.dumps(response))

    def __make_get_response(self):
        response = list()
        response.append(GET_RESPONSE_MSG_HEAD)
        result_dict = dict()
        result_dict['server'], port = self.__generate_available_address()
        result_dict['key'] = str(next(password_generator(LENGTH_OF_PASSWORD)))
        result_dict['ts'] = str(datetime.now())
        response.append(result_dict)
        return response, port

    def _ebLogin(self, failure):
        response = self.__make_authentication_is_fault_response()
        self.transport.write(pickle.dumps(response))
        self.transport.loseConnection()

    def __make_authentication_is_fault_response(self):
        response = list()
        response.append(AUTHENTICATION_IS_FAULT_MSG_HEAD)
        result_dict = dict()
        result_dict['msg'] = AUTHENTICATION_IS_FAULT_MSG
        response.append(result_dict)
        return response

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
    def __init__(self, portal, clients_cash):
        self.__portal = portal
        self.__proto = None
        self.__clients_cash = clients_cash

    def buildProtocol(self, addr):
        self.__proto = Dispatcher(self.__clients_cash)
        self.__proto.set_portal(self.__portal)
        return self.__proto
