import unittest

from events import EventMessage
from test.server_mock import ServerMock
from test.test_base import TestBase


class LeaveChannelTest(TestBase, unittest.TestCase):

    def test_no_args(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "leave"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0].text.lower()
        assert self.test_chan.name in data[0].text.lower()

    def test_channel_name(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave "+self.test_chan.name))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0].text.lower()
        assert self.test_chan.name in data[0].text.lower()

    def test_no_args_privmsg(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "leave"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        self.server.get_left_channels(0)
        assert "error" in data[0].text.lower()

    def test_other_channel_name(self):
        other = self.server.get_channel_by_address("#other".lower(), "#other")
        other.in_channel = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave "+other.name))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        chans = self.server.get_left_channels(1)
        assert chans[0] == other
        assert "left" in data[0].text.lower()
        assert other.name in data[0].text.lower()

    def test_channel_name_privmsg(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "leave "+self.test_chan.name))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0].text.lower()
        assert self.test_chan.name in data[0].text.lower()

    def test_not_in_channel(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave #not_in_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        self.server.get_left_channels(0)
        assert "error" in data[0].text.lower()

    def test_server_specified_first(self):
        # Set up test resources
        test_serv = ServerMock(self.hallo)
        test_serv.name = "TestServer1"
        self.hallo.add_server(test_serv)
        test_chan = test_serv.get_channel_by_address("#other_serv".lower(), "#other_serv")
        test_chan.in_channel = True
        # Send command
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave server="+test_serv.name+" "+test_chan.name))
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        self.server.get_left_channels(0)
        chans = test_serv.get_left_channels(1)
        assert chans[0] == test_chan
        assert "left" in data[0].text.lower()
        assert test_chan.name in data[0].text.lower()

    def test_server_specified_second(self):
        # Set up test resources
        test_serv = ServerMock(self.hallo)
        test_serv.name = "TestServer1"
        self.hallo.add_server(test_serv)
        test_chan = test_serv.get_channel_by_address("#other_serv".lower(), "#other_serv")
        test_chan.in_channel = True
        # Send command
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave "+test_chan.name+" server="+test_serv.name))
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        self.server.get_left_channels(0)
        chans = test_serv.get_left_channels(1)
        assert chans[0] == test_chan
        assert "left" in data[0].text.lower()
        assert test_chan.name in data[0].text.lower()

    def test_server_specified_no_channel(self):
        # Set up test resources
        test_serv = ServerMock(self.hallo)
        test_serv.name = "TestServer1"
        self.hallo.add_server(test_serv)
        test_chan = test_serv.get_channel_by_address("#not_in_channel".lower(), "#not_in_channel")
        test_chan.in_channel = False
        # Send command
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave server="+test_serv.name+" "+test_chan.name))
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        self.server.get_left_channels(0)
        test_serv.get_left_channels(0)
        assert "error" in data[0].text.lower()

    def test_server_not_on_server(self):
        # Send command
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave server=not_a_server "+self.test_chan.name))
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        self.server.get_left_channels(0)
        assert "error" in data[0].text.lower()

    def test_not_auto_join(self):
        # Make test channel auto join
        self.test_chan.auto_join = True
        # Send command
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave "+self.test_chan.name))
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0].text.lower()
        assert self.test_chan.name in data[0].text.lower()
        # Check that test channel is not auto join anymore
        assert not self.test_chan.auto_join

    def test_post_not_in_channel(self):
        # Assert in channel
        assert self.test_chan.in_channel
        # Send command
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "leave "+self.test_chan.name))
        # Check response data
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0].text.lower()
        assert self.test_chan.name in data[0].text.lower()
        # Check that test channel is not in the channel anymore
        assert not self.test_chan.in_channel
