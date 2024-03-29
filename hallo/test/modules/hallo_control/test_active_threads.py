from threading import Thread

import time

from hallo.events import EventMessage


def test_threads_simple(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "active threads")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "i have" in data[0].text.lower()
    assert "active threads" in data[0].text.lower()


def test_threads_increase(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "active threads")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    first_threads = int(
        data[0].text.lower().split("active")[0].split("have")[1].strip()
    )
    # Launch 10 threads
    for _ in range(10):
        Thread(target=time.sleep, args=(10,)).start()
    # Run function again
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "active threads")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    second_threads = int(
        data[0].text.lower().split("active")[0].split("have")[1].strip()
    )
    assert second_threads > first_threads, "Thread count should have increased"
