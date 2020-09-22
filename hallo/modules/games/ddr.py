from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.games.games


class DDR(Function):
    """
    Function to play IRC DDR (Dance Dance Revolution)
    """

    START_CMDS = ["start", "easy", "medium", "med", "hard"]
    JOIN_CMDS = ["join"]
    END_CMDS = ["end", "quit", "escape"]
    MOVE_CMDS = ["^", ">", "<", "v", "w", "a", "d", "s"]

    # Boring functions
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "ddr"
        # Names which can be used to address the function
        self.names = {"ddr", "dance dance revolution", "dansu dansu", "dancing stage"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Plays dance dance revolution. Hallo says directions and users must respond to them "
            "correctly and in the fastest time they can"
        )
        self.game_list = []

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return DDR()

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
                    line_clean,
                    event.user,
                    event.user if event.channel is None else event.channel,
                )
            )
        elif any(cmd in line_clean for cmd in self.JOIN_CMDS):
            return event.create_response(
                self.join_game(
                    line_clean,
                    event.user,
                    event.user if event.channel is None else event.channel,
                )
            )
        elif any(cmd in line_clean for cmd in self.END_CMDS):
            return event.create_response(
                self.quit_game(
                    line_clean,
                    event.user,
                    event.user if event.channel is None else event.channel,
                )
            )
        elif any(cmd in line_clean for cmd in self.MOVE_CMDS):
            return event.create_response(
                self.make_move(
                    line_clean,
                    event.user,
                    event.user if event.channel is None else event.channel,
                )
            )
        output_string = "Invalid difficulty mode. Please specify easy, medium or hard."
        return event.create_response(output_string)

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        full_line = event.text.strip().lower()
        if any(cmd in full_line for cmd in self.JOIN_CMDS):
            resp = self.join_game(full_line, event.user, event.channel, True)
            return None if resp is None else event.create_response(resp)
        elif any(cmd in full_line for cmd in self.END_CMDS):
            resp = self.quit_game(full_line, event.user, event.channel, True)
            return None if resp is None else event.create_response(resp)
        elif any(cmd in full_line for cmd in self.MOVE_CMDS):
            resp = self.make_move(full_line, event.user, event.channel, True)
            return None if resp is None else event.create_response(resp)
        pass

    def find_game(self, destination_obj):
        """Finds the game running in a specified channel, None otherwise."""
        for game in self.game_list:
            if game.destination == destination_obj:
                if game.is_game_over():
                    self.game_list.remove(game)
                    return None
                else:
                    return game
        return None

    def new_game(self, line_clean, user_obj, destination_obj):
        """Starts a new game"""
        current_game = self.find_game(destination_obj)
        if current_game is not None:
            return "There's already a game going in this channel."
        # Find out the game difficulty
        game_difficulty = hallo.modules.games.games.DDRGame.DIFFICULTY_EASY
        if "easy" in line_clean:
            game_difficulty = hallo.modules.games.games.DDRGame.DIFFICULTY_EASY
        elif "med" in line_clean:
            game_difficulty = hallo.modules.games.games.DDRGame.DIFFICULTY_MEDIUM
        elif "hard" in line_clean:
            game_difficulty = hallo.modules.games.games.DDRGame.DIFFICULTY_HARD
        else:
            "Invalid difficulty mode. Please specify easy, medium or hard."
        # Create the new game and start it
        new_game = hallo.modules.games.games.DDRGame(game_difficulty, user_obj, destination_obj)
        new_game.start_game()
        self.game_list.append(new_game)

    def join_game(self, line_clean, user_obj, destination_obj, passive=False):
        """Player requests to join a game"""
        current_game = self.find_game(destination_obj)
        if current_game is None:
            if not passive:
                return "There is no game happening in this channel."
            else:
                return None
        output_string = current_game.join_game(user_obj)
        return output_string

    def quit_game(self, line_clean, user_obj, destination_obj, passive=False):
        """Player requests to quit a game"""
        current_game = self.find_game(destination_obj)
        if current_game is None:
            if not passive:
                return "There is no game happening in this channel."
            else:
                return None
        output_string = current_game.quit_game(user_obj)
        if current_game.is_game_over():
            self.game_list.remove(current_game)
        return output_string

    def make_move(self, line_clean, user_obj, destination_obj, passive=False):
        """Player makes a move"""
        current_game = self.find_game(destination_obj)
        if current_game is None:
            if not passive:
                return "There is no game happening in this channel."
            else:
                return None
        output_string = None
        if line_clean in ["<", "a"]:
            output_string = current_game.make_move(hallo.modules.games.games.DDRGame.DIRECTION_LEFT, user_obj)
        if line_clean in [">", "d"]:
            output_string = current_game.make_move(hallo.modules.games.games.DDRGame.DIRECTION_RIGHT, user_obj)
        if line_clean in ["^", "w"]:
            output_string = current_game.make_move(hallo.modules.games.games.DDRGame.DIRECTION_UP, user_obj)
        if line_clean in ["v", "s"]:
            output_string = current_game.make_move(hallo.modules.games.games.DDRGame.DIRECTION_DOWN, user_obj)
        return output_string