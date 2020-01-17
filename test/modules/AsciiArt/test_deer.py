import time
from threading import Thread

import pytest

from events import EventMessage
from function_dispatcher import FunctionDispatcher
from hallo import Hallo
from test.server_mock import ServerMock


@pytest.fixture
def hallo_getter():
    # Create a Hallo
    hallo = Hallo()
    hallo.printer.output = lambda *args: None
    hallo_thread = Thread(target=hallo.start, )

    def function(modules=None):
        if modules is None:
            modules = {
                "ascii_art", "bio", "channel_control", "convert", "euler", "hallo_control", "math",
                "permission_control", "random", "server_control", "silly", "subscriptions"
            }
        function_dispatcher = FunctionDispatcher(modules, hallo)
        hallo.function_dispatcher = function_dispatcher
        # Create server
        server = ServerMock(hallo)
        server.name = "mock-server"
        hallo.add_server(server)
        # Start hallo thread
        hallo_thread.start()
        # Create test users and channel, and configure them
        hallo_user = server.get_user_by_address(server.get_nick().lower(), server.get_nick())
        test_user = server.get_user_by_address("test", "test")
        test_user.online = True
        test_chan = server.get_channel_by_address("#test", "#test")
        test_chan.in_channel = True
        test_chan.add_user(hallo_user)
        test_chan.add_user(test_user)
        # Wait until hallo is open
        count = 0
        while not hallo.open:
            time.sleep(0.01)
            count += 1
            assert count < 1000, "Hallo took too long to start."
            if count > 1000:
                break
        # Clear any data in the server
        server.get_send_data()
        return hallo, server, test_chan, test_user
    yield function
    hallo.close()
    hallo_thread.join()


def test_deer_simple(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"ascii_art"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "deer"))
    data = test_server.get_send_data()
    assert "error" not in data[0].text, "Deer output should not produce errors."
    assert "\n" in data[0].text, "Deer output should be multiple lines."
