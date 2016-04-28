import re
import unittest
import urllib.request

from Function import Function
from Server import Server
from modules.Silly import ReplyMessage, ReplyMessageList
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class ReplyTest(TestBase, unittest.TestCase):

    def test_run(self):
        self.function_dispatcher.dispatch("reply", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_reply_passive(self):
        self.function_dispatcher.dispatch_passive(Function.EVENT_MESSAGE, "beep",
                                                  self.server, self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "boop" == data[0][0].lower()

    def test_reply_beep(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check beep/boop works
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "beep",
                                         self.server, self.test_user, self.test_chan)
        assert response == "boop"
        # Check that it doesn't respond if beep is in the message
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "it goes beep",
                                         self.server, self.test_user, self.test_chan)
        assert response is None

    def test_reply_pew(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check pewpew
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "pew",
                                         self.server, self.test_user, self.test_chan)
        assert response == "pew pew"
        # Check blacklist
        serv1 = ServerMock(None)
        serv1.name = "canternet"
        chan1 = serv1.get_channel_by_name("#ukofequestria")
        user1 = serv1.get_user_by_name("test_user")
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "pew",
                                         serv1, user1, chan1)
        assert response is None

    def test_reply_haskell(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check haskell.jpg
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "haskell.jpg",
                                         self.server, self.test_user, self.test_chan)
        assert response is None
        # Check on correct channel
        serv1 = ServerMock(None)
        serv1.name = "shadowworld"
        chan1 = serv1.get_channel_by_name("#ecco-the-dolphin")
        user1 = serv1.get_user_by_name("test_user")
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "haskell.jpg",
                                         serv1, user1, chan1)
        assert "http" in response.lower()
        assert "haskell.jpg" in response.lower()
        # Check image exists
        page_request = urllib.request.Request(response)
        page_opener = urllib.request.build_opener()
        response_data = page_opener.open(page_request).read()
        assert len(response) > 0, "haskell.jpg image does not exist."

    def test_reply_podbay_doors(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check pod bay doors
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "open the pod bay doors hallo.",
                                         self.server, self.test_user, self.test_chan)
        assert self.test_user.name in response
        assert "i'm sorry" in response.lower()
        assert "afraid i cannot do that" in response.lower()

    def test_reply_irc_client(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check irc client response
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "Which IRC client should I use?",
                                         self.server, self.test_user, self.test_chan)
        assert "irssi" in response
        assert "hexchat" in response
        assert "mibbit" in response

    def test_reply_who_hallo(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check what is hallo response
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "What is hallo?",
                                         self.server, self.test_user, self.test_chan)
        assert "built by dr-spangle" in response

    def test_reply_mfw(self):
        reply_func = self.function_dispatcher.get_function_by_name("reply")
        reply_obj = self.function_dispatcher.get_function_object(reply_func)
        # Check MFW produces response
        response = reply_obj.passive_run(Function.EVENT_MESSAGE, "MFW",
                                         self.server, self.test_user, self.test_chan)
        assert "http" in response
        # Check multiple times
        for _ in range(10):
            response = reply_obj.passive_run(Function.EVENT_MESSAGE, "MFW",
                                             self.server, self.test_user, self.test_chan)
            assert "http" in response
            response_url = "http" + response.split("http")[1]
            page_request = urllib.request.Request(response_url)
            page_opener = urllib.request.build_opener()
            resp_data = page_opener.open(page_request).read()
            assert len(resp_data) > 0
            # Check upper case url
            urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                              response_url)
            data = response_url.upper()
            for url in urls:
                response_url = response_url.replace(url.upper(), url)
            page_request = urllib.request.Request(response_url)
            page_opener = urllib.request.build_opener()
            resp_data_upper = page_opener.open(page_request).read()
            assert len(resp_data_upper) > 0


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
        # Setup common testing objects
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        # Test basic response works
        rm1 = ReplyMessage("test")
        rm1.add_response("response")
        assert rm1.check_response("just a test", user1, chan1) == "response"
        # Test regex pattern match
        rm2 = ReplyMessage("\\btest[0-9]+\\b")
        rm2.add_response("response")
        assert rm2.check_response("random testing", user1, chan1) is None
        assert rm2.check_response("random test here", user1, chan1) is None
        assert rm2.check_response("this is test3 I think", user1, chan1) == "response"
        assert rm2.check_response("this is test4", user1, chan1) == "response"
        # Test multi-response works
        rm3 = ReplyMessage("test")
        rm3.add_response("response1")
        rm3.add_response("response2")
        rm3.add_response("response3")
        found_responses = set()
        for _ in range(50):
            response = rm3.check_response("another test", user1, chan1)
            found_responses.add(response)
            assert response in ["response1", "response2", "response3"]
        assert len(found_responses) > 1
        # Test replacements
        rm4 = ReplyMessage("test")
        rm4.add_response("response {USER} {CHANNEL} {SERVER}")
        assert rm4.check_response("test", user1, chan1) == "response test_user1 test_chan1 test_serv1"

    def test_check_destination(self):
        serv_name1 = "test_serv1"
        serv_name2 = "test_serv2"
        serv_name3 = "test_serv3"
        chan_name1 = "test_chan1"
        chan_name2 = "test_chan2"
        chan_name3 = "test_chan3"
        chan_name4 = "test_chan4"
        chan_name5 = "test_chan5"
        # Set up test destinations
        serv1 = ServerMock(None)
        serv2 = ServerMock(None)
        serv3 = ServerMock(None)
        serv1.name = serv_name1
        serv2.name = serv_name2
        serv3.name = serv_name3
        chan1 = serv1.get_channel_by_name(chan_name1)
        chan2 = serv1.get_channel_by_name(chan_name2)
        chan3 = serv2.get_channel_by_name(chan_name3)
        chan4 = serv3.get_channel_by_name(chan_name4)
        chan5 = serv3.get_channel_by_name(chan_name5)
        # Check when no whitelist or blacklist
        rm = ReplyMessage("test")
        assert rm.check_destination(chan1), "check_destination() not working without list"
        assert rm.check_destination(chan2), "check_destination() not working without list"
        assert rm.check_destination(chan3), "check_destination() not working without list"
        assert rm.check_destination(chan4), "check_destination() not working without list"
        assert rm.check_destination(chan5), "check_destination() not working without list"
        # Add a blacklist for a specific channel on a specific server
        rm.add_blacklist(serv_name1, chan_name1)
        assert not rm.check_destination(chan1), "check_destination() not working with blacklist"
        assert rm.check_destination(chan2), "check_destination() not working with blacklist"
        assert rm.check_destination(chan3), "check_destination() not working with blacklist"
        assert rm.check_destination(chan4), "check_destination() not working with blacklist"
        assert rm.check_destination(chan5), "check_destination() not working with blacklist"
        # Add a whitelist for a specific channel on a specific server
        rm.add_whitelist(serv_name3, chan_name5)
        assert not rm.check_destination(chan1), "check_destination() not working with blacklist"
        assert not rm.check_destination(chan2), "check_destination() not working with blacklist"
        assert not rm.check_destination(chan3), "check_destination() not working with blacklist"
        assert not rm.check_destination(chan4), "check_destination() not working with blacklist"
        assert rm.check_destination(chan5), "check_destination() not working with blacklist"


