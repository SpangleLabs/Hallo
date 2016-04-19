import unittest

from test.TestBase import TestBase


class DragonTest(TestBase, unittest.TestCase):

    def test_dragon_simple(self):
        self.function_dispatcher.dispatch("dragon", self.test_user, self.test_user)
        data = self.server.get_send_data()
        assert "error" not in data[0][0], "Dragon output should not produce errors."
        assert "\n" in data[0][0], "Dragon output should be multiple lines."

    def test_dragon_deer(self):
        found_deer = False
        for _ in range(1000):
            self.function_dispatcher.dispatch("dragon", self.test_user, self.test_user)
            data = self.server.get_send_data()
            assert "error" not in data[0][0], "Dragon output should not contain errors."
            assert "\n" in data[0][0], "Dragon output should be multiple lines."
            if "deer" in data[0][0]:
                found_deer = True
        assert found_deer, "In 1000 runs, at least 1 call to dragon should return deer."
