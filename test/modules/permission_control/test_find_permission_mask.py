import modules.permission_control
from hallo import Hallo
from modules.permission_control import Permissions
from permission_mask import PermissionMask
from test.server_mock import ServerMock
from user_group import UserGroup


def test_3_fail(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    try:
        perm_cont.find_permission_mask(["a", "b", "c"], test_user, test_channel)
        assert False, "Exception should be thrown if more than 2 arguments passed."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "too many filters" in str(e).lower()


def test_2_no_server(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    try:
        perm_cont.find_permission_mask(
            ["channel=chan1", "user=user1"], test_user, test_channel
        )
        assert False, "Exception should be thrown if 2 arguments and neither is server."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "no server name found" in str(e).lower()


def test_2_no_server_by_name(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    try:
        perm_cont.find_permission_mask(
            ["server=no_server_by_name", "chan=test_chan1"], test_user, test_user
        )
        assert False, "Exception should be thrown if server does not exist."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "no server exists by that name" in str(e).lower()


def test_2_server_chan(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    # Set up a test server and channel
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    # Get permission mask of given channel
    data = perm_cont.find_permission_mask(
        ["server=test_serv1", "channel=test_chan1"], test_user, test_channel
    )
    assert perm1 == data, "Did not find the correct permission mask."


def test_2_server_user(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    # Set up a test server and user
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    hallo.add_server(serv1)
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm1 = PermissionMask()
    user1.permission_mask = perm1
    # Get permission mask of given channel
    data = perm_cont.find_permission_mask(
        ["server=test_serv1", "user=test_user1"], test_user, test_channel
    )
    assert perm1 == data, "Did not find the correct permission mask."


def test_2_server_no_chan_user(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    # Set up a test server and channel and user
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    hallo.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permission mask of given channel
    try:
        perm_cont.find_permission_mask(["server=test_serv1", "core"], user1, chan1)
        assert False, "Should have failed to find any permission mask."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "server but not channel or user" in str(e).lower()


def test_1_hallo():
    perm_cont = Permissions()
    # Set up a test hallo and server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permission of hallo
    data = perm_cont.find_permission_mask(["hallo"], user1, chan1)
    assert data == perm3, "Did not find the correct permission mask."


def test_1_server():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permissions of current server
    data = perm_cont.find_permission_mask(["server"], user1, chan1)
    assert data == perm0, "Did not find the correct permission mask."


def test_1_server_no_name():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permissions of current server
    try:
        perm_cont.find_permission_mask(["server=test_serv2"], user1, chan1)
        assert False, "Find permission mask should have failed."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "no server exists by that name" in str(e).lower()


def test_1_server_name(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"permission_control"})
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permissions of current server
    data = perm_cont.find_permission_mask(["server=test_serv1"], user1, chan1)
    assert data == perm0, "Did not find correct permission mask"


def test_1_channel():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permissions of current channel
    data = perm_cont.find_permission_mask(["channel"], user1, chan1)
    assert data == perm1, "Did not find the correct permission mask."


def test_1_channel_privmsg():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Try to get permissions of current channel from a privmsg
    try:
        perm_cont.find_permission_mask(["channel"], user1, None)
        assert False, "Should not have managed to get permission mask."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "can't set generic channel permissions in a privmsg" in str(e).lower()


def test_1_channel_name():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    perm4 = PermissionMask()
    chan2.permission_mask = perm4
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    # Get permissions of current channel
    data = perm_cont.find_permission_mask(["channel=test_chan2"], user1, chan1)
    assert data == perm4, "Did not find the correct permission mask."


def test_1_user_group_no_name():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    group1 = UserGroup("test_group1", hallo1)
    perm4 = PermissionMask()
    group1.permission_mask = perm4
    hallo1.add_user_group(group1)
    # Try to get permissions of non-existent user group
    try:
        perm_cont.find_permission_mask(["user_group=test_group2"], user1, chan1)
        assert False, "Find permission mask should have failed."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "no user group exists by that name" in str(e).lower()


def test_1_user_group_name():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    group1 = UserGroup("test_group1", hallo1)
    perm4 = PermissionMask()
    group1.permission_mask = perm4
    hallo1.add_user_group(group1)
    # Get permissions of specified user group
    data = perm_cont.find_permission_mask(["user_group=test_group1"], user1, chan1)
    assert data == perm4, "Did not find the correct permission mask."


def test_1_user_name():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    perm4 = PermissionMask()
    user2.permission_mask = perm4
    # Get permissions of specified user
    data = perm_cont.find_permission_mask(["user=test_user2"], user1, chan1)
    assert data == perm4, "Did not find the correct permission mask."


def test_1_user_just_name():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    chan1.add_user(user1)
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    perm4 = PermissionMask()
    user2.permission_mask = perm4
    chan1.add_user(user2)
    # Get permissions of specified user in channel
    data = perm_cont.find_permission_mask(["test_user2"], user1, chan1)
    assert data == perm4, "Did not find the correct permission mask."


def test_1_user_just_name_not_in_channel():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    chan1.add_user(user1)
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    perm4 = PermissionMask()
    user2.permission_mask = perm4
    # Get permissions of specified user group
    try:
        perm_cont.find_permission_mask(["test_user2"], user1, chan1)
        assert False, "Find permission mask should have failed."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "i can't find that permission mask" in str(e).lower()


def test_1_user_just_name_privmsg():
    perm_cont = Permissions()
    # Set up a test server and channel and user
    hallo1 = Hallo()
    perm3 = PermissionMask()
    hallo1.permission_mask = perm3
    serv1 = ServerMock(hallo1)
    serv1.name = "test_serv1"
    perm0 = PermissionMask()
    serv1.permission_mask = perm0
    hallo1.add_server(serv1)
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    perm1 = PermissionMask()
    chan1.permission_mask = perm1
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    perm2 = PermissionMask()
    user1.permission_mask = perm2
    chan1.add_user(user1)
    user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
    perm4 = PermissionMask()
    user2.permission_mask = perm4
    # Get permissions of specified user group
    try:
        perm_cont.find_permission_mask(["test_user2"], user1, None)
        assert False, "Find permission mask should have failed."
    except modules.permission_control.PermissionControlException as e:
        assert "error" in str(e).lower()
        assert "i can't find that permission mask" in str(e).lower()
