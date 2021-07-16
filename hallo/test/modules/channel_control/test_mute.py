from hallo.events import EventMessage, EventMode
from hallo.server import Server
from hallo.test.server_mock import ServerMock


def test_mute_not_irc(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = "NOT_IRC"
    test_hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    chan1.add_user(user1)
    chan1.add_user(
        serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    )
    try:
        test_hallo.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "mute"))
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "only available for irc" in data[0].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_privmsg(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    try:
        test_hallo.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "mute"))
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "can't set mute on a private message" in data[0].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_0_no_power(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_user1 = chan1.get_membership_by_user(user1)
    chan1_user1.is_op = False
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        test_hallo.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "mute"))
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_0(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
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
        test_hallo.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "mute"))
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].channel == chan1
        assert data[0].__class__ == EventMode
        assert data[1].__class__ == EventMessage
        assert data[0].mode_changes == "+m"
        assert "set mute in " + chan1.name in data[1].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_1_not_known(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
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
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "mute test_chan2")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "test_chan2 is not known" in data[0].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_1_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    chan2 = serv1.get_channel_by_address("test_chan2", "test_chan2")
    chan2.in_channel = False
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_user1 = chan1.get_membership_by_user(user1)
    chan1_user1.is_op = False
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = True
    try:
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "mute test_chan2")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "not in that channel" in data[0].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_1_no_power(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan1.in_channel = True
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
    chan1.add_user(user1)
    chan1.add_user(user_hallo)
    chan1_user1 = chan1.get_membership_by_user(user1)
    chan1_user1.is_op = False
    chan1_hallo = chan1.get_membership_by_user(user_hallo)
    chan1_hallo.is_op = False
    try:
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "mute test_chan1")
        )
        data = serv1.get_send_data(1, user1, EventMessage)
        assert "error" in data[0].text.lower()
        assert "don't have power" in data[0].text.lower()
    finally:
        test_hallo.remove_server(serv1)


def test_mute_1(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    serv1.type = Server.TYPE_IRC
    test_hallo.add_server(serv1)
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
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, None, user1, "mute test_chan1")
        )
        data = serv1.get_send_data(2)
        assert "error" not in data[1].text.lower()
        assert data[0].channel == chan1
        assert data[1].user == user1
        assert data[0].__class__ == EventMode
        assert data[1].__class__ == EventMessage
        assert data[0].mode_changes == "+m"
        assert "set mute in " + chan1.name in data[1].text.lower()
    finally:
        test_hallo.remove_server(serv1)
