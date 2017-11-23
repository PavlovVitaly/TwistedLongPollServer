from datetime import datetime


class Event(object):
    def __init__(self, description_of_event):
        self.__timestamp = datetime.now()
        self.__description_of_event = description_of_event

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def description_of_event(self):
        return self.__description_of_event
