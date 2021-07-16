import os

import pytest

from hallo.events import EventMessage


@pytest.mark.external_integration
def test_cat_gif_with_key(hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Check API key is set
    if test_hallo.get_api_key("thecatapi") is None:
        # Read from env variable
        test_hallo.add_api_key("thecatapi", os.getenv("test_api_key_thecatapi"))
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "cat gif")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text.lower().startswith("http"), "Link not being returned."
    assert data[0].text.lower().endswith(".gif"), "Gif not being returned."


def test_cat_gif_no_key(hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Check there's no API key
    if test_hallo.get_api_key("thecatapi") is not None:
        del test_hallo.api_key_list["thecatapi"]
    # Test function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "cat gif")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "no api key" in data[0].text.lower(), "Not warning about lack of API key."
    assert "cat api" in data[0].text.lower(), "Not specifying cat API."
