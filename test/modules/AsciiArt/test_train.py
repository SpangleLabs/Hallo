import unittest

from events import EventMessage
from test.test_base import TestBase


class TrainTest(TestBase, unittest.TestCase):

    def test_train_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "train"))
        data = self.server.get_send_data()
        assert "error" not in data[0].text, "Train output should not produce errors."
        assert "\n" in data[0].text, "Train output should be multiple lines."
        assert "chugga chugga" in data[0].text, "Train needs to say chugga chugga."
