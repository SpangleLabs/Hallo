from threading import Thread

from FunctionDispatcher import FunctionDispatcher
from Hallo import Hallo
import unittest
from test.ServerMock import ServerMock
import time


class TestBase(unittest.TestCase):

    def setUp(self):
        # Create a Hallo
        self.hallo = Hallo()
        # only 1 module, only 1 (mock) server
        self.function_dispatcher = FunctionDispatcher({"AsciiArt", "Bio", "ChannelControl", "Euler", "Furry",
                                                       "HalloControl", "Math", "PermissionControl", "Rss", "Silly",
                                                       "SillyEtd"},
                                                      self.hallo)
        self.hallo.function_dispatcher = self.function_dispatcher
        self.server = ServerMock(self.hallo)
        self.server.name = "mock-server"
        # self.server = unittest.mock.Mock()
        self.hallo.server_list = [self.server]
        # send shit in, check shit out
        self.hallo_thread = Thread(target=self.hallo.start,)
        self.hallo_thread.start()
        self.test_user = self.server.get_user_by_name("test")
        self.test_user.online = True
        self.test_chan = self.server.get_channel_by_name("#test")
        self.test_chan.in_channel = True
        # Wait until hallo is open
        count = 0
        while not self.hallo.open:
            time.sleep(0.1)
            count += 1
            assert count < 100, "Hallo took too long to start."
            if count > 100:
                break
        # Clear any data in the server
        self.server.get_send_data()

    def tearDown(self):
        self.hallo.open = False
        self.hallo_thread.join()
