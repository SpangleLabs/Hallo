import unittest

from Events import EventMessage
from test.TestBase import TestBase


class ChooseTest(TestBase, unittest.TestCase):

    def test_no_options(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "more than 1 thing" in data[0].text.lower(), "Not warning about single option."

    def test_one_option(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose x"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "more than 1 thing" in data[0].text.lower(), "Not warning about single option."

    def test_x_or_y(self):
        results = {"x": 0, "y": 0}
        for _ in range(100):
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose x or y"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "i choose" in data[0].text.lower(), "Didn't choose an option"
            if "\"x\"" in data[0].text.lower():
                results["x"] += 1
            elif "\"y\"" in data[0].text.lower():
                results["y"] += 1
            else:
                assert False, "Option chosen wasn't one of the 2 options."
        assert results["x"] + results["y"] == 100, "Not 100 options were chosen."
        assert results["x"] < 65, "Chose first option too often."
        assert results["x"] >= 35, "Chose second option too often."

    def test_x_comma_y(self):
        results = {"x": 0, "y": 0}
        for _ in range(100):
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose x, y"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "i choose" in data[0].text.lower(), "Didn't choose an option"
            if "\"x\"" in data[0].text.lower():
                results["x"] += 1
            elif "\"y\"" in data[0].text.lower():
                results["y"] += 1
            else:
                assert False, "Option chosen wasn't one of the 2 options."
        assert results["x"] + results["y"] == 100, "Not 100 options were chosen."
        assert results["x"] < 65, "Chose first option too often."
        assert results["x"] >= 35, "Chose second option too often."

    def test_x_or_comma_y(self):
        results = {"x": 0, "y": 0}
        for _ in range(100):
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose x or, y"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "i choose" in data[0].text.lower(), "Didn't choose an option"
            if "\"x\"" in data[0].text.lower():
                results["x"] += 1
            elif "\"y\"" in data[0].text.lower():
                results["y"] += 1
            else:
                assert False, "Option chosen wasn't one of the 2 options."
        assert results["x"] + results["y"] == 100, "Not 100 options were chosen."
        assert results["x"] < 65, "Chose first option too often."
        assert results["x"] >= 35, "Chose second option too often."

    def test_x_y_z(self):
        results = {"x": 0, "y": 0, "z": 0}
        for _ in range(100):
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose x or y or z"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "i choose" in data[0].text.lower(), "Didn't choose an option"
            if "\"x\"" in data[0].text.lower():
                results["x"] += 1
            elif "\"y\"" in data[0].text.lower():
                results["y"] += 1
            elif "\"z\"" in data[0].text.lower():
                results["z"] += 1
            else:
                assert False, "Option chosen wasn't one of the 3 options."
        assert results["x"] + results["y"] + results["z"] == 100, "Not 100 options were chosen."
        assert results["x"] < 49, "Chose first option too often."
        assert results["x"] >= 19, "Chose first option not often enough."
        assert results["y"] < 49, "Chose second option too often."
        assert results["y"] >= 19, "Chose second option not often enough."
        assert results["z"] < 49, "Chose third option too often."
        assert results["z"] >= 19, "Chose third option not often enough."

    def test_multiple_separators(self):
        results = {"x": 0, "y": 0, "z": 0}
        for _ in range(100):
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "choose x, y or z"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "i choose" in data[0].text.lower(), "Didn't choose an option"
            if "\"x\"" in data[0].text.lower():
                results["x"] += 1
            elif "\"y\"" in data[0].text.lower():
                results["y"] += 1
            elif "\"z\"" in data[0].text.lower():
                results["z"] += 1
            else:
                assert False, "Option chosen wasn't one of the 3 options."
        assert results["x"] + results["y"] + results["z"] == 100, "Not 100 options were chosen."
        assert results["x"] < 49, "Chose first option too often."
        assert results["x"] >= 19, "Chose first option not often enough."
        assert results["y"] < 49, "Chose second option too often."
        assert results["y"] >= 19, "Chose second option not often enough."
        assert results["z"] < 49, "Chose third option too often."
        assert results["z"] >= 19, "Chose third option not often enough."
