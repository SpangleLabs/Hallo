import re
import unittest

from modules.Silly import ReplyMessage
from test.TestBase import TestBase


class ReplyTest(TestBase, unittest.TestCase):

    def test_reply(self):
        pass


class ReplyMessageTest(unittest.TestCase):

    def test_init(self):
        # Create reply message
        rm = ReplyMessage("hello")
        assert rm.prompt.pattern == "hello"
        assert rm.response_list == []
        assert rm.whitelist == {}
        assert rm.blacklist == {}
        # Another, with more regex
        rm2 = ReplyMessage("hello (world|universe|computer)!{1,5}")
        assert rm2.prompt.pattern == "hello (world|universe|computer)!{1,5}"
        # Another, invalid regex
        try:
            rm3 = ReplyMessage("hello ((((")
            assert False, "Invalid regex should not be able to create a valid ReplyMessage object"
        except re.error:
            pass

    def test_add_response(self):
        # Create reply message
        rm = ReplyMessage("test")
        # Add response
        rm.add_response("reply2")
        # Check
        assert len(rm.response_list) == 1
        assert rm.response_list[0] == "reply2"
        # Add another
        rm.add_response("reply3")
        assert len(rm.response_list) == 2
        assert rm.response_list[1] == "reply3"

    def test_add_whitelist(self):
        # Create reply message
        rm = ReplyMessage("test")
        # Add whitelist element
        rm.add_whitelist("test_server", "test_chan")
        assert len(rm.whitelist) == 1
        assert "test_server" in rm.whitelist
        assert len(rm.whitelist["test_server"]) == 1
        assert "test_chan" in rm.whitelist["test_server"]
        # Add same-server whitelist element
        rm.add_whitelist("test_server", "test_chan2")
        assert len(rm.whitelist) == 1
        assert "test_server" in rm.whitelist
        assert len(rm.whitelist["test_server"]) == 2
        assert "test_chan" in rm.whitelist["test_server"]
        assert "test_chan2" in rm.whitelist["test_server"]
        # Add diff-server whitelist element
        rm.add_whitelist("test_serv2", "test_chan3")
        assert len(rm.whitelist) == 2
        assert "test_serv2" in rm.whitelist
        assert len(rm.whitelist["test_serv2"]) == 1
        assert "test_chan3" in rm.whitelist["test_serv2"]

    def test_add_blacklist(self):
        # Create reply message
        rm = ReplyMessage("test")
        # Add whitelist element
        rm.add_blacklist("test_server", "test_chan")
        assert len(rm.blacklist) == 1
        assert "test_server" in rm.blacklist
        assert len(rm.blacklist["test_server"]) == 1
        assert "test_chan" in rm.blacklist["test_server"]
        # Add same-server whitelist element
        rm.add_blacklist("test_server", "test_chan2")
        assert len(rm.blacklist) == 1
        assert "test_server" in rm.blacklist
        assert len(rm.blacklist["test_server"]) == 2
        assert "test_chan" in rm.blacklist["test_server"]
        assert "test_chan2" in rm.blacklist["test_server"]
        # Add diff-server whitelist element
        rm.add_blacklist("test_serv2", "test_chan3")
        assert len(rm.blacklist) == 2
        assert "test_serv2" in rm.blacklist
        assert len(rm.blacklist["test_serv2"]) == 1
        assert "test_chan3" in rm.blacklist["test_serv2"]

    def test_check_response(self):
        pass

    def test_check_destination(self):
        pass
