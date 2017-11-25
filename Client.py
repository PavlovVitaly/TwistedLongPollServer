from Event import Event
from datetime import datetime


class Client(object):
    def __init__(self, login):
        self.__login = login
        self.__events = list()
        self.__add_event_callback = list()

    @property
    def login(self):
        return self.__login

    @property
    def events(self):
        return self.__events

    def add_callback_for_add_event(self, callback):
        self.__add_event_callback.append(callback)
        return self.__add_event_callback.index(callback)

    def pop_callback_for_add_event(self, id):
        self.__add_event_callback.pop(id)

    def add_event(self, event):
        self.__events.append(event)
        for callback in self.__add_event_callback:
            callback(event)

    def is_eq_login(self, login):
        return self.__login == login

    def get_events_after(self, event_ts):
        input_event = Event('')
        input_event.timestamp = datetime.strptime(event_ts, '%Y-%m-%d %H:%M:%S.%f')
        ret_events = list()
        if len(self.events) > 0:
            last_event = max(self.events)
            for event in self.events:
                if (input_event <= event) and (last_event >= event):
                    ret_events.append(event)
        return ret_events
