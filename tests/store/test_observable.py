from orbital.store.observable import Observable


def test_observable_subscribe(concrete_observer):
    observer = concrete_observer()
    observable = Observable()
    observable.subscribe(observer)
    assert observer in observable._subscribers


def test_unsubscribe(capsys, concrete_observer):
    observer = concrete_observer()
    observable = Observable()
    observable.subscribe(observer)
    observable.unsubscribe(observer)
    assert observer not in observable._subscribers


def test_notify_subscribers(capsys, concrete_observer):
    observer = concrete_observer()
    observable = Observable()
    observable.subscribe(observer)
    observable.notify_subscribers("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_multiple_subscribers(capsys, concrete_observer):
    observer1 = concrete_observer()
    observer2 = concrete_observer()
    observer2.update = lambda message: print(f"Observer 2: {message}")
    observable = Observable()
    observable.subscribe(observer1)
    observable.subscribe(observer2)
    observable.notify_subscribers("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out
    assert "Observer 2: Test message" in captured.out
