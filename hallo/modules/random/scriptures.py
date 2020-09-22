from xml.dom import minidom

from hallo.function import Function
from hallo.inc.commons import Commons


class Scriptures(Function):
    """
    Amarr scriptures
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "scriptures"
        # Names which can be used to address the function
        self.names = {"scriptures", "amarr scriptures", "amarr"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Recites a passage from the Amarr scriptures. Format: scriptures"
        )
        self.scripture_list = []
        self.load_from_xml()

    def load_from_xml(self):
        doc = minidom.parse("store/scriptures.xml")
        scripture_list_elem = doc.getElementsByTagName("scriptures")[0]
        for scripture_elem in scripture_list_elem.getElementsByTagName("scripture"):
            self.scripture_list.append(scripture_elem.firstChild.data)

    def run(self, event):
        scripture = Commons.get_random_choice(self.scripture_list)[0]
        return event.create_response(scripture)