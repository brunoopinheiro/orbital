import pytest

from orbital.store.basic_store import (
    BasicStore,
    Reducer,
    State,
    combine_reducers,
)


@pytest.fixture
def sample_reducer() -> Reducer:
    def reducer(state: State, action: str) -> State:
        if action == "increment":
            return {"count": state.get("count", 0) + 1}
        return state

    return reducer


@pytest.fixture
def second_reducer() -> Reducer:
    def reducer(state: State, action: str) -> State:
        if action == "decrement":
            return {"count": state.get("count", 0) - 1}
        return state

    return reducer


def test_combine_reducers(sample_reducer, second_reducer):
    combined = combine_reducers([sample_reducer, second_reducer])
    assert combined({"count": 0}, "increment") == {"count": 1}
    assert combined({"count": 1}, "decrement") == {"count": 0}


def test_combined_reducer_raising_error(sample_reducer, second_reducer):
    def invalid_reducer(state: State, action: str) -> str:
        return "invalid_state"
    combined = combine_reducers(
        [sample_reducer, second_reducer, invalid_reducer],  # type: ignore
    )
    with pytest.raises(ValueError):  # noqa: PT011
        combined({"count": 0}, "unknown_action")


def test_notifier_subscribe_doesnt_change_store(
    sample_reducer,
    concrete_observer,
):
    store = BasicStore(
        reducer=sample_reducer,
        current_state={"count": 0},
    )
    observer_1 = concrete_observer()
    store.subscribe(observer_1)
    assert observer_1 in store._notifier._subscribers


def test_notifier_unsubscribe_doesnt_change_store(
    sample_reducer,
    concrete_observer,
):
    store = BasicStore(
        reducer=sample_reducer,
        current_state={'count': 0},
    )
    observer1 = concrete_observer()
    store.subscribe(observer1)
    store.unsubscribe(observer1)
    assert observer1 not in store._notifier._subscribers


def test_notifier_notify_subscribers_doesnt_change_store(
    sample_reducer,
    concrete_observer,
    capsys,
):
    store = BasicStore(
        reducer=sample_reducer,
        current_state={'count': 0},
    )
    observer1 = concrete_observer()
    store.subscribe(observer1)
    store.notify_subscribers("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_get_state(sample_reducer):
    store = BasicStore(
        reducer=sample_reducer,
        current_state={'count': 0},
    )
    assert store.get_state() == {'count': 0}


def test_dispatch_action(sample_reducer):
    store = BasicStore(
        reducer=sample_reducer,
        current_state={'count': 0},
    )
    new_store = store.dispatch("increment")
    assert store.get_state() == {'count': 0}
    assert new_store.get_state() == {'count': 1}


def test_update_state_raises_value_error_at_invalid_state():
    def invalid_reducer(state: State, action: str) -> State:
        state['new_key'] = action
        return state

    store = BasicStore(
        reducer=invalid_reducer,
        current_state={'count': 0},
    )
    with pytest.raises(ValueError):  # noqa: PT011
        store.dispatch("increment")


def test_dispatch_should_raise_value_error_on_invalid_type_state():
    def invalid_reducer(state: State, action: str) -> str:
        return "invalid_state"

    store = BasicStore(
        reducer=invalid_reducer,  # type: ignore
        current_state={'count': 0},
    )

    with pytest.raises(ValueError):  # noqa: PT011
        store.dispatch("increment")


def test_current_state_is_imutable(
    sample_reducer,
):
    store = BasicStore(
        reducer=sample_reducer,
        current_state={'count': 0},
    )

    store.current_state['count'] = 1
    assert store.current_state['count'] == 0
