from hallo.function import Function
import hallo.modules.games.games


class RandomCard(Function):
    """
    Returns a random card from a fresh deck.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "card"
        # Names which can be used to address the function
        self.names = {"card", "random card", "randomcard"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Picks a random card from a deck. Format: random_card"

    def run(self, event):
        new_deck = hallo.modules.games.games.Deck()
        new_deck.shuffle()
        random_card = new_deck.get_next_card()
        return event.create_response(
            "I have chosen the {}.".format(random_card.to_string())
        )