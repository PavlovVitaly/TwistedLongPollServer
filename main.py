from twisted.cred import checkers, portal
from twisted.internet import reactor, endpoints

from Dispatcher import DispatcherFactory, Realm

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

LENGTH_OF_PASSWORD = 15

realm = Realm()
myPortal = portal.Portal(realm)
checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
checker.addUser("user", "pass")
myPortal.registerChecker(checker)
endpoints.serverFromString(reactor, "tcp:" + str(DISPATCHER_PORT)).listen(DispatcherFactory(myPortal))
reactor.run()
