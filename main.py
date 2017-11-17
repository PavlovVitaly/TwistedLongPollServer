from twisted.internet import reactor, endpoints

from Dispatcher import DispatcherFactory

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

LENGTH_OF_PASSWORD = 15

endpoints.serverFromString(reactor, "tcp:"+str(DISPATCHER_PORT)).listen(DispatcherFactory())
reactor.run()
