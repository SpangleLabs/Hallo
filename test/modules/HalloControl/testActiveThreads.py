import unittest
from threading import Thread

import time

from Server import Server
from test.TestBase import TestBase


class ActiveThreadsTest(TestBase, unittest.TestCase):

    def test_threads_simple(self):
        self.function_dispatcher.dispatch("active threads", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "i have" in data[0][0].lower()
        assert "active threads" in data[0][0].lower()

    def test_threads_increase(self):
        self.function_dispatcher.dispatch("active threads", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "i have" in data[0][0].lower()
        assert "active threads" in data[0][0].lower()
        first_threads = int(data[0][0].lower().split("active")[0].split("have")[1].strip())
        # Launch 10 threads
        for _ in range(10):
            Thread(target=time.sleep, args=(10,)).start()
        # Run function again
        self.function_dispatcher.dispatch("active threads", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "i have" in data[0][0].lower()
        assert "active threads" in data[0][0].lower()
        second_threads = int(data[0][0].lower().split("active")[0].split("have")[1].strip())
        assert second_threads > first_threads, "Thread count should have increased"
