import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class LeaveChannelTest(TestBase, unittest.TestCase):

    def test_no_args(self):
        self.function_dispatcher.dispatch("leave", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()

    def test_channel_name(self):
        self.function_dispatcher.dispatch("leave "+self.test_chan.name, self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()

    def test_no_args_privmsg(self):
        self.function_dispatcher.dispatch("leave", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        self.server.get_left_channels(0)
        assert "error" in data[0][0].lower()

    def test_other_channel_name(self):
        other = self.server.get_channel_by_name("#other")
        other.in_channel = True
        self.function_dispatcher.dispatch("leave "+other.name, self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == other
        assert "left" in data[0][0].lower()
        assert other.name in data[0][0].lower()

    def test_channel_name_privmsg(self):
        self.function_dispatcher.dispatch("leave "+self.test_chan.name, self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()

    def test_not_in_channel(self):
        self.function_dispatcher.dispatch("leave #not_in_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        self.server.get_left_channels(0)
        assert "error" in data[0][0].lower()

    def test_server_specified_first(self):
        # Set up test resources
        test_serv = ServerMock(self.hallo)
        test_serv.name = "TestServer1"
        self.hallo.add_server(test_serv)
        test_chan = test_serv.get_channel_by_name("#other_serv")
        test_chan.in_channel = True
        # Send command
        self.function_dispatcher.dispatch("leave server="+test_serv.name+" "+test_chan.name, self.test_user,
                                          self.test_chan)
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        self.server.get_left_channels(0)
        chans = test_serv.get_left_channels(1)
        assert chans[0] == test_chan
        assert "left" in data[0][0].lower()
        assert test_chan.name in data[0][0].lower()

    def test_server_specified_second(self):
        # Set up test resources
        test_serv = ServerMock(self.hallo)
        test_serv.name = "TestServer1"
        self.hallo.add_server(test_serv)
        test_chan = test_serv.get_channel_by_name("#other_serv")
        test_chan.in_channel = True
        # Send command
        self.function_dispatcher.dispatch("leave "+test_chan.name+" server="+test_serv.name, self.test_user,
                                          self.test_chan)
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        self.server.get_left_channels(0)
        chans = test_serv.get_left_channels(1)
        assert chans[0] == test_chan
        assert "left" in data[0][0].lower()
        assert test_chan.name in data[0][0].lower()

    def test_server_specified_no_channel(self):
        # Set up test resources
        test_serv = ServerMock(self.hallo)
        test_serv.name = "TestServer1"
        self.hallo.add_server(test_serv)
        test_chan = test_serv.get_channel_by_name("#not_in_channel")
        test_chan.in_channel = False
        # Send command
        self.function_dispatcher.dispatch("leave server="+test_serv.name+" "+test_chan.name, self.test_user,
                                          self.test_chan)
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        self.server.get_left_channels(0)
        test_serv.get_left_channels(0)
        assert "error" in data[0][0].lower()

    def test_server_not_on_server(self):
        # Send command
        self.function_dispatcher.dispatch("leave server=not_a_server "+self.test_chan.name, self.test_user,
                                          self.test_chan)
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        self.server.get_left_channels(0)
        print(data[0][0].lower())
        assert "error" in data[0][0].lower()

    def test_not_auto_join(self):
        # Make test channel auto join
        self.test_chan.auto_join = True
        # Send command
        self.function_dispatcher.dispatch("leave "+self.test_chan.name, self.test_user, self.test_chan)
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()
        # Check that test channel is not auto join anymore
        assert not self.test_chan.auto_join

    def test_post_not_in_channel(self):
        # Assert in channel
        assert self.test_chan.in_channel
        # Send command
        self.function_dispatcher.dispatch("leave "+self.test_chan.name, self.test_user, self.test_chan)
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()
        # Check that test channel is not in the channel anymore
        assert not self.test_chan.in_channel