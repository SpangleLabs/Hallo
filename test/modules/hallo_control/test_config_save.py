from events import EventMessage
from hallo import Hallo


def test_save_config(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    old_hallo = test_user.server.hallo
    try:
        mock_hallo = HalloMock()
        test_user.server.hallo = mock_hallo
        hallo.function_dispatcher.dispatch(
            EventMessage(test_server, None, test_user, "config save")
        )
        data = test_server.get_send_data(1, test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "config has been saved" in data[0].text.lower()
        assert mock_hallo.saved_to_json
    finally:
        test_user.server.hallo = old_hallo


class HalloMock(Hallo):
    saved_to_json = False

    def save_json(self):
        self.saved_to_json = True
