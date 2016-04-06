from threading import Thread

from FunctionDispatcher import FunctionDispatcher
from Hallo import Hallo
from Server import Server
import unittest


class ServerMock(Server):

    def __init__(self, hallo):
        super().__init__(hallo)
        self.send_data = []

    def join_channel(self, channel_obj):
        pass

    def disconnect(self):
        pass

    def connect(self):
        pass

    def get_type(self):
        pass

    @staticmethod
    def from_xml(xml_string, hallo):
        pass

    def leave_channel(self, channel_obj):
        pass

    def send(self, data, destination_obj=None, msg_type=Server.MSG_MSG):
        self.send_data.append((data, destination_obj, msg_type))

    def run(self):
        pass

    def reconnect(self):
        pass

    def check_user_identity(self, user_obj):
        pass

    def to_xml(self):
        pass

    def get_send_data(self):
        out_data = self.send_data
        self.send_data = []
        return out_data


class MathTest(unittest.TestCase):

    def setUp(self):
        # Create a Hallo
        self.hallo = Hallo()
        # only 1 module, only 1 (mock) server
        self.function_dispatcher = FunctionDispatcher({"Math"}, self.hallo)
        self.hallo.function_dispatcher = self.function_dispatcher
        self.server = ServerMock(self.hallo)
        # self.server = unittest.mock.Mock()
        self.hallo.server_list = [self.server]
        # send shit in, check shit out
        self.hallo_thread = Thread(target=self.hallo.start,)
        self.hallo_thread.start()
        self.test_user = self.server.get_user_by_name("test")

    def tearDown(self):
        self.hallo.open = False
        self.hallo_thread.join()

    def test_calc_simple(self):
        self.server.get_send_data()
        self.function_dispatcher.dispatch("calc 2+2", self.test_user, self.test_user)
        data = self.server.get_send_data()
        assert len(data) == 1
        assert len(data[0]) == 3
        assert data[0][0] == "4"
        assert data[0][1] == self.test_user
        assert data[0][2] == Server.MSG_MSG

    def test_calc_multiply(self):
        self.server.get_send_data()
        self.function_dispatcher.dispatch("calc 21*56", self.test_user, self.test_user)
        data = self.server.get_send_data()
        assert len(data) == 1
        assert len(data[0]) == 3
        assert data[0][0] == "1176"
        assert data[0][1] == self.test_user
        assert data[0][2] == Server.MSG_MSG
