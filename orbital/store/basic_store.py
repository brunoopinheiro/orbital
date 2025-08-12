from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, TypeAlias

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


@dataclass(frozen=True)
class BasicStore:
    reducer: Reducer
    current_state: State = field(
        default_factory=dict,
        metadata={
            'description': 'Represents the current state of the store. This is a frozen dataclass, meaning its instances are immutable.',  # noqa
        },
        kw_only=True,
    )

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
        return curr_state_keys.difference(new_state_keys) == set()

    def get_state(self) -> State:
        """Returns the current state of the store.

        Returns:
            State: The current state of the store.
        """
        return self.current_state

    def __update_state(self, new_state: State) -> 'BasicStore':
        if not self.__check_state_keys(new_state):
            raise ValueError(
                'The state must contain all keys from the current state.'
            )
        return BasicStore(
            reducer=self.reducer,
            current_state=new_state,
        )

    def dispatch(self, action: str) -> 'BasicStore':
        """
        Dispatches an action to update the store's state.
        The action should be a dictionary with a 'type' key.
        """
        if not isinstance(action, dict) or 'type' not in action:
            raise ValueError("Action must be a dictionary with a 'type' key.")

        new_state = self.reducer(self.current_state, action)
        return self.__update_state(new_state)
