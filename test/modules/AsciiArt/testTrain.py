import unittest

from test.TestBase import TestBase


class TrainTest(TestBase, unittest.TestCase):

    def test_train_simple(self):
        self.function_dispatcher.dispatch("train", self.test_user, self.test_user)
        data = self.server.get_send_data()
        assert "error" not in data[0][0], "Train output should not produce errors."
        assert "\n" in data[0][0], "Train output should be multiple lines."
        assert "chugga chugga" in data[0][0], "Train needs to say chugga chugga."
