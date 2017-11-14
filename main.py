from twisted.internet import reactor, endpoints, protocol
from twisted.web import server, resource
import random
from generator_of_password import password_generator

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

LENGTH_OF_PASSWORD = 15


class Dispatcher(protocol.Protocol):
    def __init__(self):
        self.__unavailable_address = (DISPATCHER_ADDRESS,)

    def connectionMade(self):
        result_dict = dict()
        result_dict['server'], port = self.__generate_available_address()
        result_dict['key'] = str(next(password_generator(LENGTH_OF_PASSWORD)))
        result_dict['ts'] = '0'
        endpoints.serverFromString(reactor, "tcp:" + str(port)).listen(DispatcherFactory())     # todo: Заменить на long poll port
        self.transport.write(str(result_dict).encode("ascii"))

    def __generate_available_address(self):
        port = random.randint(DISPATCHER_PORT+1, LAST_PORT)
        address = DISPATCHER_IP + ':' + str(port)
        while address in self.__unavailable_address:
            port = random.randint(DISPATCHER_PORT + 1, LAST_PORT)
            address = DISPATCHER_IP + ':' + str(port)
        return address, port


class DispatcherFactory(protocol.Factory):
    # todo: сделать синглетоном
    def buildProtocol(self, addr):
        return Dispatcher()

endpoints.serverFromString(reactor, "tcp:"+str(DISPATCHER_PORT)).listen(DispatcherFactory())
reactor.run()
