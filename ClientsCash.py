from Client import Client


class ClientsCash(object):
    def __init__(self, list_of_logins):
        self.__list_of_clients = list()
        for login in list_of_logins:
            self.__list_of_clients.append(Client(login))

    def client(self, login):
        for client in self.__list_of_clients:
            if client.is_eq_login(login):
                return client
        return None

    def __iter__(self):
        return iter(self.__list_of_clients)

    def __getitem__(self, item):
        return self.__list_of_clients[item]

    def __setitem__(self, key, value):
        self.__list_of_clients[key] = value

    def __delitem__(self, key):
        self.__list_of_clients.pop(key)

    def __len__(self):
        return len(self.__list_of_clients)

    def __contains__(self, item):
        for client in self.__list_of_clients:
            if client.is_eq_login(item):
                return True
        return False


if __name__ == '__main__':
    c = ClientsCash(('a', 'b', 'c'))
    for client in c:
        print(client.login)
