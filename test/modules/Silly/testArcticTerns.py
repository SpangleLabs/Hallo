import unittest

from Server import Server
from test.TestBase import TestBase
from inc.Commons import Commons


class ArcticTernTest(TestBase, unittest.TestCase):

    def test_tern_simple(self):
        self.function_dispatcher.dispatch("arctic tern", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "arctic tern" in data[0][0].lower(), "Arctic tern function not returning arctic tern."
        assert "http://" in data[0][0].lower(), "URL not in arctic tern response."
        url = "http://" + data[0][0].split("http://")[1]
        data_url = Commons.load_url_string(url)
        assert len(data_url) > 0, "Arctic tern link incorrect."

    def test_tern_plush(self):
        self.function_dispatcher.dispatch("arctic tern plush", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "plush" in data[0][0].lower(), "Plush arctic tern function didn't say it was plush."
        assert "arctic tern" in data[0][0].lower(), "Arctic tern function not returning arctic tern."
        assert "http://" in data[0][0].lower(), "URL not in arctic tern response."
        url = "http://" + data[0][0].split("http://")[1]
        data_url = Commons.load_url_string(url)
        assert len(data_url) > 0, "Plush arctic tern link incorrect."
