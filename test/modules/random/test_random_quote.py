import os
import re

import pytest

from events import EventMessage


@pytest.mark.external_integration
def test_quote(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"random"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "random quote")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    quote_regex = re.compile(r"\".+\" - .+")
    assert (
        quote_regex.match(data[0].text) is not None
    ), "Quote and author not in response."
