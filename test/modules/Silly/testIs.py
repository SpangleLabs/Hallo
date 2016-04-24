import unittest

from Server import Server
from test.TestBase import TestBase


class BlankTest(TestBase, unittest.TestCase):

    def test_blank_empty(self):
        self.function_dispatcher.dispatch("is", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "i am?" == data[0][0].lower(), "Is function not working."

