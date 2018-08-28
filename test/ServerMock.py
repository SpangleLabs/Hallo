from Server import Server


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

    def send(self, data, destination_obj=None, msg_type=Server.MSG_MSG):
        self.send_data.append((data, destination_obj, msg_type))

    def reconnect(self):
        pass

    def check_user_identity(self, user_obj):
        pass

    def to_xml(self):
        pass

    def to_json(self):
        return dict()

    @staticmethod
    def from_json(json_obj, hallo):
        return ServerMock(hallo)

    # Mock server specific methods below:

    def get_send_data(self, exp_lines=None, dest_obj=None, msg_type=None):
        out_data = self.send_data
        self.send_data = []
        if exp_lines is not None:
            assert len(out_data) == exp_lines, "Wrong amount of data received. Expected "+str(exp_lines)+\
                                               " but got "+str(len(out_data))+". Full data : " + str(out_data)
        if dest_obj is not None:
            assert all(out_data[x][1] == dest_obj for x in range(len(out_data))), "Incorrect destination for data. " \
                                                                                  "Full data: " + \
                                                                                  str(out_data)
        if msg_type is not None:
            assert all(out_data[x][2] == msg_type for x in range(len(out_data))), "Incorrect message type for data. " \
                                                                                  "Full data: " + \
                                                                                  str(out_data)
        return out_data

    def get_left_channels(self, exp_chans=None):
        left_chans = self.left_channels
        self.left_channels = []
        if exp_chans is not None:
            assert len(left_chans) == exp_chans, "Wrong amount of channels left: "+str(left_chans)
        return left_chans
