import unittest

from Hallo import Hallo
from PermissionMask import PermissionMask
from modules.PermissionControl import Permissions
from test.ServerMock import ServerMock
from test.TestBase import TestBase
import modules.PermissionControl


class PermissionControlTest(TestBase, unittest.TestCase):

    def test_run(self):
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
                                                       self.test_user, self.test_chan)
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
        self.hallo.add_server(serv1)
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
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        perm0 = PermissionMask()
        serv1.permission_mask = perm0
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        perm1 = PermissionMask()
        chan1.permission_mask = perm1
        user1 = serv1.get_user_by_name("test_user1")
        perm2 = PermissionMask()
        user1.permission_mask = perm2
        # Get permissions of current server
        data = self.perm_cont.find_permission_mask(["server"], user1, chan1)
        assert data == perm0, "Did not find the correct permission mask."
