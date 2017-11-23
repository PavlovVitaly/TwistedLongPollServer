class Client(object):
    def __init__(self, login):
        self.__login = login
        self.__events = list()

    @property
    def login(self):
        return self.__login

    @property
    def events(self):
        return self.__events

    def add_event(self, event):
        self.__events.append(event)

    def is_eq_login(self, login):
        return self.login == login
