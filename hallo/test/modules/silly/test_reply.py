import urllib.request

import pytest

from hallo.events import EventMessage
from hallo.inc.commons import Commons
from hallo.modules.silly import Reply
from hallo.test.server_mock import ServerMock


def test_run(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "reply")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower()


def test_reply_passive(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "beep")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "boop" == data[0].text.lower()


def test_reply_beep(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check beep/boop works
    response = reply_obj.passive_run(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "beep"), test_hallo
    )
    assert response.text == "boop"
    # Check that it doesn't respond if beep is in the message
    response = reply_obj.passive_run(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "it goes beep"), test_hallo
    )
    assert response is None


def test_reply_pew(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check pewpew
    response = reply_obj.passive_run(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "pew"), test_hallo
    )
    assert response.text == "pew pew"
    # Check blacklist
    serv1 = ServerMock(test_hallo)
    serv1.name = "canternet"
    chan1 = serv1.get_channel_by_address("#ukofequestria".lower(), "#ukofequestria")
    user1 = serv1.get_user_by_address("test_user".lower(), "test_user")
    response = reply_obj.passive_run(EventMessage(serv1, chan1, user1, "pew"), test_hallo)
    assert response is None


@pytest.mark.external_integration
def test_reply_haskell(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check haskell.jpg
    response = reply_obj.passive_run(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "haskell.jpg"), test_hallo
    )
    assert response is None
    # Check on correct channel
    serv1 = ServerMock(test_hallo)
    serv1.name = "shadowworld"
    chan1 = serv1.get_channel_by_address(
        "#ecco-the-dolphin".lower(), "#ecco-the-dolphin"
    )
    user1 = serv1.get_user_by_address("test_user".lower(), "test_user")
    response = reply_obj.passive_run(
        EventMessage(serv1, chan1, user1, "haskell.jpg"), test_hallo
    )
    assert "http" in response.text.lower()
    assert "haskell.jpg" in response.text.lower()
    # Check image exists
    page_request = urllib.request.Request(response.text)
    page_opener = urllib.request.build_opener()
    response_data = page_opener.open(page_request).read()
    assert len(response_data) > 0, "haskell.jpg image does not exist."


def test_reply_podbay_doors(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check pod bay doors
    response = reply_obj.passive_run(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "open the pod bay doors hallo."
        ),
        test_hallo,
    )
    assert test_hallo.test_user.name in response.text
    assert "i'm sorry" in response.text.lower()
    assert "afraid i cannot do that" in response.text.lower()


def test_reply_irc_client(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check irc client response
    response = reply_obj.passive_run(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "Which IRC client should I use?"
        ),
        test_hallo,
    )
    assert "irssi" in response.text
    assert "hexchat" in response.text
    assert "mibbit" in response.text


def test_reply_who_hallo(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check what is hallo response
    response = reply_obj.passive_run(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "What is hallo?"), test_hallo
    )
    assert "built by dr-spangle" in response.text


@pytest.mark.external_integration
def test_reply_mfw(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    reply_func = test_hallo.function_dispatcher.get_function_by_name("reply")
    reply_obj = test_hallo.function_dispatcher.get_function_object(reply_func)  # type: Reply
    # Check MFW produces response
    response = reply_obj.passive_run(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "MFW"), test_hallo
    )
    assert "http" in response.text
    # Check multiple times
    for _ in range(10):
        response = reply_obj.passive_run(
            EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "MFW"), test_hallo
        )
        assert "http" in response.text
        response_url = "http" + response.text.split("http")[1]
        page_request = urllib.request.Request(response_url)
        page_opener = urllib.request.build_opener()
        resp_data = page_opener.open(page_request).read()
        assert len(resp_data) > 0
        # Check upper case url
        response_url_upper = Commons.upper(response_url)
        page_request = urllib.request.Request(response_url_upper)
        page_opener = urllib.request.build_opener()
        resp_data_upper = page_opener.open(page_request).read()
        assert len(resp_data_upper) > 0
