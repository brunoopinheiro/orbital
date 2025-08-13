import pytest

from orbital.abstract.observer import Observer


@pytest.fixture
def concrete_observer() -> type[Observer]:
    class ConcreteObserver(Observer):

        def update(self, message: str) -> None:  # noqa
            print(message)

    return ConcreteObserver
