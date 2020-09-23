from xml.dom import minidom

from hallo.function import Function
from hallo.inc.commons import Commons


class NightValeProverb(Function):
    """
    Returns a random night vale proverb
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "nightvale proverb"
        # Names which can be used to address the function
        self.names = {
            "nightvale proverb",
            "night vale proverb",
            "random proverb",
            "proverb",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random proverb from Welcome to Night Vale. Format: nightvale proverb"
        self.proverb_list = []
        self.load_from_xml()

    def load_from_xml(self):
        doc = minidom.parse("store/proverbs.xml")
        proverb_list_elem = doc.getElementsByTagName("proverbs")[0]
        for proverb_elem in proverb_list_elem.getElementsByTagName("proverb"):
            self.proverb_list.append(proverb_elem.firstChild.data)

    def run(self, event):
        proverb = Commons.get_random_choice(self.proverb_list)[0]
        return event.create_response(proverb)
