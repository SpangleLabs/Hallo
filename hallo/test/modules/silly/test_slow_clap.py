import time

from hallo.events import EventMessage


def test_slowclap(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    time_start = time.time()
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "slowclap")
    )
    time_end = time.time()
    data = test_hallo.test_server.get_send_data(3, test_hallo.test_chan, EventMessage)
    assert time_end - time_start > 2, "Slowclap should take at least 2 seconds."
    assert "clap" in data[0].text.lower()
    assert "clap" in data[1].text.lower()
    assert "clap." in data[2].text.lower(), "Final clap needs a fullstop."


def test_slowclap_privmsg(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    time_start = time.time()
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "slowclap")
    )
    time_end = time.time()
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert time_end - time_start < 2, "Slowclap error should take less than 2 seconds."
    assert "error" in data[0].text.lower()


def test_slowclap_chan(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    time_start = time.time()
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "slowclap " + test_hallo.test_chan2.name)
    )
    time_end = time.time()
    data = test_hallo.test_server.get_send_data(4, None, EventMessage)
    assert time_end - time_start > 2, "Slowclap should take at least 2 seconds."
    assert data[0].channel == test_hallo.test_chan2
    assert data[1].channel == test_hallo.test_chan2
    assert data[2].channel == test_hallo.test_chan2
    assert data[3].user == test_hallo.test_user, "Done response should go to user."
    assert "clap" in data[0].text.lower()
    assert "clap" in data[1].text.lower()
    assert "clap." in data[2].text.lower(), "Final clap needs a fullstop."
    assert (
        "done" in data[3].text.lower()
    ), "Done message should be sent to original user."


def test_slowclap_chan_not_in_chan(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = False
    time_start = time.time()
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "slowclap " + test_hallo.test_chan2.name)
    )
    time_end = time.time()
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert time_end - time_start < 2, "Slowclap error should take less than 2 seconds."
    assert "error" in data[0].text.lower()
