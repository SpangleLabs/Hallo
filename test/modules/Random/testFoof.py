import unittest
from datetime import datetime

from Events import EventMessage
from inc.Commons import Commons
from test.TestBase import TestBase


class MockRoller:

    def __init__(self):
        self.answer = 0
        self.last_min = None
        self.last_max = None
        self.last_count = None

    def roll(self, min_int, max_int, count=1):
        self.last_min = min_int
        self.last_max = max_int
        self.last_count = count
        if isinstance(self.answer, list):
            return self.answer
        return [self.answer] * count


class FoofTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.roller = MockRoller()
        self.old_int_method = Commons.get_random_int
        Commons.get_random_int = self.roller.roll

    def tearDown(self):
        super().tearDown()
        Commons.get_random_int = self.old_int_method

    def test_short_doof(self):
        for x in range(21):
            # Set RNG
            self.roller.answer = x
            # Check
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fooooooof"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "doof" == data[0].text.lower(), "Should be short doof."

    def test_medium_doof(self):
        for x in range(21, 41):
            # Set RNG
            self.roller.answer = x
            # Check
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "foof"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "doooooof" == data[0].text.lower(), "Should be medium doof."

    def test_long_doof(self):
        for x in range(41, 60):
            if x == 40 + 15:
                continue
            # Set RNG
            self.roller.answer = x
            # Check
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "foooof"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "ddddoooooooooooooooooooooffffffffff." == data[0].text.lower(), "Should be long doof."

    def test_mega_doof(self):
        # Set RNG
        self.roller.answer = 55
        # Check
        start_time = datetime.now()
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "foof"))
        end_time = datetime.now()
        data = self.server.get_send_data(2, self.test_user, EventMessage)
        assert "powering up..." == data[0].text.lower(), "Should have powered up."
        assert (end_time - start_time).seconds > 3, "Should have had a delay between powering up and mega doof."
        assert len(data[1].text.lower()) > 1000, "doof should be extra long."
        assert "!" in data[1].text, "doof should have exclamation mark."

    def test_passive_foof(self):
        self.roller.answer = 0
        self.function_dispatcher.dispatch_passive(EventMessage(self.server, self.test_chan, self.test_user, "foof"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "doof" == data[0].text.lower(), "Should be short doof."

    def test_passive_foof_exclamation(self):
        self.roller.answer = 0
        self.function_dispatcher.dispatch_passive(EventMessage(self.server, self.test_chan, self.test_user, "foof!"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "doof" == data[0].text.lower(), "Should be short doof."

    def test_passive_long_foof(self):
        self.roller.answer = 0
        self.function_dispatcher.dispatch_passive(EventMessage(self.server, self.test_chan, self.test_user,
                                                               "foooooooooooooooof"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "doof" == data[0].text.lower(), "Should be short doof."
