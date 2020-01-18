from threading import Thread

import gc

from function_dispatcher import FunctionDispatcher
from hallo import Hallo
import unittest
from test.server_mock import ServerMock
import time


class TestBase(unittest.TestCase):

    def setUp(self):
        print("Starting test: "+self.id())
        self.start_time = time.time()
        # Create a Hallo
        self.hallo = Hallo()
        # Swap out raw printer function for empty
        self.hallo.printer.output = lambda *args: None
        # Only the required modules, only 1 (mock) server
        # Todo: specify modules by test?
        self.function_dispatcher = FunctionDispatcher(
            {
                "convert", "random", "server_control", "subscriptions"
            },
            self.hallo
        )
        self.hallo.function_dispatcher = self.function_dispatcher
        print("Running test: "+self.id()+". Init took: "+str(time.time()-self.start_time)+" seconds.")
        self.server = ServerMock(self.hallo)
        self.server.name = "mock-server"
        self.hallo.add_server(self.server)
        # Start hallo thread
        self.hallo_thread = Thread(target=self.hallo.start,)
        self.hallo_thread.start()
        # Create test users and channel, and configure them
        self.hallo_user = self.server.get_user_by_address(self.server.get_nick().lower(), self.server.get_nick())
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
        # Print test startup time
        print("Running test: "+self.id()+". Startup took: "+str(time.time()-self.start_time)+" seconds.")
        self.start_time = time.time()

    def tearDown(self):
        print("Finishing test: "+self.id()+". Test took: "+str(time.time()-self.start_time)+" seconds.")
        self.hallo.close()
        self.hallo_thread.join()
        print("Finished test: "+self.id()+". Test took: "+str(time.time()-self.start_time)+" seconds.")

    @classmethod
    def tearDownClass(cls):
        del cls
        gc.collect()
