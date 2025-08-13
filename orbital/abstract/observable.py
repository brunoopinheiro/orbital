from abc import ABC, abstractmethod

from orbital.abstract.observer import Observer


class AbstractObservable(ABC):
    @abstractmethod
    def subscribe(self, subscriber: Observer) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: Observer) -> None:
        pass

    @abstractmethod
    def notify_subscribers(self, message: str) -> None:
        pass
