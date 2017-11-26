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
SUCCESSFUL_REGISTRATION_RESPONSE_MSG_HEAD = 'successful_registration'
FAILURE_REGISTRATION_RESPONSE_MSG_HEAD = 'failure_registration'
AUTHENTICATION_IS_FAULT_MSG_HEAD = 'error'
AUTHENTICATION_IS_FAULT_MSG = 'authentication is fault'


class Dispatcher(protocol.Protocol):
    def __init__(self, clients_cash, db):
        self.__unavailable_address = (DISPATCHER_ADDRESS,)
        self.__portal = None
        self.__avatar = None
        self.__logout = None
        self.__login = None
        self.__clients_cash = clients_cash
        self.__server = clients_cash.client('SERVER')
        self.__clients_db = db

    def set_portal(self, portal):
        self.__portal = portal

    def connectionMade(self):
        pass

    def dataReceived(self, data):
        if not self.__avatar:
            data = unpack_request_to_dict(data)
            if data[0] == 'login':
                self.__start_authentication(data[1])
            elif data[0] == 'register':
                self.__try_register(data[1])
            else:
                self.connectionLost()

    def __start_authentication(self, data):
        login, password = data.get('login'), data.get('password')
        self.__login = login
        self.tryLogin(login, password)

    def tryLogin(self, username, password):
        d = self.__portal.login(credentials.UsernameHashedPassword(username, password), None, IProtocolAvatar)
        d.addCallbacks(self._cbLogin, self._ebLogin)

    def _cbLogin(self, interface_avatar_logout):
        _, self.__avatar, self.__logout = interface_avatar_logout
        response, port = self.__make_get_response()
        self.__avatar.client = self.__clients_cash.client(self.__login)
        self.__avatar.server = self.__server
        endpoints.serverFromString(reactor, "tcp:" + str(port)).listen(
            LongPollConnectionFactory(self.__avatar, response[1].get('key'), response[1].get('ts')))
        self.transport.write(pickle.dumps(response))
        self.connectionLost(None)

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

    def __try_register(self, data):
        login, password = data.get('login'), data.get('password')
        self.__login = login
        d = self.__clients_db.insert_clients(((login, password),))
        d.addCallbacks(self._cbRegister, self._ebRegister)

    def _cbRegister(self, data):
        response = self.__make_success_registration_response()
        self.__clients_cash.add_client(Client(self.__login))
        self.transport.write(pickle.dumps(response))
        self.connectionLost(None)

    def __make_success_registration_response(self):
        response = list()
        response.append(SUCCESSFUL_REGISTRATION_RESPONSE_MSG_HEAD)
        result_dict = dict()
        response.append(result_dict)
        return response

    def _ebRegister(self, failure):
        response = self.__make_failure_registration_response()
        self.transport.write(pickle.dumps(response))
        self.connectionLost(None)

    def __make_failure_registration_response(self):
        response = list()
        response.append(FAILURE_REGISTRATION_RESPONSE_MSG_HEAD)
        result_dict = dict()
        response.append(result_dict)
        return response

    def connectionLost(self, reason):
        if self.__logout:
            self.__logout()
            self.__avatar = None
            self.__logout = None
            self.__login = None


class DispatcherFactory(protocol.Factory):
    def __init__(self, portal, clients_cash, db):
        self.__portal = portal
        self.__proto = None
        self.__clients_cash = clients_cash
        self.__clients_db = db

    def buildProtocol(self, addr):
        self.__proto = Dispatcher(self.__clients_cash, self.__clients_db)
        self.__proto.set_portal(self.__portal)
        return self.__proto
