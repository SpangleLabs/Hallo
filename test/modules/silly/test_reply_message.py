import re

from modules.silly import ReplyMessage
from test.server_mock import ServerMock


def test_init():
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
        ReplyMessage("hello ((((")
        assert (
            False
        ), "Invalid regex should not be able to create a valid ReplyMessage object"
    except re.error:
        pass


def test_add_response():
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


def test_add_whitelist():
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


def test_add_blacklist():
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


def test_check_response(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"silly"})
    # Setup common testing objects
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
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
    assert (
        rm4.check_response("test", user1, chan1)
        == "response test_user1 test_chan1 test_serv1"
    )


def test_check_destination(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"silly"})
    serv_name1 = "test_serv1"
    serv_name2 = "test_serv2"
    serv_name3 = "test_serv3"
    chan_name1 = "test_chan1"
    chan_name2 = "test_chan2"
    chan_name3 = "test_chan3"
    chan_name4 = "test_chan4"
    chan_name5 = "test_chan5"
    # Set up test destinations
    serv1 = ServerMock(hallo)
    serv2 = ServerMock(hallo)
    serv3 = ServerMock(hallo)
    serv1.name = serv_name1
    serv2.name = serv_name2
    serv3.name = serv_name3
    chan1 = serv1.get_channel_by_address(chan_name1.lower(), chan_name1)
    chan2 = serv1.get_channel_by_address(chan_name2.lower(), chan_name2)
    chan3 = serv2.get_channel_by_address(chan_name3.lower(), chan_name3)
    chan4 = serv3.get_channel_by_address(chan_name4.lower(), chan_name4)
    chan5 = serv3.get_channel_by_address(chan_name5.lower(), chan_name5)
    # Check when no whitelist or blacklist
    rm = ReplyMessage("test")
    assert rm.check_destination(chan1), "check_destination() not working without list"
    assert rm.check_destination(chan2), "check_destination() not working without list"
    assert rm.check_destination(chan3), "check_destination() not working without list"
    assert rm.check_destination(chan4), "check_destination() not working without list"
    assert rm.check_destination(chan5), "check_destination() not working without list"
    # Add a blacklist for a specific channel on a specific server
    rm.add_blacklist(serv_name1, chan_name1)
    assert not rm.check_destination(
        chan1
    ), "check_destination() not working with blacklist"
    assert rm.check_destination(chan2), "check_destination() not working with blacklist"
    assert rm.check_destination(chan3), "check_destination() not working with blacklist"
    assert rm.check_destination(chan4), "check_destination() not working with blacklist"
    assert rm.check_destination(chan5), "check_destination() not working with blacklist"
    # Add a whitelist for a specific channel on a specific server
    rm.add_whitelist(serv_name3, chan_name5)
    assert not rm.check_destination(
        chan1
    ), "check_destination() not working with blacklist"
    assert not rm.check_destination(
        chan2
    ), "check_destination() not working with blacklist"
    assert not rm.check_destination(
        chan3
    ), "check_destination() not working with blacklist"
    assert not rm.check_destination(
        chan4
    ), "check_destination() not working with blacklist"
    assert rm.check_destination(chan5), "check_destination() not working with blacklist"


def test_xml():
    rm1_regex = "\\btest[0-9]+\\b"
    rm1_resp1 = "response1"
    rm1_resp2 = "response2 {USER} {CHANNEL} {SERVER}"
    rm1_resp3 = "<response>"
    rm1_serv1 = "serv1"
    rm1_serv2 = "serv2"
    rm1_serv3 = "serv3"
    rm1_chan1 = "chan1"
    rm1_chan2 = "chan2"
    rm1_chan3 = "chan3"
    rm1 = ReplyMessage(rm1_regex)
    rm1.add_response(rm1_resp1)
    rm1.add_response(rm1_resp2)
    rm1.add_response(rm1_resp3)
    rm1.add_whitelist(rm1_serv1, rm1_chan1)
    rm1.add_blacklist(rm1_serv2, rm1_chan2)
    rm1.add_blacklist(rm1_serv3, rm1_chan3)
    rm1_xml = rm1.to_xml()
    rm1_obj = ReplyMessage.from_xml(rm1_xml)
    assert rm1_obj.prompt.pattern == rm1.prompt.pattern
    assert len(rm1_obj.response_list) == len(rm1.response_list)
    for resp in rm1_obj.response_list:
        assert resp in rm1.response_list
    assert len(rm1_obj.whitelist) == len(rm1.whitelist)
    for white_serv in rm1_obj.whitelist:
        assert white_serv in rm1.whitelist
        for white_chan in rm1_obj.whitelist[white_serv]:
            assert white_chan in rm1.whitelist[white_serv]
    assert len(rm1_obj.blacklist) == len(rm1.blacklist)
    for black_serv in rm1_obj.blacklist:
        assert black_serv in rm1.blacklist
        for black_chan in rm1_obj.blacklist[black_serv]:
            assert black_chan in rm1.blacklist[black_serv]
