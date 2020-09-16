from hallo.function import Function


class Longcat(Function):
    """
    Draws a classic longcat
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "longcat"
        # Names which can be used to address the function
        self.names = {"longcat", "ascii longcat"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Make a longcat! Format: longcat <length>"

    def run(self, event):
        """Make a longcat! Format: longcat <length>"""
        try:
            segments = int(event.command_args)
        except ValueError:
            segments = 5
        long_cat_head = r"""    /\___/\
   /       \
  |  #    # |
  \     @   |
   \   _|_ /
   /       \______
  / _______ ___   \
  |_____   \   \__/
  |    \__/
"""
        long_cat_segment = "   |       |\n"
        long_cat_tail = r"""   /        \
  /   ____   \
  |  /    \  |
  | |      | |
 /  |      |  \ 
 \__/      \__/"""
        longcat = long_cat_head + long_cat_segment * segments + long_cat_tail
        longcat += "\n Longcat is L{}ng!".format("o" * segments)
        return event.create_response(longcat)