import os
import re

import pytest

from events import EventMessage


@pytest.mark.external_integration
def test_quote(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"random"})
    # Check API key is set
    if hallo.get_api_key("mashape") is None:
        # Read from env variable
        hallo.add_api_key("mashape", os.getenv("test_api_key_mashape"))
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "random quote"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    quote_regex = re.compile(r"\".+\" - .+")
    assert quote_regex.match(data[0].text) is not None, "Quote and author not in response."


@pytest.mark.external_integration
def test_quote_no_key(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"random"})
    # Check there's no API key
    if hallo.get_api_key("mashape") is not None:
        del hallo.api_key_list["mashape"]
    # Test function
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "random quote"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "no api key" in data[0].text.lower(), "Not warning about lack of API key."
    assert "mashape" in data[0].text.lower(), "Not specifying mashape API."
