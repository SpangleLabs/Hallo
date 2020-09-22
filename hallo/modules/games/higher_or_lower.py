from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.games.games


class HigherOrLower(Function):
    """
    Function to play Higher or Lower
    """

    START_CMDS = ["start"]
    END_CMDS = ["end", "quit", "escape"]
    HIGH_CMDS = ["higher", "high", "more", "more", "greater", "greater", "bigger", ">"]
    LOW_CMDS = ["lower", "low", "less", "small", "<"]

    # Boring functions
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "higher or lower"
        # Names which can be used to address the function
        self.names = {"higher or lower", "higherorlower"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Plays a game of higher or lower."
        self.game_list = []

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return HigherOrLower()

    def save_function(self):
        """Saves the function, persistent functions only."""
        # TODO: save all games to XML perhaps?
        pass

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    # Interesting functions from here
    def run(self, event):
        line_clean = event.command_args.strip().lower()
        if line_clean in [""] + self.START_CMDS:
            return event.create_response(
                self.new_game(
                    event.user, event.user if event.channel is None else event.channel
                )
            )
        elif any(cmd in line_clean for cmd in self.END_CMDS):
            return event.create_response(
                self.quit_game(
                    event.user, event.user if event.channel is None else event.channel
                )
            )
        elif any(cmd in line_clean for cmd in self.HIGH_CMDS):
            return event.create_response(
                self.guess_higher(
                    event.user, event.user if event.channel is None else event.channel
                )
            )
        elif any(cmd in line_clean for cmd in self.LOW_CMDS):
            return event.create_response(
                self.guess_lower(
                    event.user, event.user if event.channel is None else event.channel
                )
            )
        output_string = "I don't understand this input."
        output_string += ' Syntax: "higher_or_lower start" to start a game, '
        output_string += (
            '"higher_or_lower higher" to guess the next card will be higher, '
        )
        output_string += (
            '"higher_or_lower lower" to guess the next card will be lower, '
        )
        output_string += '"higher_or_lower end" to quit the game.'
        return event.create_response(output_string)

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        clean_line = event.text.strip().lower()
        if any(cmd in clean_line for cmd in self.END_CMDS):
            return event.create_response(
                self.quit_game(event.user, event.channel, True)
            )
        elif any(cmd in clean_line for cmd in self.HIGH_CMDS):
            return event.create_response(
                self.guess_higher(event.user, event.channel, True)
            )
        elif any(cmd in clean_line for cmd in self.LOW_CMDS):
            return event.create_response(
                self.guess_lower(event.user, event.channel, True)
            )
        pass

    def find_game(self, user_obj):
        """Finds the game a specified user is in, None otherwise."""
        for game in self.game_list:
            if game.contains_player(user_obj):
                return game
        return None

    def new_game(self, user_obj, destination_obj):
        """User request to create a new game"""
        current_game = self.find_game(user_obj)
        if current_game is not None:
            return "You're already playing a game."
        new_game = hallo.modules.games.games.HigherOrLowerGame(user_obj, destination_obj)
        self.game_list.append(new_game)
        output_string = new_game.start_game()
        return output_string

    def quit_game(self, user_obj, destination_obj, passive=False):
        """User request to quit game"""
        current_game = self.find_game(user_obj)
        if current_game is None:
            if not passive:
                return "You're not playing a game."
            else:
                return None
        output_string = current_game.quit_game()
        self.game_list.remove(current_game)
        return output_string

    def guess_higher(self, user_obj, destination_obj, passive=False):
        """User guessed next card is higher"""
        current_game = self.find_game(user_obj)
        if current_game is None:
            if not passive:
                return "You're not playing a game."
            else:
                return None
        output_string = current_game.guess_higher()
        if current_game.is_lost():
            self.game_list.remove(current_game)
        return output_string

    def guess_lower(self, user_obj, destination_obj, passive=False):
        """User guessed next card is lower"""
        current_game = self.find_game(user_obj)
        if current_game is None:
            if not passive:
                return "You're not playing a game."
            else:
                return None
        output_string = current_game.guess_lower()
        if current_game.is_lost():
            self.game_list.remove(current_game)
        return output_string