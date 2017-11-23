from twisted.cred import portal
from twisted.internet import reactor, endpoints

from ClientsCash import ClientsCash
from Database import UsersDatabase
from DbChecker import DBCredentialsChecker
from Dispatcher import DispatcherFactory
from Realm import Realm

DISPATCHER_IP = 'http://127.0.0.1'
DISPATCHER_PORT = 8000
DISPATCHER_ADDRESS = DISPATCHER_IP + ':' + str(DISPATCHER_PORT)

LAST_PORT = 65000

LENGTH_OF_PASSWORD = 15

SQLITE3 = "sqlite3"
DATABASE_NAME = "users.db"

realm = Realm()
myPortal = portal.Portal(realm)
db = UsersDatabase(SQLITE3, DATABASE_NAME)
dbpool = db.database_pool
list_of_logins = None


# todo: list_of_logins isn't connected.
def fill_list_of_logins(x):
    list_of_logins = x


db.get_all_logins().addCallback(fill_list_of_logins)
while not list_of_logins:
    pass
clients_cash = ClientsCash(list_of_logins)
checker = DBCredentialsChecker(dbpool.runQuery, query="SELECT login, password FROM clients WHERE login = ?")
myPortal.registerChecker(checker)
endpoints.serverFromString(reactor, "tcp:" + str(DISPATCHER_PORT)).listen(DispatcherFactory(myPortal))
reactor.run()

# from datetime import datetime
#
# a = datetime.now()
# print(a, type(a))
# b = str(a)
# print(b, type(b))
# d = datetime.strptime(b, '%Y-%m-%d %H:%M:%S.%f')
# print(d, type(d))
