from hallo.events import EventMessage
from hallo.hallo import Hallo


def test_shutdown(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    mock_hallo = HalloMock()
    test_user.server.hallo = mock_hallo
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "shutdown")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "shutting down" in data[0].text.lower()
    assert mock_hallo.shutdown


class HalloMock(Hallo):
    shutdown = False

    def close(self):
        self.shutdown = True
