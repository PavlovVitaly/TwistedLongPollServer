import random
from Event import Event


EVENTS = ('Event code 0',
          'Event code 1',
          'Event code 2',
          'Event code 3',
          'Event code 4',
          'Event code 5',
          'Event code 6',
          'Event code 7',
          'Event code 8',
          'Event code 9')


def generate_event(clients_cash):
    desc_of_event = EVENTS[random.randint(0, len(EVENTS)-1)]
    num_of_client = random.randint(0, len(clients_cash)-1)
    if clients_cash[num_of_client].login == 'SERVER':
        desc_of_event = 'SERVER: ' + desc_of_event
    clients_cash[num_of_client].add_event(Event(desc_of_event))


if __name__ == '__main__':
    from ClientsCash import ClientsCash
    c = ClientsCash(('SERVER', 'a', 'b', 'c'))
    for i in range(10):
        generate_event(c)
    for client in c:
        print(client.login)
        for event in client.events:
            print(event.timestamp, event.description_of_event)
