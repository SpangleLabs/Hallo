import re

from hallo.function import Function
from hallo.inc.commons import Commons


class Roll(Function):
    """
    Function to roll dice or pick random numbers in a given range
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "roll"  # Name for use in help listing
        self.names = {
            "roll",
            "dice",
            "random",
            "random number",
        }  # Names which can be used to address the function
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Roll X-Y returns a random number between X and Y. "
            'Format: "roll <min>-<max>" or "roll <num>d<sides>"'
        )

    def run(self, event):
        """Runs the function"""
        # Check which format the input is in.
        dice_format_regex = re.compile("^[0-9]+d[0-9]+$", re.IGNORECASE)
        range_format_regex = re.compile("^[0-9]+-[0-9]+$", re.IGNORECASE)
        if dice_format_regex.match(event.command_args):
            num_dice = int(event.command_args.lower().split("d")[0])
            num_sides = int(event.command_args.lower().split("d")[1])
            return event.create_response(self.run_dice_format(num_dice, num_sides))
        elif range_format_regex.match(event.command_args):
            range_min = min([int(x) for x in event.command_args.split("-")])
            range_max = max([int(x) for x in event.command_args.split("-")])
            return event.create_response(self.run_range_format(range_min, range_max))
        else:
            return event.create_response("Please give input in the form of X-Y or XdY.")

    def run_dice_format(self, num_dice, num_sides):
        """Rolls numDice number of dice, each with numSides number of sides"""
        if num_dice == 0 or num_dice > 100:
            return "Invalid number of dice."
        if num_sides == 0 or num_sides > 1000000:
            return "Invalid number of sides."
        if num_dice == 1:
            rand = Commons.get_random_int(1, num_sides)[0]
            return "I roll {}!!!".format(rand)
        else:
            dice_rolls = Commons.get_random_int(1, num_sides, num_dice)
            output_string = "I roll {}. The total is {}.".format(
                ", ".join([str(x) for x in dice_rolls]), sum(dice_rolls)
            )
            return output_string

    def run_range_format(self, range_min, range_max):
        """Generates a random number between rangeMin and rangeMax"""
        rand = Commons.get_random_int(range_min, range_max)[0]
        return "I roll {}!!!".format(rand)
