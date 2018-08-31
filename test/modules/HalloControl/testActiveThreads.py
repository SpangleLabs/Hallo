import unittest
from threading import Thread

import time

from Events import EventMessage
from test.TestBase import TestBase


class ActiveThreadsTest(TestBase, unittest.TestCase):

    def test_threads_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "active threads"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i have" in data[0].text.lower()
        assert "active threads" in data[0].text.lower()

    def test_threads_increase(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "active threads"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i have" in data[0].text.lower()
        assert "active threads" in data[0].text.lower()
        first_threads = int(data[0].text.lower().split("active")[0].split("have")[1].strip())
        # Launch 10 threads
        for _ in range(10):
            Thread(target=time.sleep, args=(10,)).start()
        # Run function again
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "active threads"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i have" in data[0].text.lower()
        assert "active threads" in data[0].text.lower()
        second_threads = int(data[0].text.lower().split("active")[0].split("have")[1].strip())
        assert second_threads > first_threads, "Thread count should have increased"
