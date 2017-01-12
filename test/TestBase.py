from threading import Thread

from FunctionDispatcher import FunctionDispatcher
from Hallo import Hallo
import unittest
from test.ServerMock import ServerMock
import time


class TestBase(unittest.TestCase):

    def setUp(self):
        print("Starting test: "+self.id())
        self.start_time = time.time()
        # Create a Hallo
        self.hallo = Hallo()
        # Swap out raw printer function for empty
        self.hallo.printer.print_raw = self.empty
        # Only the required modules, only 1 (mock) server
        # Todo: specify modules by test?
        self.function_dispatcher = FunctionDispatcher({"AsciiArt", "Bio", "ChannelControl", "Euler", "Furry",
                                                       "HalloControl", "Math", "PermissionControl", "Rss",
                                                       "ServerControl", "Silly", "SillyEtd"},
                                                      self.hallo)
        self.hallo.function_dispatcher = self.function_dispatcher
        self.server = ServerMock(self.hallo)
        self.server.name = "mock-server"
        # self.server = unittest.mock.Mock()
        self.hallo.add_server(self.server)
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
        # Print test startup time
        print("Running test: "+self.id()+". Startup took: "+str(time.time()-self.start_time)+" seconds.")
        self.start_time = time.time()

    def tearDown(self):
        print("Finishing test: "+self.id()+". Test took: "+str(time.time()-self.start_time)+" seconds.")
        self.hallo.open = False
        self.hallo_thread.join()
        self.hallo = None

    def empty(self, var1=None, var2=None, var3=None, var4=None):
        pass
