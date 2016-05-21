import unittest

from Hallo import Hallo
from PermissionMask import PermissionMask
from Server import Server
from UserGroup import UserGroup
from modules.PermissionControl import Permissions
from test.ServerMock import ServerMock
from test.TestBase import TestBase
import modules.PermissionControl


class PermissionControlTest(TestBase, unittest.TestCase):

    def test_run_add_on(self):
        # Set up a test hallo and server and channel and user
        hallo1 = Hallo()
        perm0 = PermissionMask()
        hallo1.permission_mask = perm0
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm1 = PermissionMask()
        serv1.permission_mask = perm1
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm2 = PermissionMask()
        chan1.permission_mask = perm2
        user1 = serv1.get_user_by_name("test_user1")
        perm3 = PermissionMask()
        user1.permission_mask = perm3
        # Get permission mask of given channel
        test_right = "test_right"
        self.function_dispatcher.dispatch("permissions server=test_serv1 channel=test_chan1 "+test_right+" on",
                                          user1, chan1)
        data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "set "+test_right+" to true" in data[0][0].lower()
        assert test_right in perm2.rights_map
        assert perm2.rights_map[test_right]

    def test_run_set_on(self):
        # Set up a test hallo and server and channel and user
        hallo1 = Hallo()
        perm0 = PermissionMask()
        hallo1.permission_mask = perm0
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm1 = PermissionMask()
        serv1.permission_mask = perm1
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm2 = PermissionMask()
        chan1.permission_mask = perm2
        user1 = serv1.get_user_by_name("test_user1")
        perm3 = PermissionMask()
        user1.permission_mask = perm3
        # Get permission mask of given channel
        test_right = "test_right"
        perm2.set_right(test_right, False)
        self.function_dispatcher.dispatch("permissions server=test_serv1 channel=test_chan1 "+test_right+" on",
                                          user1, chan1)
        data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "set "+test_right+" to true" in data[0][0].lower()
        assert test_right in perm2.rights_map
        assert perm2.rights_map[test_right]

    def test_run_add_off(self):
        # Set up a test hallo and server and channel and user
        hallo1 = Hallo()
        perm0 = PermissionMask()
        hallo1.permission_mask = perm0
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm1 = PermissionMask()
        serv1.permission_mask = perm1
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm2 = PermissionMask()
        chan1.permission_mask = perm2
        user1 = serv1.get_user_by_name("test_user1")
        perm3 = PermissionMask()
        user1.permission_mask = perm3
        # Get permission mask of given channel
        test_right = "test_right"
        self.function_dispatcher.dispatch("permissions server=test_serv1 channel=test_chan1 "+test_right+" off",
                                          user1, chan1)
        data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "set "+test_right+" to false" in data[0][0].lower()
        assert test_right in perm2.rights_map
        assert not perm2.rights_map[test_right]

    def test_run_set_off(self):
        # Set up a test hallo and server and channel and user
        hallo1 = Hallo()
        perm0 = PermissionMask()
        hallo1.permission_mask = perm0
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm1 = PermissionMask()
        serv1.permission_mask = perm1
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm2 = PermissionMask()
        chan1.permission_mask = perm2
        user1 = serv1.get_user_by_name("test_user1")
        perm3 = PermissionMask()
        user1.permission_mask = perm3
        # Get permission mask of given channel
        test_right = "test_right"
        perm2.set_right(test_right, True)
        self.function_dispatcher.dispatch("permissions server=test_serv1 channel=test_chan1 "+test_right+" on",
                                          user1, chan1)
        data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "set "+test_right+" to true" in data[0][0].lower()
        assert test_right in perm2.rights_map
        assert perm2.rights_map[test_right]

    def test_run_fail_args(self):
        # Set up a test hallo and server and channel and user
        hallo1 = Hallo()
        perm0 = PermissionMask()
        hallo1.permission_mask = perm0
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm1 = PermissionMask()
        serv1.permission_mask = perm1
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm2 = PermissionMask()
        chan1.permission_mask = perm2
        user1 = serv1.get_user_by_name("test_user1")
        perm3 = PermissionMask()
        user1.permission_mask = perm3
        # Get permission mask of given channel
        test_right = "test_right"
        perm1.set_right(test_right, True)
        self.function_dispatcher.dispatch("permissions server=test_serv1 "+test_right, user1, chan1)
        data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert "a location, a right and the value" in data[0][0].lower()
        assert test_right in perm1.rights_map
        assert perm1.rights_map[test_right]

    def test_run_fail_location(self):
        pass

    def test_run_fail_not_bool(self):
        pass


class FindPermissionMaskTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.perm_cont = Permissions()

    def tearDown(self):
        super().tearDown()

    def test_3_fail(self):
        try:
            self.perm_cont.find_permission_mask(["a", "b", "c"], self.test_user, self.test_chan)
            assert False, "Exception should be thrown if more than 2 arguments passed."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "too many filters" in str(e).lower()

    def test_2_no_server(self):
        try:
            self.perm_cont.find_permission_mask(["channel=chan1", "user=user1"], self.test_user, self.test_chan)
            assert False, "Exception should be thrown if 2 arguments and neither is server."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "no server name found" in str(e).lower()

    def test_2_no_server_by_name(self):
        try:
            self.perm_cont.find_permission_mask(["server=no_server_by_name", "chan=test_chan1"],
                                                self.test_user, self.test_user)
            assert False, "Exception should be thrown if server does not exist."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "no server exists by that name" in str(e).lower()

    def test_2_server_chan(self):
        # Set up a test server and channel
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        # Get permission mask of given channel
        data = self.perm_cont.find_permission_mask(["server=test_serv1", "channel=test_chan1"],
                                                   self.test_user, self.test_chan)
        assert perm1 == data, "Did not find the correct permission mask."

    def test_2_server_user(self):
        # Set up a test server and user
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        self.hallo.add_server(serv1)
        user1 = serv1.get_user_by_name("test_user1")
        perm1 = PermissionMask()
        user1.permission_mask = perm1
        # Get permission mask of given channel
        data = self.perm_cont.find_permission_mask(["server=test_serv1", "user=test_user1"],
                                                   self.test_user, self.test_chan)
        assert perm1 == data, "Did not find the correct permission mask."

    def test_2_server_no_chan_user(self):
        # Set up a test server and channel and user
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permission mask of given channel
        try:
            data = self.perm_cont.find_permission_mask(["server=test_serv1", "core"],
                                                       user1, chan1)
            assert False, "Should have failed to find any permission mask."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "server but not channel or user" in str(e).lower()

    def test_1_hallo(self):
        # Set up a test hallo and server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permission of hallo
        data = self.perm_cont.find_permission_mask(["hallo"], user1, chan1)
        assert data == perm3, "Did not find the correct permission mask."

    def test_1_server(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permissions of current server
        data = self.perm_cont.find_permission_mask(["server"], user1, chan1)
        assert data == perm0, "Did not find the correct permission mask."

    def test_1_server_no_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permissions of current server
        try:
            data = self.perm_cont.find_permission_mask(["server=test_serv2"], user1, chan1)
            assert False, "Find permission mask should have failed."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "no server exists by that name" in str(e).lower()

    def test_1_server_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permissions of current server
        data = self.perm_cont.find_permission_mask(["server=test_serv1"], user1, chan1)
        assert data == perm0, "Did not find correct permission mask"

    def test_1_channel(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permissions of current channel
        data = self.perm_cont.find_permission_mask(["channel"], user1, chan1)
        assert data == perm1, "Did not find the correct permission mask."

    def test_1_channel_privmsg(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Try to get permissions of current channel from a privmsg
        try:
            data = self.perm_cont.find_permission_mask(["channel"], user1, None)
            assert False, "Should not have managed to get permission mask."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "can't set generic channel permissions in a privmsg" in str(e).lower()

    def test_1_channel_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        chan2 = serv1.get_channel_by_name("test_chan2")
        perm4 = PermissionMask()
        chan2.permission_mask = perm4
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permissions of current channel
        data = self.perm_cont.find_permission_mask(["channel=test_chan2"], user1, chan1)
        assert data == perm4, "Did not find the correct permission mask."

    def test_1_user_group_no_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        group1 = UserGroup("test_group1", hallo1)
        perm4 = PermissionMask()
        group1.permission_mask = perm4
        hallo1.add_user_group(group1)
        # Try to get permissions of non-existent user group
        try:
            data = self.perm_cont.find_permission_mask(["user_group=test_group2"], user1, chan1)
            assert False, "Find permission mask should have failed."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "no user group exists by that name" in str(e).lower()

    def test_1_user_group_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        group1 = UserGroup("test_group1", hallo1)
        perm4 = PermissionMask()
        group1.permission_mask = perm4
        hallo1.add_user_group(group1)
        # Get permissions of specified user group
        data = self.perm_cont.find_permission_mask(["user_group=test_group1"], user1, chan1)
        assert data == perm4, "Did not find the correct permission mask."

    def test_1_user_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        user2 = serv1.get_user_by_name("test_user2")
        perm4 = PermissionMask()
        user2.permission_mask = perm4
        # Get permissions of specified user
        data = self.perm_cont.find_permission_mask(["user=test_user2"], user1, chan1)
        assert data == perm4, "Did not find the correct permission mask."

    def test_1_user_just_name(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        chan1.add_user(user1)
        user2 = serv1.get_user_by_name("test_user2")
        perm4 = PermissionMask()
        user2.permission_mask = perm4
        chan1.add_user(user2)
        # Get permissions of specified user in channel
        data = self.perm_cont.find_permission_mask(["test_user2"], user1, chan1)
        assert data == perm4, "Did not find the correct permission mask."

    def test_1_user_just_name_not_in_channel(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        chan1.add_user(user1)
        user2 = serv1.get_user_by_name("test_user2")
        perm4 = PermissionMask()
        user2.permission_mask = perm4
        # Get permissions of specified user group
        try:
            data = self.perm_cont.find_permission_mask(["test_user2"], user1, chan1)
            assert False, "Find permission mask should have failed."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "i can't find that permission mask" in str(e).lower()

    def test_1_user_just_name_privmsg(self):
        # Set up a test server and channel and user
        hallo1 = Hallo()
        perm3 = PermissionMask()
        hallo1.permission_mask = perm3
        serv1 = ServerMock(hallo1)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        hallo1.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        chan1.add_user(user1)
        user2 = serv1.get_user_by_name("test_user2")
        perm4 = PermissionMask()
        user2.permission_mask = perm4
        # Get permissions of specified user group
        try:
            data = self.perm_cont.find_permission_mask(["test_user2"], user1, None)
            assert False, "Find permission mask should have failed."
        except modules.PermissionControl.PermissionControlException as e:
            assert "error" in str(e).lower()
            assert "i can't find that permission mask" in str(e).lower()
