import os
import re

import pytest

from hallo.events import EventMessage


@pytest.mark.external_integration
def test_weather(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Check API key is set
    if test_hallo.get_api_key("youtube") is None:
        # Read from env variable
        test_hallo.add_api_key("youtube", os.getenv("test_api_key_youtube"))
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "nightvale weather")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "and now, the weather" in data[0].text.lower()
    ), "Didn't announce the weather"
    youtube_regex = re.compile(r"https?://youtu\.be/[A-Za-z0-9_\-]{11} .+")
    assert (
            youtube_regex.search(data[0].text) is not None
    ), "Youtube URL and title didn't appear in message"
    assert (
            len(mock_chooser.last_choices) > 1
    ), "One or fewer videos was on the playlist."


@pytest.mark.external_integration
def test_passive(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Check API key is set
    if test_hallo.get_api_key("youtube") is None:
        # Read from env variable
        test_hallo.add_api_key("youtube", os.getenv("test_api_key_youtube"))
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "and now to {} with the weather".format(test_hallo.test_server.get_nick()),
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "and now, the weather" in data[0].text.lower()
    ), "Didn't announce the weather"
    youtube_regex = re.compile(r"https?://youtu\.be/[A-Za-z0-9_\-]{11} .+")
    assert (
            youtube_regex.search(data[0].text) is not None
    ), "Youtube URL and title didn't appear in message"
    assert (
            len(mock_chooser.last_choices) > 1
    ), "One or fewer videos was on the playlist."


@pytest.mark.external_integration
def test_no_api_key(hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Check there's no API key
    if test_hallo.get_api_key("youtube") is not None:
        del test_hallo.api_key_list["youtube"]
    # Test function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "nightvale weather")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "no api key" in data[0].text.lower()
    ), "Not warning about lack of API key."
    assert "youtube" in data[0].text.lower(), "Not specifying youtube API."
