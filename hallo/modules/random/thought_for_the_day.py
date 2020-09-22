from hallo.function import Function
from hallo.inc.commons import Commons


class ThoughtForTheDay(Function):
    """
    WH40K Thought for the day.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "thought for the day"  # Name for use in help listing
        # Names which can be used to address the function
        self.names = {
            "thought for the day",
            "thoughtfortheday",
            "thought of the day",
            "40k quote",
            "wh40k quote",
            "quote 40k",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "WH40K Thought for the day. Format: thought_for_the_day"
        self.thought_list = []
        self.load_thought_list()

    def load_thought_list(self):
        self.thought_list = Commons.read_file_to_list("store/WH40K_ToTD2.txt")

    def run(self, event):
        """WH40K Thought for the day. Format: thought_for_the_day"""
        thought = Commons.get_random_choice(self.thought_list)[0]
        if thought[-1] not in [".", "!", "?"]:
            thought += "."
        return event.create_response('"{}"'.format(thought))