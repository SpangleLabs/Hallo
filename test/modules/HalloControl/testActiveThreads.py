import unittest

from Server import Server
from test.TestBase import TestBase


class ActiveThreadsTest(TestBase, unittest.TestCase):

    def test_threads_simple(self):
        self.function_dispatcher.dispatch("active threads", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "i have" in data[0][0].lower()
        assert "active threads" in data[0][0].lower()

    def test_threads_increase(self):
        pass
