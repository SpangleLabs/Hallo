from hallo.function import Function
from hallo.inc.commons import Commons


class ChosenOne(Function):
    """
    Selects a random user from a channel
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "chosen one"
        # Names which can be used to address the function
        self.names = {"chosen one", "chosenone", "random user"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Specifies who the chosen one is. Format: chosen one"

    def run(self, event):
        # If this command is run in privmsg, it won't work
        if event.channel is None:
            return event.create_response("This function can only be used in a channel")
        # Get the user list
        user_set = event.channel.get_user_list()
        # Get list of users' names
        names_list = [user_obj.name for user_obj in user_set]
        rand_name = Commons.get_random_choice(names_list)[0]
        return event.create_response(
            "It should be obvious by now that {} is the chosen one.".format(rand_name)
        )
