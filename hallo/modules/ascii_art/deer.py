from hallo.function import Function
from hallo.server import Server


class Deer(Function):
    """
    Draws an ascii deer
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "deer"
        # Names which can be used to address the function
        self.names = {"deer", "ascii deer"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Ascii art deer. Format: deer"

    def run(self, event):
        """ascii art deer. Format: deer"""
        deer = r"""   /|       |\
`__\\       //__'
   ||      ||
 \__`\     |'__/
   `_\\   //_'
   _.,:---;,._
   \_:     :_/
     |@. .@|
     |     |
     ,\.-./ \
     ;;`-'   `---__________-----.-.
     ;;;                         \_\
     ';;;                         |
      ;    |                      ;
       \   \     \        |      /
        \_, \    /        \     |\
          |';|  |,,,,,,,,/ \    \ \_
          |  |  |           \   /   |
          \  \  |           |  / \  |
           | || |           | |   | |
           | || |           | |   | |
           | || |           | |   | |
           |_||_|           |_|   |_|
          /_//_/           /_/   /_/aaa"""
        if event.server.type == Server.TYPE_TELEGRAM:
            deer = "```" + deer + "```"
        return event.create_response(deer)
