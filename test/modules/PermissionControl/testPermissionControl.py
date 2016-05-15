import unittest

from modules.PermissionControl import Permissions
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
