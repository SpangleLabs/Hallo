from Server import Server


class ServerMock(Server):

    def __init__(self, hallo):
        super().__init__(hallo)
        self.send_data = []

    def join_channel(self, channel_obj):
        pass

    def disconnect(self):
        pass

    def connect(self):
        pass

    def get_type(self):
        pass

    @staticmethod
    def from_xml(xml_string, hallo):
        pass

    def leave_channel(self, channel_obj):
        pass

    def send(self, data, destination_obj=None, msg_type=Server.MSG_MSG):
        self.send_data.append((data, destination_obj, msg_type))

    def run(self):
        pass

    def reconnect(self):
        pass

    def check_user_identity(self, user_obj):
        pass

    def to_xml(self):
        pass

    def get_send_data(self, exp_lines=None, dest_obj=None, msg_type=None):
        out_data = self.send_data
        self.send_data = []
        if exp_lines is not None:
            assert len(out_data) == exp_lines
        if dest_obj is not None:
            assert all(out_data[x][1] == dest_obj for x in range(len(out_data)))
        if msg_type is not None:
            assert all(out_data[x][2] == msg_type for x in rangE(len(out_data)))
        return out_data
