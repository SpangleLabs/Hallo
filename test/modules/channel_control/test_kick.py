from events import EventMessage, EventKick
from server import Server
from test.server_mock import ServerMock


def test_kick_not_irc(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = "NOT_IRC"
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    chan1.add_user(user1)
    chan1.add_user(
        serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    )
    try:
        hallo.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "kick"))
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "only available for irc" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_0_fail(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_user1 = chan1.get_membership_by_user(user1)
    chan1_user1.is_op = False
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "kick"))
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "specify a user to kick and/or a channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1priv_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1priv_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user1.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1priv_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1priv(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user1
        assert "kicked " + user1.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1chan_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: This doesn't function, if 1 argument, it's assumed to be a user, not a channel."""
    pass


def test_kick_1chan_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan2.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user1.name + " is not in " + chan2.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1chan_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan2.add_user(user1)
    chan2.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1chan(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan2.add_user(user1)
    chan2.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user1
        assert "kicked " + user1.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1user_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: Does not make sense, hallo must be in channel to receive message on it."""
    pass


def test_kick_1user_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1user_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_1user(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanuser_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 test_user2")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanuser_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'channel user' in privmsg, and user is not in channel, function will assume it was
    given 'channel message'"""
    pass


def test_kick_2privchanuser_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 test_user2")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanuser(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 test_user2")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanmsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = False
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanmsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user1.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanmsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privchanmsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user1
        assert data[0].kick_message == "goodbye"
        assert "kicked " + user1.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privuserchan_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = False
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privuserchan_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privuserchan_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2privuserchan(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2chanuser_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'channel user' and not in channel, will assume 'user msg'"""
    pass


def test_kick_2chanuser_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'channel user' and user not there, will assume 'channel msg'"""
    pass


def test_kick_2chanuser_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 test_user2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2chanuser(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 test_user2")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert "kicked " + user2.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2chanmsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'chan msg' and not in channel, will assume 'user msg'"""
    pass


def test_kick_2chanmsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 goodbye")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user1.name + " is not in " + chan2.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2chanmsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user1)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 goodbye")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2chanmsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user1)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 goodbye")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user1
        assert data[0].kick_message == "goodbye"
        assert "kicked " + user1.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2userchan_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'user channel' and not in channel, will assume 'user msg'"""
    pass


def test_kick_2userchan_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 test_chan2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan2.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2userchan_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 test_chan2")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2userchan(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 test_chan2")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert "kicked " + user2.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2usermsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: Does not make sense, hallo must be in channel to receive message on it."""
    pass


def test_kick_2usermsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 goodbye")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2usermsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 goodbye")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_2usermsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 goodbye")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert data[0].kick_message == "goodbye"
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanusermsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = False
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 test_user2 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanusermsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: if given 'chan user msg' and user not in channel, will assume 'chan msg'"""
    pass


def test_kick_3privchanusermsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 test_user2 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanusermsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 test_user2 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanmsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = False
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanmsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user1.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanmsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privchanmsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_chan1 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user1
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user1.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privuserchanmsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = False
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privuserchanmsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privuserchanmsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1 goodbye now")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3privuserchanmsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "kick test_user2 test_chan1 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3chanusermsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'channel user msg' and not in channel, will assume 'user msg'"""
    pass


def test_kick_3chanusermsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'chan user msg' and user not in channel, will assume 'chan msg'"""
    pass


def test_kick_3chanusermsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 test_user2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3chanusermsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 test_user2 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user2.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3chanmsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'channel msg' and not in channel, will assume 'user msg'"""
    pass


def test_kick_3chanmsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user1.name + " is not in " + chan2.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3chanmsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user1)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3chanmsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user1)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_chan2 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user1
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user1.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3userchanmsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: If given 'user channel msg' and not in channel, will assume 'user msg'"""
    pass


def test_kick_3userchanmsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 test_chan2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan2.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3userchanmsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 test_chan2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3userchanmsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    chan2.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    chan2.add_user(user2)
    chan2.add_user(user_hallo)
    chan2_hallo = chan2.get_membership_by_user(user_hallo)
    chan2_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 test_chan2 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan2
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user2.name + " from " + chan2.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3usermsg_not_in_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    """Placeholder: Does not make sense, hallo must be in channel to receive message on it."""
    pass


def test_kick_3usermsg_user_not_there(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert user2.name + " is not in " + chan1.name in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3usermsg_no_power(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 goodbye now")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        hallo.remove_server(serv1)


def test_kick_3usermsg(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user2)
    chan1.add_user(user_hallo)
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "kick test_user2 goodbye now")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].channel == chan1
        assert data[0].__class__ == EventKick
        assert data[1].__class__ == EventMessage
        assert data[0].kicked_user == user2
        assert data[0].kick_message == "goodbye now"
        assert "kicked " + user2.name + " from " + chan1.name in data[1].text.lower()
    finally:
        hallo.remove_server(serv1)
