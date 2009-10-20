class Observer:
    def update(self):
        return;

class Subject:
    
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        '''Add a new observer to self'''
        if not observer in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, *args):
        '''Notify all observers and update states'''
        for observer in self._observers:
            observer.update(self, *args)