class ReplyMessageListTest(unittest.TestCase):

    def test_init(self):
        # Create reply message list
        rml = ReplyMessageList()
        assert rml.reply_message_list == set(), "Reply message list did not initialise with empty list."

    def test_add_reply_message(self):
        rml1 = ReplyMessageList()
        rm1 = ReplyMessage("test1")
        rm2 = ReplyMessage("test2")
        assert rml1.reply_message_list == set()
        rml1.add_reply_message(rm1)
        assert len(rml1.reply_message_list) == 1
        assert rm1 in rml1.reply_message_list
        rml1.add_reply_message(rm2)
        assert len(rml1.reply_message_list) == 2
        assert rm2 in rml1.reply_message_list

    def test_get_response(self):
        # Setup common testing objects
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        # Basic ReplyMessageList get_response() test
        rml1 = ReplyMessageList()
        rm1 = ReplyMessage("test1")
        rm1.add_response("response1")
        rm2 = ReplyMessage("test2")
        rm2.add_response("response2")
        rml1.add_reply_message(rm1)
        rml1.add_reply_message(rm2)
        # Check response 1 works
        assert rml1.get_response("test1", user1, chan1) == "response1"
        assert rml1.get_response("test2", user1, chan1) == "response2"
        assert rml1.get_response("test3", user1, chan1) is None
        # Check blacklists
        rml2 = ReplyMessageList()
        rm1 = ReplyMessage("test")
        rm1.add_response("response1")
        rm1.add_blacklist(serv1.name, chan1.name)
        rm2 = ReplyMessage("test")
        rm2.add_response("response2")
        rml2.add_reply_message(rm1)
        rml2.add_reply_message(rm2)
        assert rml2.get_response("test", user1, chan1) == "response2"
        # Check whitelists
        rml3 = ReplyMessageList()
        rm1 = ReplyMessage("test")
        rm1.add_response("response1")
        rm1.add_whitelist(serv1.name, "not_chan_1")
        rm2 = ReplyMessage("test")
        rm2.add_response("response2")
        rml3.add_reply_message(rm1)
        rml3.add_reply_message(rm2)
        assert rml3.get_response("test", user1, chan1) == "response2"
        # Check replacements
        rml4 = ReplyMessageList()
        rm1 = ReplyMessage("test")
        rm1.add_response("response {USER} {CHANNEL} {SERVER}")
        rml4.add_reply_message(rm1)
        assert rml4.get_response("test", user1, chan1) == "response test_user1 test_chan1 test_serv1"
