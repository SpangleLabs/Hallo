import unittest

from Server import Server
from test.TestBase import TestBase

#
# class TrumpTest(TestBase, unittest.TestCase):
# 
#     def test_trump_simple(self):
#         self.function_dispatcher.dispatch("trump", self.test_user, self.test_user)
#         data = self.server.get_send_data(1, self.test_user, EventMessage)
#         assert "error" not in data[0].text.lower(), "Trump function is returning error."
#         assert "IMPERATOR TRUMP!" in data[0].text, "Trump function does not declare imperator trump."
#
#     def test_trump_num(self):
#         self.function_dispatcher.dispatch("trump 7", self.test_user, self.test_user)
#         data = self.server.get_send_data(1, self.test_user, EventMessage)
#         assert data[0].text.count("Trump") == 7, "Trump numerical input not working."
#
#     def test_trump_max(self):
#         self.function_dispatcher.dispatch("trump 10", self.test_user, self.test_user)
#         data10 = self.server.get_send_data(1, self.test_user, EventMessage)
#         self.function_dispatcher.dispatch("trump 20", self.test_user, self.test_user)
#         data20 = self.server.get_send_data(1, self.test_user, EventMessage)
#         assert data10[0][0] == data20[0][0], "Trump function max limit is not working."
#
#     def test_trump_str(self):
#         self.function_dispatcher.dispatch("trump yeah!", self.test_user, self.test_user)
#         data = self.server.get_send_data(1, self.test_user, EventMessage)
#         assert "error" not in data[0].text.lower(), "Trump function is not working when given invalid number."
