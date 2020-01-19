from modules.silly import ReplyMessageList, ReplyMessage
from test.server_mock import ServerMock


def test_init():
    # Create reply message list
    rml = ReplyMessageList()
    assert rml.reply_message_list == set(), "Reply message list did not initialise with empty list."


def test_add_reply_message():
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


def test_get_response(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"silly"})
    # Setup common testing objects
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
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
