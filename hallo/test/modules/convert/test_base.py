from threading import Thread

import gc

from hallo.function_dispatcher import FunctionDispatcher
from hallo.hallo import Hallo
import unittest
from hallo.test.server_mock import ServerMock
import time


class TestBase(unittest.TestCase):
    def setUp(self):
        # Create a Hallo
        self.hallo = Hallo()
        # Only the required modules, only 1 (mock) server
        # Todo: specify modules by test?
        self.function_dispatcher = FunctionDispatcher(
            {"convert", "random", "server_control", "subscriptions"}, self.hallo
        )
        self.hallo.function_dispatcher = self.function_dispatcher
        self.server = ServerMock(self.hallo)
        self.server.name = "mock-server"
        self.hallo.add_server(self.server)
        # Start hallo thread
        self.hallo_thread = Thread(target=self.hallo.start,)
        self.hallo_thread.start()
        # Create test users and channel, and configure them
        self.hallo_user = self.server.get_user_by_address(
            self.server.get_nick().lower(), self.server.get_nick()
        )
        self.test_user = self.server.get_user_by_address("test", "test")
        self.test_user.online = True
        self.test_chan = self.server.get_channel_by_address("#test", "#test")
        self.test_chan.in_channel = True
        self.test_chan.add_user(self.hallo_user)
        self.test_chan.add_user(self.test_user)
        # Wait until hallo is open
        count = 0
        while not self.hallo.open:
            time.sleep(0.01)
            count += 1
            assert count < 1000, "Hallo took too long to start."
            if count > 1000:
                break
        # Clear any data in the server
        self.server.get_send_data()

    def tearDown(self):
        self.hallo.close()
        self.hallo_thread.join()

    @classmethod
    def tearDownClass(cls):
        del cls
        gc.collect()
