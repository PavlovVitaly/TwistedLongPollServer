from twisted.cred import portal
from twisted.internet import reactor, endpoints, task, threads

from ClientsCash import ClientsCash
from Database import UsersDatabase
from DbChecker import DBCredentialsChecker
from Dispatcher import DispatcherFactory
from Event import Event
from EventGenerator import generate_event
from Realm import Realm

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

MAX_NUMBERS_PORTS = LAST_PORT - DISPATCHER_PORT

LENGTH_OF_PASSWORD = 15

SQLITE3 = "sqlite3"
DATABASE_NAME = "users.db"

realm = Realm()
myPortal = portal.Portal(realm)
db = UsersDatabase(SQLITE3, DATABASE_NAME)
dbpool = db.database_pool


def start_server(list_of_logins):
    clients_cash = ClientsCash(list_of_logins)
    checker = DBCredentialsChecker(dbpool.runQuery, query="SELECT login, password FROM clients WHERE login = ?")
    myPortal.registerChecker(checker)
    endpoints.serverFromString(reactor, "tcp:" + str(DISPATCHER_PORT)).listen(DispatcherFactory(myPortal, clients_cash, db))

    def looping_event_generator():
        generate_event(clients_cash)

    l = task.LoopingCall(looping_event_generator)
    l.start(1.0)

    server = clients_cash.client('SERVER')

    def generate_server_event():
        while True:
            msg = input()
            server.add_event(Event('SERVER: ' + msg))

    threads.deferToThread(generate_server_event)

d = db.get_all_logins()
d.addCallback(start_server)
d.addErrback(print)

reactor.suggestThreadPoolSize(MAX_NUMBERS_PORTS)
reactor.run()

# from datetime import datetime
#
# a = datetime.now()
# print(a, type(a))
# b = str(a)
# print(b, type(b))
# d = datetime.strptime(b, '%Y-%m-%d %H:%M:%S.%f')
# print(d, type(d))
