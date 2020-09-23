from hallo.function import Function
from hallo.inc.commons import Commons


class EightBall(Function):
    """
    Magic 8 ball. Format: eightball
    """

    RESPONSES_YES_TOTALLY = [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes definitely",
        "You may rely on it",
    ]
    RESPONSES_YES_PROBABLY = [
        "As I see it yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
    ]
    RESPONSES_MAYBE = [
        "Reply hazy try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
    ]
    RESPONSES_NO = [
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful",
    ]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "eightball"
        # Names which can be used to address the function
        self.names = {"eightball"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Magic 8 ball. Format: eightball"

    def run(self, event):
        responses = (
            EightBall.RESPONSES_YES_TOTALLY
            + EightBall.RESPONSES_YES_PROBABLY
            + EightBall.RESPONSES_MAYBE
            + EightBall.RESPONSES_NO
        )
        resp = Commons.get_random_choice(responses)[0]
        return event.create_response("{}.".format(resp))

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = {"eightball"}
        for magic in ["magic ", "magic", ""]:
            for eight in ["eight", "8"]:
                for space in [" ", "-", ""]:
                    self.names.add("{}{}{}ball".format(magic, eight, space))
        self.names.add(self.help_name)
        return self.names
