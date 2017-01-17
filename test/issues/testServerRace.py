import unittest
from threading import Thread

import time

from Server import ServerIRC
from test.TestBase import TestBase


class ServerRaceTest(TestBase, unittest.TestCase):

    def testServerRaceIRC(self):
        # Create ten servers
        for x in range(10):
            new_server_obj = ServerIRC(self.hallo, "example"+str(x), "example.com", 80)
            new_server_obj.set_auto_connect(True)
            new_server_obj.set_nick("hallo")
            new_server_obj.set_prefix(None)
            self.hallo.add_server(new_server_obj)
            # Connect to the new server object.
            Thread(target=new_server_obj.run).start()
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
