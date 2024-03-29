from hallo.events import EventMessage
from hallo.hallo import Hallo


def test_save_config(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    old_hallo = test_hallo.test_user.server.hallo
    try:
        mock_hallo = HalloMock()
        test_hallo.test_user.server.hallo = mock_hallo
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "config save")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "config has been saved" in data[0].text.lower()
        assert mock_hallo.saved_to_json
    finally:
        test_hallo.test_user.server.hallo = old_hallo


class HalloMock(Hallo):
    saved_to_json = False

    def save_json(self):
        self.saved_to_json = True
