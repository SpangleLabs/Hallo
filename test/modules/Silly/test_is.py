import unittest

from events import EventMessage
from test.test_base import TestBase


class BlankTest(TestBase, unittest.TestCase):

    def test_blank_empty(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "is"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i am?" == data[0].text.lower(), "Is function not working."

