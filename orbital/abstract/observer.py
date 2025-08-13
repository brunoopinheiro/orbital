from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, message: str) -> None:
        """Update the subscriber with a message.

        Args:
            message (str): The message to update the subscriber with.
        """
        raise NotImplementedError('Subscriber.update() not implemented')
