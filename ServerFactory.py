from Server import Server
from ServerIRC import ServerIRC
from ServerTelegram import ServerTelegram


class ServerFactory:
    """
    Server factory, makes servers.
    Basically looks at xml, finds server type, and passes to appropriate Server object constructor
    """

    def __init__(self, hallo):
        """
        Constructs the Server Factory, stores Hallo object.
        :param hallo: Hallo object which owns this server factory
        :type hallo: Hallo.Hallo
        """
        self.hallo = hallo

    def new_server_from_json(self, json_obj):
        server_type = json_obj["type"]
        if server_type == Server.TYPE_IRC:
            return ServerIRC.from_json(json_obj, self.hallo)
        elif server_type == Server.TYPE_TELEGRAM:
            return ServerTelegram.from_json(json_obj, self.hallo)
        else:
            return None
