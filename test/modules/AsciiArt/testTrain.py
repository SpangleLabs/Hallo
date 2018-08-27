import unittest

from Events import EventMessage
from test.TestBase import TestBase


class TrainTest(TestBase, unittest.TestCase):

    def test_train_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "train"))
        data = self.server.get_send_data()
        assert "error" not in data[0][0], "Train output should not produce errors."
        assert "\n" in data[0][0], "Train output should be multiple lines."
        assert "chugga chugga" in data[0][0], "Train needs to say chugga chugga."
