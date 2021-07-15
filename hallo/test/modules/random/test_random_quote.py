import re

import pytest

from hallo.events import EventMessage


@pytest.mark.external_integration
def test_quote(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random quote")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    quote_regex = re.compile(r"\".+\" - .+")
    assert (
        quote_regex.match(data[0].text) is not None
    ), "Quote and author not in response."
