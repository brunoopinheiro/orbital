from typing import List

from orbital.abstract.observable import AbstractObservable
from orbital.abstract.observer import Observer


class Observable(AbstractObservable):

    def __init__(
        self,
        subscribers: List[Observer] = [],
    ) -> None:
        self._subscribers = subscribers

    def subscribe(self, subscriber: Observer) -> None:
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: Observer) -> None:
        self._subscribers.remove(subscriber)

    def notify_subscribers(self, message: str) -> None:
        for subscriber in self._subscribers:
            subscriber.update(message)
