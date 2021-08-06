from typing import TYPE_CHECKING

from hallo.server import Server

if TYPE_CHECKING:
    from hallo.events import ChannelUserTextEvent


class ServerMock(Server):
    def __init__(self, hallo):
        super().__init__(hallo)
        self.send_data = []
        self.left_channels = []
        self.state = Server.STATE_CLOSED
        self.type = Server.TYPE_MOCK
        self.prefix = ""

    def join_channel(self, channel_obj):
        pass

    def start(self):
        self.state = Server.STATE_OPEN

    def disconnect(self, force=False):
        self.state = Server.STATE_CLOSED

    def get_type(self):
        return Server.TYPE_MOCK

    @staticmethod
    def from_xml(xml_string, hallo):
        pass

    def leave_channel(self, channel_obj):
        super().leave_channel(channel_obj)
        self.left_channels.append(channel_obj)

    def send(self, event, *, after_sent_callback=None):
        self.send_data.append(event)
        if after_sent_callback:
            after_sent_callback(event)

    def reply(self, old_event, new_event):
        super().reply(old_event, new_event)
        self.send(new_event)

    def edit_by_id(self, message_id: int, new_event: 'ChannelUserTextEvent', *, has_photo: bool = False):
        self.send(new_event)

    def reconnect(self):
        pass

    def check_user_identity(self, user_obj):
        pass

    def get_name_by_address(self, address):
        return address

    def to_json(self):
        return dict()

    @staticmethod
    def from_json(json_obj, hallo):
        return ServerMock(hallo)

    # Mock server specific methods below:

    def get_send_data(self, exp_lines=None, dest_obj=None, msg_type=None):
        """
        :type exp_lines: int | None
        :type dest_obj: destination.Destination | None
        :type msg_type: type | None
        :rtype: list[ServerEvent]
        """
        out_data = self.send_data
        self.send_data = []
        if exp_lines is not None:
            assert len(out_data) == exp_lines, (
                "Wrong amount of events received. Expected {}  but got {}. "
                "Full data : {}".format(exp_lines, len(out_data), out_data)
            )
        if dest_obj is not None:
            assert all(
                (out_data[x].user == dest_obj or out_data[x].channel == dest_obj)
                for x in range(len(out_data))
            ), "Incorrect destination for data. Full data: {}".format(out_data)
        if msg_type is not None:
            assert all(
                isinstance(out_data[x], msg_type) for x in range(len(out_data))
            ), "Incorrect message type for data. Full data: {}".format(out_data)
        return out_data

    def get_left_channels(self, exp_chans=None):
        left_chans = self.left_channels
        self.left_channels = []
        if exp_chans is not None:
            assert (
                len(left_chans) == exp_chans
            ), "Wrong amount of channels left: " + str(left_chans)
        return left_chans
