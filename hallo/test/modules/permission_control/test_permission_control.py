from hallo.events import EventMessage
from hallo.hallo import Hallo
from hallo.permission_mask import PermissionMask
from hallo.test.server_mock import ServerMock


def test_run_add_on(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm0 = PermissionMask()
    hallo1.permission_mask = perm0
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm1 = PermissionMask()
    serv1.permission_mask = perm1
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm2 = PermissionMask()
    chan1.permission_mask = perm2
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    perm3 = PermissionMask()
    user1.permission_mask = perm3
    # Get permission mask of given channel
    test_right = "test_right"
    hallo.function_dispatcher.dispatch(
        EventMessage(
            serv1,
            chan1,
            user1,
            "permissions server=test_serv1 channel=test_chan1 " + test_right + " on",
        )
    )
    data = serv1.get_send_data(1, chan1, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "set " + test_right + " to true" in data[0].text.lower()
    assert test_right in perm2.rights_map
    assert perm2.rights_map[test_right]


def test_run_set_on(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm0 = PermissionMask()
    hallo1.permission_mask = perm0
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm1 = PermissionMask()
    serv1.permission_mask = perm1
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm2 = PermissionMask()
    chan1.permission_mask = perm2
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    perm3 = PermissionMask()
    user1.permission_mask = perm3
    # Get permission mask of given channel
    test_right = "test_right"
    perm2.set_right(test_right, False)
    hallo.function_dispatcher.dispatch(
        EventMessage(
            serv1,
            chan1,
            user1,
            "permissions server=test_serv1 channel=test_chan1 " + test_right + " on",
        )
    )
    data = serv1.get_send_data(1, chan1, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "set " + test_right + " to true" in data[0].text.lower()
    assert test_right in perm2.rights_map
    assert perm2.rights_map[test_right]


def test_run_add_off(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm0 = PermissionMask()
    hallo1.permission_mask = perm0
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm1 = PermissionMask()
    serv1.permission_mask = perm1
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm2 = PermissionMask()
    chan1.permission_mask = perm2
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    perm3 = PermissionMask()
    user1.permission_mask = perm3
    # Get permission mask of given channel
    test_right = "test_right"
    hallo.function_dispatcher.dispatch(
        EventMessage(
            serv1,
            chan1,
            user1,
            "permissions server=test_serv1 channel=test_chan1 " + test_right + " off",
        )
    )
    data = serv1.get_send_data(1, chan1, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "set " + test_right + " to false" in data[0].text.lower()
    assert test_right in perm2.rights_map
    assert not perm2.rights_map[test_right]


def test_run_set_off(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm0 = PermissionMask()
    hallo1.permission_mask = perm0
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm1 = PermissionMask()
    serv1.permission_mask = perm1
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm2 = PermissionMask()
    chan1.permission_mask = perm2
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    perm3 = PermissionMask()
    user1.permission_mask = perm3
    # Get permission mask of given channel
    test_right = "test_right"
    perm2.set_right(test_right, True)
    hallo.function_dispatcher.dispatch(
        EventMessage(
            serv1,
            chan1,
            user1,
            "permissions server=test_serv1 channel=test_chan1 " + test_right + " off",
        )
    )
    data = serv1.get_send_data(1, chan1, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "set " + test_right + " to false" in data[0].text.lower()
    assert test_right in perm2.rights_map
    assert not perm2.rights_map[test_right]


def test_run_fail_args(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm0 = PermissionMask()
    hallo1.permission_mask = perm0
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm1 = PermissionMask()
    serv1.permission_mask = perm1
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm2 = PermissionMask()
    chan1.permission_mask = perm2
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    perm3 = PermissionMask()
    user1.permission_mask = perm3
    # Get permission mask of given channel
    test_right = "test_right"
    perm1.set_right(test_right, True)
    hallo.function_dispatcher.dispatch(
        EventMessage(serv1, chan1, user1, "permissions server=test_serv1 " + test_right)
    )
    data = serv1.get_send_data(1, chan1, EventMessage)
    assert "error" in data[0].text.lower()
    assert "a location, a right and the value" in data[0].text.lower()
    assert test_right in perm1.rights_map
    assert perm1.rights_map[test_right]


def test_run_fail_not_bool(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm0 = PermissionMask()
    hallo1.permission_mask = perm0
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm1 = PermissionMask()
    serv1.permission_mask = perm1
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm2 = PermissionMask()
    chan1.permission_mask = perm2
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    perm3 = PermissionMask()
    user1.permission_mask = perm3
    # Get permission mask of given channel
    test_right = "test_right"
    perm1.set_right(test_right, True)
    hallo.function_dispatcher.dispatch(
        EventMessage(
            serv1,
            chan1,
            user1,
            "permissions server=test_serv1 " + test_right + " yellow",
        )
    )
    data = serv1.get_send_data(1, chan1, EventMessage)
    assert "error" in data[0].text.lower()
    assert "don't understand your boolean value" in data[0].text.lower()
    assert test_right in perm1.rights_map
    assert perm1.rights_map[test_right]
