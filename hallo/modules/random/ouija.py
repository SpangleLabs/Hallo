from hallo.function import Function
from hallo.inc.commons import Commons


class Ouija(Function):
    """
    Ouija board function. "Ouija board" is copyright Hasbro.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "ouija"
        # Names which can be used to address the function
        self.names = {
            "ouija",
            "ouija board",
            "random words",
            "message from the other side",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Ouija board function. Format: ouija <message>"

    def run(self, event):
        word_list = Commons.read_file_to_list("store/ouija_wordlist.txt")
        num_words = Commons.get_random_int(1, 3)[0]
        rand_words = Commons.get_random_choice(word_list, num_words)
        output_string = "I'm getting a message from the other side... {}.".format(
            " ".join(rand_words)
        )
        return event.create_response(output_string)