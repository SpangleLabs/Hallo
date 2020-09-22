import re

from hallo.function import Function
from hallo.inc.commons import Commons


class Choose(Function):
    """
    Function to pick one of multiple given options
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "choose"  # Name for use in help listing
        self.names = {
            "choose",
            "pick",
        }  # Names which can be used to address the function
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            'Choose X, Y or Z or ... Returns one of the options separated by "or" or a comma. '
            "Format: choose <first_option>, <second_option> ... <n-1th option> or <nth option>"
        )

    def run(self, event):
        choices = re.compile(", (?:or )?| or,? ", re.IGNORECASE).split(
            event.command_args
        )
        numchoices = len(choices)
        if numchoices == 1:
            return event.create_response(
                "Please present me with more than 1 thing to choose from!"
            )
        else:
            choice = Commons.get_random_choice(choices)[0]
            return event.create_response('I choose "{}".'.format(choice))