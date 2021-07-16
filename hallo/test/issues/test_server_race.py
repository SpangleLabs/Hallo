import threading

import time

import pytest

from hallo.server import Server
from hallo.server_irc import ServerIRC


@pytest.mark.slow
def test_server_race_cancel_failing_connection(hallo_getter):
    test_hallo = hallo_getter({})
    # Create a server
    server = ServerIRC(test_hallo, "example", "example.com", 80)
    test_hallo.add_server(server)
    server.start()
    # Disconnect a server
    server.disconnect()
    # Check it's closed
    assert server.state == Server.STATE_CLOSED
    # Wait a bit
    time.sleep(5)
    # Check it's still closed
    assert server.state == Server.STATE_CLOSED


@pytest.mark.external_integration
def test_server_race_connect_delay_disconnect(hallo_getter):
    test_hallo = hallo_getter({})
    # Create a server
    server = ServerIRC(test_hallo, "freenode", "irc.freenode.net", 6667)
    test_hallo.add_server(server)
    server.start()
    # Delay
    time.sleep(1)
    test_hallo.open = False
    # Disconnect a server
    server.disconnect()
    # Check it's closed
    assert server.state == Server.STATE_CLOSED
    # Wait a bit
    time.sleep(5)
    # Check it's still closed
    assert server.state == Server.STATE_CLOSED


@pytest.mark.external_integration
def test_server_race_connect_disconnect(hallo_getter):
    test_hallo = hallo_getter({})
    # Create a server
    server = ServerIRC(test_hallo, "freenode", "irc.freenode.net", 6667)
    test_hallo.add_server(server)
    server.start()
    # Disconnect a server
    server.disconnect()
    # Check it's closed
    assert server.state == Server.STATE_CLOSED
    # Wait a bit
    time.sleep(5)
    # Check it's still closed
    assert server.state == Server.STATE_CLOSED


@pytest.mark.slow
def test_server_race_bulk_connect_fail(hallo_getter):
    test_hallo = hallo_getter({})
    # Create ten servers
    for x in range(10):
        new_server_obj = ServerIRC(test_hallo, "example" + str(x), "example.com", 80)
        new_server_obj.set_auto_connect(True)
        new_server_obj.nick = "hallo"
        new_server_obj.prefix = None
        test_hallo.add_server(new_server_obj)
        # Connect to the new server object.
        new_server_obj.start()
    # Wait a moment
    time.sleep(1)
    # Disconnect them all
    for server in test_hallo.server_list:
        server.disconnect()
    # Wait a couple seconds
    time.sleep(5)
    # Ensure they're all still closed
    for server in test_hallo.server_list:
        assert not server.is_connected()


@pytest.mark.external_integration
def test_server_thread_killed_after_disconnect(hallo_getter):
    test_hallo = hallo_getter({})
    thread_count = threading.active_count()
    # Create a server
    server = ServerIRC(test_hallo, "freenode", "irc.freenode.net", 6667)
    test_hallo.add_server(server)
    server.start()
    # Delay
    time.sleep(1)
    # Disconnect a server
    server.disconnect()
    # Delay
    time.sleep(1)
    # Check thread count is back to the start count
    assert threading.active_count() == thread_count
    # Check it's closed
    assert server.state == Server.STATE_CLOSED
