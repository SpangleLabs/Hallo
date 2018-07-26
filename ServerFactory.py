from xml.dom import minidom

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

    def new_server_from_xml(self, xml_string):
        """
        Identifies type of server and constructs from xml
        :param xml_string: XML string to create server from
        :type xml_string: str
        """
        doc = minidom.parseString(xml_string)
        server_type = doc.getElementsByTagName("server_type")[0].firstChild.data
        if server_type == Server.TYPE_IRC:
            return ServerIRC.from_xml(xml_string, self.hallo)
        elif server_type == Server.TYPE_TELEGRAM:
            return ServerTelegram.from_xml(xml_string, self.hallo)
        else:
            return None
