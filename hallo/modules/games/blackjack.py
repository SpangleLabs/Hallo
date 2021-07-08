from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.games.games


class Blackjack(Function):
    """
    Function to play Blackjack
    """

    START_CMDS = ["start"]
    END_CMDS = ["end", "quit", "escape"]
    HIT_CMDS = ["hit"]
    STICK_CMDS = ["stick", "stand"]

    # Boring functions
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "blackjack"
        # Names which can be used to address the function
        self.names = {"blackjack", "twentyone", "twenty one", "twenty-one", "21"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Picks a random card from a deck. Format: random_card"
        self.game_list = []

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return Blackjack()

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
                self.new_game(event.user, event.destination)
            )
        elif any(cmd in line_clean for cmd in self.END_CMDS):
            return event.create_response(
                self.quit_game(event.user, event.destination)
            )
        elif any(cmd in line_clean for cmd in self.HIT_CMDS):
            return event.create_response(
                self.hit(event.user, event.destination)
            )
        elif any(cmd in line_clean for cmd in self.STICK_CMDS):
            return event.create_response(
                self.stick(event.user, event.destination)
            )
        output_string = "I don't understand this input."
        output_string += ' Syntax: "blackjack start" to start a game, '
        output_string += '"blackjack hit" to hit, "blackjack stick" to stick, '
        output_string += 'and "blackjack end" to quit the game.'
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
        elif any(cmd in clean_line for cmd in self.HIT_CMDS):
            return event.create_response(self.hit(event.user, event.channel, True))
        elif any(cmd in clean_line for cmd in self.STICK_CMDS):
            return event.create_response(self.stick(event.user, event.channel, True))
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
        new_game = hallo.modules.games.games.BlackjackGame(user_obj, destination_obj)
        output_string = new_game.start_game()
        self.game_list.append(new_game)
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

    def hit(self, user_obj, destination_obj, passive=False):
        """User wants to hit"""
        current_game = self.find_game(user_obj)
        if current_game is None:
            if not passive:
                return "You're not playing a game."
            else:
                return None
        output_string = current_game.hit()
        if current_game.is_lost():
            self.game_list.remove(current_game)
        return output_string

    def stick(self, user_obj, destination_obj, passive=False):
        """User wants to stick"""
        current_game = self.find_game(user_obj)
        if current_game is None:
            if not passive:
                return "You're not playing a game."
            else:
                return None
        output_string = current_game.stick()
        self.game_list.remove(current_game)
        return output_string
