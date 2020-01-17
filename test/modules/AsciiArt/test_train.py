from test.modules.AsciiArt.test_deer import hallo_getter
from events import EventMessage


def test_train_simple(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"ascii_art"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "train"))
    data = test_server.get_send_data()
    assert "error" not in data[0].text, "Train output should not produce errors."
    assert "\n" in data[0].text, "Train output should be multiple lines."
    assert "chugga chugga" in data[0].text, "Train needs to say chugga chugga."
