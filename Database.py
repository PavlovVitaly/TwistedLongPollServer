from twisted.enterprise import adbapi


class UsersDatabase(object):
    def __init__(self):
        self.__SERVER = 'SERVER'
        self.__SERVER_PASSWORD = 'qwerty'
        self.dbpool = adbapi.ConnectionPool("sqlite3", "users.db", check_same_thread=False)
        self.__create_db_tables()
        self.insert_client(self.SERVER, self.SERVER_PASSWORD)

    def __create_db_tables(self):
        self.dbpool.runQuery("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                             "login TEXT NOT NULL, "
                             "password TEXT NOT NULL)")
        self.dbpool.runQuery("CREATE TABLE IF NOT EXISTS events_log (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                             "ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                             "event_description TEXT NOT NULL, "
                             "client_events INTEGER, "
                             "FOREIGN KEY(client_events) REFERENCES clients(id)))")

    def insert_client(self, login, password):
        if not self.__is_existed_login(login):
            self.dbpool.runQuery("INSERT INTO clients (login, password) VALUES(?, ?)", (login, password))
            return True
        return False

    def insert_event(self, login, ts, event):
        if self.__is_existed_login(login):
            self.dbpool.runQuery("INSERT INTO events_log (ts, event_description, client_events) "
                                 "VALUES(?, ?, (SELECT id FROM clients WHERE login = ?))", (event, ts, login))

    def __is_existed_login(self, login):
        return self.dbpool.runQuery("SELECT login FROM clients WHERE login = ?", (login,))

    def _insert_events(self, transaction, ts_event_login):
        for ts, event, login in ts_event_login:
            transaction.execute("INSERT INTO events_log (ts, event_description, client_events) "
                                "VALUES(?, ?, (SELECT id FROM clients WHERE login = ?))", (event, ts, login))

    def insert_events(self, ts_event_login):
        return self.dbpool.runInteraction(self._insert_events, ts_event_login)

    def get_password(self, login):
        return self.dbpool.runQuery("SELECT password FROM clients WHERE login = ?", (login,))

    def get_client_events(self, login, ts):
        return self.dbpool.runQuery("SELECT e.ts, e.event_description "
                                    "FROM clients AS c LEFT OUTER JOIN events_log AS e ON c.id = e.client_events"
                                    "WHERE (c.login = ? OR c.login = ?) and e.ts > ?"
                                    "ORDER BY e.ts",
                                    (login, self.SERVER, ts))

    def finish(self):
        self.dbpool.close()
