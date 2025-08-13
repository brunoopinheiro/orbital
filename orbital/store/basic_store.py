from copy import deepcopy
from json import dumps
from typing import Any, Callable, Dict, List, TypeAlias

from orbital.abstract.observer import Observer
from orbital.store.observable import Observable

State: TypeAlias = Dict[str, Any]
Reducer: TypeAlias = Callable[[State, str], State]


def combine_reducers(reducers: List[Reducer]) -> Reducer:
    """Combines multiple reducers into a single reducer function.

    Args:
        reducers (List[Reducer]): A list of reducer functions to combine.

    Returns:
        Reducer: A single reducer function that applies all the provided
            reducers.
    """

    def combined(state: State, action: str) -> State:
        callables = [reducer for reducer in reducers if callable(reducer)]
        old_state = deepcopy(state)
        for reducer in callables:
            new_state = reducer(old_state, action)
            if not isinstance(new_state, dict):
                raise ValueError(
                    f"Reducer {reducer} did not return a valid state,"
                    f" when called for {action}."
                )
            old_state.update(new_state)
        return old_state
    return combined


class BasicStore:

    def __init__(
        self,
        reducer: Reducer,
        current_state: State,
    ) -> None:
        self.__reducer = reducer
        self.__current_state = current_state
        self.__notifier = Observable()

    @property
    def current_state(self) -> State:
        current_state = deepcopy(self.__current_state)
        return current_state

    def __check_state_keys(self, new_state: State) -> bool:
        """Checks if the new state contains all keys from the current state.
        Both states must have the same keys for the update to be valid.

        Args:
            new_state (State): The new state to check.

        Returns:
            bool: True if the new state contains all keys from the current
                state, False otherwise.
        """
        curr_state_keys = set(self.current_state.keys())
        new_state_keys = set(new_state.keys())
        all_keys_match = curr_state_keys == new_state_keys
        return all_keys_match

    @property
    def _notifier(self) -> Observable:
        return self.__notifier

    def subscribe(self, subscriber: Observer) -> None:
        """Subscribes an observer to the store.

        Args:
            subscriber (Observer): The observer to subscribe.
        """
        self.__notifier.subscribe(subscriber)

    def unsubscribe(self, subscriber: Observer) -> None:
        """Unsubscribes an observer from the store.

        Args:
            subscriber (Observer): The observer to unsubscribe.
        """
        self.__notifier.unsubscribe(subscriber)

    def notify_subscribers(self, message: str) -> None:
        """Notifies all subscribers about a state change.

        Args:
            message (str): The message to send to subscribers.
        """
        self.__notifier.notify_subscribers(message)

    def get_state(self) -> State:
        """Returns the current state of the store.

        Returns:
            State: The current state of the store.
        """
        return self.current_state

    def __update_state(self, new_state: State) -> 'BasicStore':
        if self.__check_state_keys(new_state) is False:
            raise ValueError(
                'The state must contain all keys from the current state.'
            )
        self.notify_subscribers(dumps(new_state, skipkeys=True))
        return BasicStore(
            reducer=self.__reducer,
            current_state=new_state,
        )

    def dispatch(self, action: str) -> 'BasicStore':
        """
        Dispatches an action to update the store's state.
        The action should be a dictionary with a 'type' key.
        """
        new_state = self.__reducer(self.current_state, action)
        if not isinstance(new_state, dict):
            raise ValueError("Reducer must return a valid state.")

        return self.__update_state(new_state)
