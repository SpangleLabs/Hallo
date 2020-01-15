import threading
import unittest

import time

from server import Server
from server_irc import ServerIRC
from test.test_base import TestBase


class ServerRaceTest(TestBase, unittest.TestCase):

    def test_server_race_cancel_failing_connection(self):
        # Create a server
        server = ServerIRC(self.hallo, "example", "example.com", 80)
        self.hallo.add_server(server)
        server.start()
        # Disconnect a server
        server.disconnect()
        # Check it's closed
        assert server.state == Server.STATE_CLOSED
        # Wait a bit
        time.sleep(5)
        # Check it's still closed
        assert server.state == Server.STATE_CLOSED

    def test_server_race_connect_delay_disconnect(self):
        # Create a server
        server = ServerIRC(self.hallo, "freenode", "irc.freenode.net", 6667)
        self.hallo.add_server(server)
        server.start()
        # Delay
        time.sleep(1)
        self.hallo.open = False
        # Disconnect a server
        server.disconnect()
        # Check it's closed
        assert server.state == Server.STATE_CLOSED
        # Wait a bit
        time.sleep(5)
        # Check it's still closed
        assert server.state == Server.STATE_CLOSED

    def test_server_race_connect_disconnect(self):
        # Create a server
        server = ServerIRC(self.hallo, "freenode", "irc.freenode.net", 6667)
        self.hallo.add_server(server)
        server.start()
        # Disconnect a server
        server.disconnect()
        # Check it's closed
        assert server.state == Server.STATE_CLOSED
        # Wait a bit
        time.sleep(5)
        # Check it's still closed
        assert server.state == Server.STATE_CLOSED

    def test_server_race_bulk_connect_fail(self):
        # Create ten servers
        for x in range(10):
            new_server_obj = ServerIRC(self.hallo, "example"+str(x), "example.com", 80)
            new_server_obj.set_auto_connect(True)
            new_server_obj.nick = "hallo"
            new_server_obj.prefix = None
            self.hallo.add_server(new_server_obj)
            # Connect to the new server object.
            new_server_obj.start()
        # Wait a moment
        time.sleep(1)
        # Disconnect them all
        for server in self.hallo.server_list:
            server.disconnect()
        # Wait a couple seconds
        time.sleep(5)
        # Ensure they're all still closed
        for server in self.hallo.server_list:
            assert not server.is_connected()

    def test_server_thread_killed_after_disconnect(self):
        thread_count = threading.active_count()
        # Create a server
        server = ServerIRC(self.hallo, "freenode", "irc.freenode.net", 6667)
        self.hallo.add_server(server)
        server.start()
        # Delay
        time.sleep(1)
        # Disconnect a server
        server.disconnect()
        # Check thread count is back to the start count
        assert threading.active_count() == thread_count
        # Check it's closed
        assert server.state == Server.STATE_CLOSED
