from hallo.destination import Channel, User
from hallo.events import EventMessage
import random
import time

from hallo.inc.commons import Commons
from threading import Thread


class Card:
    """
    Card object, for use by higher or lower, blackjack, and any other card games.
    """

    # Constants
    SUIT_DIAMONDS = "diamonds"
    SUIT_HEARTS = "hearts"
    SUIT_CLUBS = "clubs"
    SUIT_SPADES = "spades"
    COLOUR_RED = "red"
    COLOUR_BLACK = "black"
    CARD_ACE = 1
    CARD_2 = 2
    CARD_3 = 3
    CARD_4 = 4
    CARD_5 = 5
    CARD_6 = 6
    CARD_7 = 7
    CARD_8 = 8
    CARD_9 = 9
    CARD_10 = 10
    CARD_JACK = "jack"
    CARD_QUEEN = "queen"
    CARD_KING = "king"

    def __init__(self, deck, suit, value):
        """
        Constructor
        """
        self.deck = deck
        self.in_deck = True
        if suit in [self.SUIT_DIAMONDS, self.SUIT_HEARTS]:
            self.suit = suit
            self.colour = self.COLOUR_RED
        elif suit in [self.SUIT_CLUBS, self.SUIT_SPADES]:
            self.suit = suit
            self.colour = self.COLOUR_BLACK
        else:
            raise Exception("Invalid suit")
        if value in [
            self.CARD_ACE,
            self.CARD_2,
            self.CARD_3,
            self.CARD_4,
            self.CARD_5,
            self.CARD_6,
            self.CARD_7,
            self.CARD_8,
            self.CARD_9,
            self.CARD_10,
            self.CARD_JACK,
            self.CARD_QUEEN,
            self.CARD_KING,
        ]:
            self.value = value
        else:
            raise Exception("Invalid value")

    def __str__(self):
        return self.to_string()

    def to_string(self):
        """Outputs a string representing the card\'s value and suit."""
        if self.value == self.CARD_ACE:
            card_value = "Ace"
        elif self.value == self.CARD_JACK:
            card_value = "Jack"
        elif self.value == self.CARD_QUEEN:
            card_value = "Queen"
        elif self.value == self.CARD_KING:
            card_value = "King"
        else:
            card_value = str(self.value)
        if self.suit == self.SUIT_CLUBS:
            card_suit = "clubs"
        elif self.suit == self.SUIT_DIAMONDS:
            card_suit = "diamonds"
        elif self.suit == self.SUIT_HEARTS:
            card_suit = "hearts"
        elif self.suit == self.SUIT_SPADES:
            card_suit = "spades"
        else:
            raise Exception("invalid suit")
        return "{} of {}".format(card_value, card_suit)

    def sum_value(self):
        """Outputs the value as an integer. For blackjack."""
        black_jack_dict = {
            self.CARD_KING: 10,
            self.CARD_QUEEN: 10,
            self.CARD_JACK: 10,
            self.CARD_10: 10,
            self.CARD_9: 9,
            self.CARD_8: 8,
            self.CARD_7: 7,
            self.CARD_6: 6,
            self.CARD_5: 5,
            self.CARD_4: 4,
            self.CARD_3: 3,
            self.CARD_2: 2,
            self.CARD_ACE: 1,
        }
        if self.value in black_jack_dict:
            return black_jack_dict[self.value]
        return None

    def poker_value(self):
        """Outputs poker value. From 2 to 14."""
        poker_dict = {
            self.CARD_ACE: 14,
            self.CARD_KING: 13,
            self.CARD_QUEEN: 12,
            self.CARD_JACK: 11,
            self.CARD_10: 10,
            self.CARD_9: 9,
            self.CARD_8: 8,
            self.CARD_7: 7,
            self.CARD_6: 6,
            self.CARD_5: 5,
            self.CARD_4: 4,
            self.CARD_3: 3,
            self.CARD_2: 2,
        }
        if self.value in poker_dict:
            return poker_dict[self.value]
        return None

    def __int__(self):
        return self.to_int()

    def to_int(self):
        """Converts the card value to integer, for higher or lower and similar"""
        int_dict = {
            self.CARD_KING: 13,
            self.CARD_QUEEN: 12,
            self.CARD_JACK: 11,
            self.CARD_10: 10,
            self.CARD_9: 9,
            self.CARD_8: 8,
            self.CARD_7: 7,
            self.CARD_6: 6,
            self.CARD_5: 5,
            self.CARD_4: 4,
            self.CARD_3: 3,
            self.CARD_2: 2,
            self.CARD_ACE: 1,
        }
        if self.value in int_dict:
            return int_dict[self.value]
        return None

    def is_in_deck(self):
        """boolean, whether the card is still in the deck."""
        return self.in_deck

    def set_in_deck(self, in_deck):
        """mInDeck setter"""
        self.in_deck = in_deck

    def get_suit(self):
        """Suit getter"""
        return self.suit

    def get_colour(self):
        """Colour getter"""
        return self.colour

    def get_value(self):
        """Value getter"""
        return self.value


class Deck:
    """
    Deck object, for use by higher or lower, blackjack, and any other card games.
    Generates 52 cards and can then shuffle them.
    WILL NOT SHUFFLE BY DEFAULT.
    """

    def __init__(self):
        self.card_list = []  # List of cards in the deck.
        self.all_cards = []  # All the cards which were originally in the deck.
        card_list = []
        for card_suit in [
            Card.SUIT_HEARTS,
            Card.SUIT_CLUBS,
            Card.SUIT_DIAMONDS,
            Card.SUIT_SPADES,
        ]:
            suit_list = []
            for card_value in [
                Card.CARD_ACE,
                Card.CARD_2,
                Card.CARD_3,
                Card.CARD_4,
                Card.CARD_5,
                Card.CARD_6,
                Card.CARD_7,
                Card.CARD_8,
                Card.CARD_9,
                Card.CARD_10,
                Card.CARD_JACK,
                Card.CARD_QUEEN,
                Card.CARD_KING,
            ]:
                new_card = Card(self, card_suit, card_value)
                suit_list.append(new_card)
            if card_suit in [Card.SUIT_DIAMONDS, Card.SUIT_SPADES]:
                suit_list.reverse()
            card_list += suit_list
        self.card_list = card_list
        self.all_cards = card_list

    def shuffle(self):
        """Shuffles the deck"""
        random.shuffle(self.card_list)

    def get_next_card(self):
        """Gets the next card from the deck"""
        next_card = self.card_list.pop(0)
        next_card.set_in_deck(False)
        return next_card

    def is_empty(self):
        """Boolean, whether the deck is empty."""
        return len(self.card_list) == 0

    def get_card(self, suit, value):
        """Returns the card object for this deck with the specified suit and value."""
        for card in self.all_cards:
            if suit == card.get_suit() and value == card.get_value():
                return card


class Hand:
    """
    Hand of cards, stores a set of cards in an order.
    """

    def __init__(self, user_obj=None):
        self.card_list = []
        self.player = user_obj

    def shuffle(self):
        """Shuffles a hand"""
        random.shuffle(self.card_list)

    def add_card(self, new_card):
        """Adds a new card to the hand"""
        self.card_list.append(new_card)

    def get_card_list(self):
        """Returns the card list"""
        return self.card_list

    def sum_total(self):
        """Returns the sum total of the hand."""
        return sum([card.sum_value() for card in self.card_list])

    def blackjack_total(self):
        """Returns the blackjack total of the hand. (Takes aces as 11 if that doesn\'t make you bust."""
        sum_total = self.sum_total()
        if sum_total <= 11 and self.contains_value(Card.CARD_ACE):
            sum_total += 10
        return sum_total

    def contains_card(self, card_obj):
        """Checks whether a hand contains a specified card"""
        return card_obj in self.card_list

    def contains_value(self, value):
        """Checks whether a hand contains a specified card value"""
        return value in [card.get_value() for card in self.card_list]

    def count_value(self, value):
        """Counts how many cards of a specified value are in the hand"""
        return [card.get_value() for card in self.card_list].count(value)

    def cards_in_hand(self):
        """Returns the number of cards in the hand"""
        return len(self.card_list)

    def is_royal_flush(self):
        """Checks whether a hand is a royal flush, for poker. Returns False or True"""
        if self.is_straight_flush() == 14:
            return True
        return False

    def is_straight_flush(self):
        """Checks whether a hand is a straight flush, for poker. Returns False or highest value"""
        # Check if flush
        if not self.is_flush():
            return False
        # Check if straight
        return self.is_straight()

    def is_four_of_a_kind(self):
        """
        Checks whether a hand is 4 of a kind, for poker.
        Returns False or list with element 0 being the value of the quadrupled card,
        element 1 being value of other card.
        """
        four_card_value = None
        other_card_value = None
        for card in self.card_list:
            card_value = card.get_value()
            count_value = self.count_value(card_value)
            if count_value == 4:
                four_card_value = card.poker_value()
            elif count_value == 1:
                other_card_value = card.poker_value()
            else:
                return False
        if four_card_value is None:
            return False
        return [four_card_value, other_card_value]

    def is_full_house(self):
        """
        Checks whether a hand contains 3 of a kind and a pair, for poker.
        Returns False or list with element 0 being value of the triplicated card,
        element 1 being value of duplicated card.
        """
        three_card_value = None
        two_card_value = None
        for card in self.card_list:
            card_value = card.get_value()
            count_value = self.count_value(card_value)
            if count_value == 3:
                three_card_value = card.poker_value()
            elif count_value == 2:
                two_card_value = card.poker_value()
            else:
                return False
        if three_card_value is None or two_card_value is None:
            return False
        return [three_card_value, two_card_value]

    def is_flush(self):
        """Checks whether a hand is all the same suit, for poker. Returns False or value of highest card."""
        # Check all cards are the same suit.
        if len(set([card.get_suit() for card in self.card_list])) != 1:
            return False
        # Get highest card value and output
        max_value = max([card.poker_value() for card in self.card_list])
        return max_value

    def is_straight(self):
        """Checks whether a hand is a straight, for poker. Returns False or highest value"""
        # Get minimum card poker value
        min_value = min([card.poker_value() for card in self.card_list])
        # Check that the set of card values minus minimum value is equal to the range 0-4
        card_range = set([card.poker_value() - min_value for card in self.card_list])
        if card_range == set(range(5)):
            return min_value + 4
        return False

    def is_three_of_a_kind(self):
        """Checks whether a hand contains 3 of a kind, for poker. Returns False or list."""
        three_card_value = None
        other_card_values = []
        for card in self.card_list:
            card_value = card.get_value()
            count_value = self.count_value(card_value)
            if count_value == 3:
                three_card_value = card.poker_value()
            else:
                other_card_values.append(card.poker_value())
        if three_card_value is None:
            return False
        max_other_card_value = max(other_card_values)
        min_other_card_value = min(other_card_values)
        return [three_card_value, max_other_card_value, min_other_card_value]

    def is_two_pairs(self):
        """Checks whether a hand contains two pairs, for poker. Returns False or list."""
        two_card_values = set()
        other_card_value = None
        for card in self.card_list:
            card_value = card.get_value()
            count_value = self.count_value(card_value)
            if count_value == 2:
                two_card_values.add(card.poker_value())
            elif count_value == 1:
                other_card_value = card.poker_value()
            else:
                return False
        if len(two_card_values) != 2:
            return False
        max_two_card_value = max(two_card_values)
        min_two_card_value = min(two_card_values)
        return [max_two_card_value, min_two_card_value, other_card_value]

    def is_one_pair(self):
        """Checks whether a hand contains one pair, for poker. Returns False or list."""
        two_card_value = None
        other_card_values = []
        for card in self.card_list:
            card_value = card.get_value()
            count_value = self.count_value(card_value)
            if count_value == 2:
                two_card_value = card.poker_value()
            elif count_value == 1:
                other_card_values.append(card.poker_value())
            else:
                return False
        if two_card_value is None or len(other_card_values) != 3:
            return False
        return [two_card_value] + sorted(other_card_values)[::-1]

    def poker_high_card(self):
        """Returns a list of poker card values, sorted from highest to lowest."""
        card_values = [card.poker_value() for card in self.card_list]
        return sorted(card_values)[::-1]

    def poker_beats(self, other_hand):
        """
        Compares hand with another hand, to see if this hand beats the other at poker. Returns true, false or none.
        """
        # Check if either hand is a royal flush
        if self.is_royal_flush():
            if other_hand.is_royal_flush():
                return None
            return True
        if other_hand.is_royal_flush():
            return False
        # Check if either hand is a straight flush
        straight_flush = self.is_straight_flush()
        other_straight_flush = other_hand.is_straight_flush()
        if straight_flush:
            if not other_straight_flush:
                return True
            if straight_flush == other_straight_flush:
                return None
            return straight_flush > other_straight_flush
        if other_straight_flush:
            return False
        # Check if either hand is four of a kind
        four_of_a_kind = self.is_four_of_a_kind()
        other_four_of_a_kind = other_hand.is_four_of_a_kind()
        if four_of_a_kind:
            if not other_four_of_a_kind:
                return True
            return Commons.list_greater(four_of_a_kind, other_four_of_a_kind)
        if other_four_of_a_kind:
            return False
        # Check if either hand is a full house
        full_house = self.is_full_house()
        other_full_house = other_hand.is_full_house()
        if full_house:
            if not other_full_house:
                return True
            return Commons.list_greater(full_house, other_full_house)
        if other_full_house:
            return False
        # Check if either hand is a flush
        flush = self.is_flush()
        other_flush = other_hand.is_flush()
        if flush:
            if not other_flush:
                return True
            return flush > other_flush
        if other_flush:
            return False
        # Check if either hand is a straight
        straight = self.is_straight()
        other_straight = other_hand.is_straight()
        if straight:
            if not other_straight:
                return True
            return straight > other_straight
        if other_straight:
            return False
        # Check if either hand is 3 of a kind
        three_of_a_kind = self.is_three_of_a_kind()
        other_three_of_a_kind = other_hand.is_three_of_a_kind()
        if three_of_a_kind:
            if not other_three_of_a_kind:
                return True
            return Commons.list_greater(three_of_a_kind, other_three_of_a_kind)
        if other_three_of_a_kind:
            return False
        # Check if either hand is 2 pairs
        two_pairs = self.is_two_pairs()
        other_two_pairs = other_hand.is_two_pairs()
        if two_pairs:
            if not other_two_pairs:
                return True
            return Commons.list_greater(two_pairs, other_two_pairs)
        if other_two_pairs:
            return False
        # Check if either hand is 1 paid
        one_pair = self.is_one_pair()
        other_one_pair = other_hand.is_one_pair()
        if one_pair:
            if not other_one_pair:
                return True
            return Commons.list_greater(one_pair, other_one_pair)
        if other_one_pair:
            return False
        # Compare by high card
        high_card = self.poker_high_card()
        other_high_card = other_hand.poker_high_card()
        return Commons.list_greater(high_card, other_high_card)

    def __str__(self):
        return self.to_string()

    def to_string(self):
        """Returns a string representing the cards in the hand."""
        return ", ".join([card.to_string() for card in self.card_list])

    @staticmethod
    def from_two_letter_code_list(deck, two_letter_code_list):
        """Creates a hand from a deck and a list of 2 letter codes."""
        suit_dict = {
            "C": Card.SUIT_CLUBS,
            "S": Card.SUIT_SPADES,
            "H": Card.SUIT_HEARTS,
            "D": Card.SUIT_DIAMONDS,
        }
        value_dict = {
            "A": Card.CARD_ACE,
            "2": Card.CARD_2,
            "3": Card.CARD_3,
            "4": Card.CARD_4,
            "5": Card.CARD_5,
            "6": Card.CARD_6,
            "7": Card.CARD_7,
            "8": Card.CARD_8,
            "9": Card.CARD_9,
            "T": Card.CARD_10,
            "J": Card.CARD_JACK,
            "Q": Card.CARD_QUEEN,
            "K": Card.CARD_KING,
        }
        new_hand = Hand(None)
        for letter_code in two_letter_code_list:
            suit_code = letter_code[1]
            value_code = letter_code[0]
            card_suit = suit_dict[suit_code]
            card_value = value_dict[value_code]
            new_hand.add_card(deck.get_card(card_suit, card_value))
        return new_hand


class Game:
    """
    Generic Game object. Stores players and location.
    """

    def __init__(self, player_list, destination_obj):
        """
        :type player_list: list[destination.User]
        :type destination_obj: destination.Destination
        """
        self.players = set(player_list)
        self.destination = destination_obj
        self.start_time = time.time()
        self.last_time = time.time()
        self.lost = False

    def update_time(self):
        """Updates the time that something last happened to this game"""
        self.last_time = time.time()

    def contains_player(self, user_obj):
        """Whether or not this game contains a specified player"""
        return user_obj in self.players

    def is_lost(self):
        """Lost getter. (Avoided the getLost() joke.)"""
        return self.lost


class HigherOrLowerGame(Game):
    """
    Game of Higher or Lower.
    """

    HIGH_SCORE_NAME = "higher_or_lower"

    def __init__(self, user_obj, destination_obj):
        super().__init__([user_obj], destination_obj)
        self.card_list = []
        self.deck = Deck()
        self.deck.shuffle()
        function_dispatcher = user_obj.server.hallo.function_dispatcher
        high_scores_class = function_dispatcher.get_function_by_name("highscores")
        self.high_scores_obj = function_dispatcher.get_function_object(
            high_scores_class
        )  # type: HighScores
        self.last_card = None
        self.turns = 0

    def get_next_card(self):
        """Gets a new card from the deck and adds to the list"""
        self.update_time()
        self.turns += 1
        next_card = self.deck.get_next_card()
        self.card_list.append(next_card)
        self.last_card = next_card
        return next_card

    def get_turns(self):
        """Turns getter"""
        return self.turns

    def check_high_score(self):
        """Checks if this game is a high score. Returns boolean"""
        high_score = self.high_scores_obj.get_high_score(self.HIGH_SCORE_NAME)
        if high_score is None:
            return True
        last_score = int(high_score["data"]["cards"])
        current_score = self.turns
        if self.lost:
            current_score = self.turns - 1
        if current_score > last_score:
            return True
        return False

    def start_game(self):
        """Starts the new game"""
        first_card = self.get_next_card()
        return "You have started a game of higher or lower. Your first card is: {}.".format(
            first_card.to_string()
        )

    def update_high_score(self):
        """Updates the high score with current game. Checks that it is high score first."""
        if not self.check_high_score():
            return False
        current_score = self.turns
        if self.lost:
            current_score = self.turns - 1
        user_name = list(self.players)[0].name
        score = "{} cards".format(current_score)
        game_data = {"cards": current_score}
        self.high_scores_obj.add_high_score(
            self.HIGH_SCORE_NAME, score, user_name, game_data
        )
        return True

    def guess_higher(self):
        """User has guessed the next card is higher."""
        last_card = self.last_card
        next_card = self.get_next_card()
        if next_card.to_int() > last_card.to_int():
            output_string = (
                "Your {} card is {}, which is higher! Congrats! Do you think the next card will be "
                "higher or lower?".format(
                    Commons.ordinal(self.turns), next_card.to_string()
                )
            )
            return output_string
        if next_card.to_int() == last_card.to_int():
            output_string = (
                "Your {} card is {}, which is the same (that's fine.) Do you think the next card will "
                "be higher or lower?".format(
                    Commons.ordinal(self.turns), next_card.to_string()
                )
            )
            return output_string
        if next_card.to_int() < last_card.to_int():
            self.lost = True
            # high scores
            is_high_score = self.check_high_score()
            previous_score_text = ""
            if is_high_score:
                previous_score = self.high_scores_obj.get_high_score(
                    self.HIGH_SCORE_NAME
                )
                previous_score_text = "(previous highscore was: {}, set by {} .)".format(
                    previous_score["score"],
                    previous_score["player"],
                    Commons.format_unix_time(previous_score["date"]),
                )
                self.update_high_score()
            # Output message
            output_string = "Your {} card is {}. Sorry, that's lower, you lose.".format(
                Commons.ordinal(self.turns), next_card.to_string()
            )
            if is_high_score:
                output_string += " You managed {} cards though, that's a new highscore! {}".format(
                    self.turns - 1, previous_score_text
                )
            else:
                output_string += " You managed {} cards though.".format(self.turns - 1)
            return output_string

    def guess_lower(self):
        """User has guessed the next card is higher."""
        last_card = self.last_card
        next_card = self.get_next_card()
        if next_card.to_int() < last_card.to_int():
            output_string = (
                "Your {} card is {}, which is lower! Congrats! Do you think the next card will "
                "be higher or lower?".format(
                    Commons.ordinal(self.turns), next_card.to_string()
                )
            )
            return output_string
        if next_card.to_int() == last_card.to_int():
            output_string = (
                "Your {} card is {}, which is the same (that's fine.) Do you think the next card will "
                "be higher or lower?".format(
                    Commons.ordinal(self.turns), next_card.to_string()
                )
            )
            return output_string
        if next_card.to_int() > last_card.to_int():
            self.lost = True
            # high scores
            is_high_score = self.check_high_score()
            previous_score_text = ""
            if is_high_score:
                previous_score = self.high_scores_obj.get_high_score(
                    self.HIGH_SCORE_NAME
                )
                previous_score_text = "(previous highscore was: {}, set by {} {}.)".format(
                    previous_score["score"],
                    previous_score["player"],
                    Commons.format_unix_time(previous_score["date"]),
                )
                self.update_high_score()
            # Output message
            output_string = "Your {} card is {}. Sorry, that's higher, you lose.".format(
                Commons.ordinal(self.turns), next_card.to_string()
            )
            if is_high_score:
                output_string += " You managed {} cards though, that's a new highscore!{}".format(
                    self.turns - 1, previous_score_text
                )
            else:
                output_string += " You managed {} cards though.".format(
                    str(self.turns - 1)
                )
            return output_string

    def quit_game(self):
        """User has quit the game"""
        # check high scores
        is_high_score = self.check_high_score()
        if is_high_score:
            previous_score = self.high_scores_obj.get_high_score(self.HIGH_SCORE_NAME)
            previous_score_text = "(previous highscore was: {}, set by {} {}.)".format(
                previous_score["score"],
                previous_score["player"],
                Commons.format_unix_time(previous_score["date"]),
            )
            self.update_high_score()
            # Create output
            return (
                "Sorry to see you quit, you had managed {} cards, "
                "which is a new highscore!{}".format(
                    self.turns - 1, previous_score_text
                )
            )
        else:
            return "Sorry to see you quit, you had managed {} cards.".format(
                self.turns - 1
            )


class BlackjackGame(Game):
    """
    Game of Blackjack.
    """

    HIGH_SCORE_NAME = "blackjack"

    def __init__(self, user_obj, destination_obj):
        super().__init__([user_obj], destination_obj)
        self.deck = Deck()
        self.deck.shuffle()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.last_card = None
        self.high_scores_obj = None

    def start_game(self):
        """Starts the game. Returns the opening line"""
        # Deal out the opening hands
        first_card = self.deck.get_next_card()
        self.player_hand.add_card(first_card)
        second_card = self.deck.get_next_card()
        self.dealer_hand.add_card(second_card)
        third_card = self.deck.get_next_card()
        self.player_hand.add_card(third_card)
        forth_card = self.deck.get_next_card()
        self.dealer_hand.add_card(forth_card)
        # Write the first half of output
        output_string = (
            "You have started a game of Blackjack (H17), "
            "you have been dealt a {} and a {}.".format(
                first_card.to_string(), third_card.to_string()
            )
        )
        # Check if they have been dealt a blackjack
        if self.player_hand.contains_value(Card.CARD_ACE) and any(
            [
                self.player_hand.contains_value(value)
                for value in [
                    Card.CARD_10,
                    Card.CARD_JACK,
                    Card.CARD_QUEEN,
                    Card.CARD_KING,
                ]
            ]
        ):
            return output_string + "Congratulations! That's a blackjack! You win."
        # Write the rest of the output
        output_string += (
            " The dealer has a {} and another, covered, card. "
            "Would you like to hit or stick?".format(second_card.to_string())
        )
        return output_string

    def hit(self):
        """Player decided to hit."""
        new_card = self.deck.get_next_card()
        self.player_hand.add_card(new_card)
        output_string = "You have been dealt a {},".format(new_card.to_string())
        if self.player_hand.sum_total() > 21:
            self.lost = True
            return (
                output_string + " which means your hand sums to {}. "
                "You've gone bust. You lose, sorry.".format(
                    self.player_hand.sum_total()
                )
            )
        return output_string + " would you like to hit or stick?"

    def stick(self):
        """Player decided to stick."""
        # Get total of player's hand
        player_sum = self.player_hand.blackjack_total()
        output_string = "Your hand is: {}\n".format(self.player_hand.to_string())
        # Dealer continues to deal himself cards, in accordance with H17 rules
        dealer_new_cards = 0
        if self.dealer_hand.blackjack_total() < 17 or (
            self.dealer_hand.blackjack_total() == 17
            and self.dealer_hand.contains_value(Card.CARD_ACE)
        ):
            dealer_new_cards += 1
            dealer_new_card = self.deck.get_next_card()
            self.dealer_hand.add_card(dealer_new_card)
        # if dealer has dealt himself more cards, say that.
        if dealer_new_cards != 0:
            card_plural = "card" if dealer_new_cards == 1 else "cards"
            output_string += "The dealer deals himself {} more {}.\n".format(
                dealer_new_cards, card_plural
            )
        # Say the dealer's hand
        output_string += "The dealer's hand is: {}\n".format(
            self.dealer_hand.to_string()
        )
        # Check if dealer is bust
        if self.dealer_hand.blackjack_total() > 21:
            output_string += "Dealer busts.\n"
        # See who wins
        if self.dealer_hand.blackjack_total() == player_sum:
            output_string += "It's a tie, dealer wins."
        elif player_sum < self.dealer_hand.blackjack_total() <= 21:
            output_string += "Dealer wins."
        else:
            output_string += "You win! Congratulations!"
        return output_string

    def quit_game(self):
        """Player wants to quit"""
        return "You have quit the game. You had {} and the dealer had {}.".format(
            self.player_hand.blackjack_total(), self.dealer_hand.blackjack_total()
        )


class DDRGame(Game):
    """
    Game of DDR.
    """

    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"
    HIGH_SCORE_NAME = "ddr"
    DIRECTION_LEFT = "<"
    DIRECTION_RIGHT = ">"
    DIRECTION_UP = "^"
    DIRECTION_DOWN = "v"

    def __init__(self, game_difficulty, user_obj, destination_obj):
        """
        :param game_difficulty: Difficulty of the game
        :type game_difficulty: str
        :param user_obj: User who started the game
        :type user_obj: destination.User
        :param destination_obj: Channel the game is happening in
        :type destination_obj: destination.Destination
        """
        super().__init__([user_obj], destination_obj)
        self.players_moved = set()
        self.player_dict = {user_obj: {"hits": 0, "lag": 0}}
        self.difficulty = game_difficulty
        function_dispatcher = user_obj.server.hallo.function_dispatcher
        high_scores_class = function_dispatcher.get_function_by_name("highscores")
        self.high_scores_obj = function_dispatcher.get_function_object(
            high_scores_class
        )  # type: HighScores
        self.last_move = None
        self.can_join = True
        self.game_over = False
        self.num_turns = None

    def start_game(self):
        """Launches the new thread to play the game."""
        Thread(target=self.run).start()

    def run(self):
        """Launched into a new thread, this function actually plays the DDR game."""
        server_obj = self.destination.server
        chan_obj = self.destination if isinstance(self.destination, Channel) else None
        user_obj = self.destination if isinstance(self.destination, User) else None
        if self.difficulty == self.DIFFICULTY_HARD:
            self.num_turns = 20
            time_min = 1
            time_max = 2
        elif self.difficulty == self.DIFFICULTY_MEDIUM:
            self.num_turns = 15
            time_min = 3
            time_max = 5
        else:
            self.num_turns = 10
            time_min = 5
            time_max = 8
        directions = [
            self.DIRECTION_LEFT,
            self.DIRECTION_RIGHT,
            self.DIRECTION_UP,
            self.DIRECTION_DOWN,
        ]
        # Send first message and wait for new players to join
        output_string = "Starting new game of DDR in 5 seconds, say 'join' to join."
        server_obj.send(
            EventMessage(server_obj, chan_obj, user_obj, output_string, inbound=False)
        )
        time.sleep(5)
        # Output how many players joined and begin
        self.can_join = False
        output_string = "{} players joined: {}. Starting game.".format(
            len(self.players), ", ".join([p.name for p in self.players])
        )
        server_obj.send(
            EventMessage(server_obj, chan_obj, user_obj, output_string, inbound=False)
        )
        # Do the various turns of the game
        for _ in range(self.num_turns):
            if self.is_game_over():
                return
            direction = random.choice(directions)
            self.last_move = direction
            self.players_moved = set()
            self.update_time()
            server_obj.send(
                EventMessage(server_obj, chan_obj, user_obj, direction, inbound=False)
            )
            time.sleep(random.uniform(time_min, time_max))
        # end game
        # Set game over
        self.game_over = True
        output_string = "Game has finished!"
        server_obj.send(
            EventMessage(server_obj, chan_obj, user_obj, output_string, inbound=False)
        )
        # See who wins
        winner_player = self.find_winner()
        output_string = "Winner is: " + winner_player.name
        server_obj.send(
            EventMessage(server_obj, chan_obj, user_obj, output_string, inbound=False)
        )
        # Output player ratings
        for player in self.players:
            output_string = self.player_rating(player)
            server_obj.send(
                EventMessage(
                    server_obj, chan_obj, user_obj, output_string, inbound=False
                )
            )
        # Check if they have a highscore
        if self.check_high_score(winner_player):
            self.update_high_score(winner_player)
            highscore_evt = EventMessage(
                server_obj,
                chan_obj,
                user_obj,
                "{} has set a new DDR highscore with {} hits and {} lag!".format(
                    winner_player.name,
                    self.player_dict[winner_player]["hits"],
                    self.player_dict[winner_player]["lag"],
                ),
                inbound=False,
            )
            server_obj.send(highscore_evt)
            # Game ended

    def find_winner(self):
        """Determines which player won."""
        winner = None
        winner_hits = 0
        winner_lag = 0
        for player in self.player_dict:
            if self.player_dict[player]["hits"] > winner_hits:
                winner = player
                winner_hits = self.player_dict[player]["hits"]
                winner_lag = self.player_dict[player]["lag"]
            elif self.player_dict[player]["hits"] == winner_hits:
                if self.player_dict[player]["lag"] < winner_lag:
                    winner = player
                    winner_hits = self.player_dict[player]["hits"]
                    winner_lag = self.player_dict[player]["lag"]
        return winner

    def player_rating(self, player_obj):
        """Determines rating for a specified player"""
        hits = self.player_dict[player_obj]["hits"]
        lag = self.player_dict[player_obj]["lag"]
        if hits == self.num_turns:
            if lag < 5:
                return "Marvelous!! ({} hits, {}s lag.)".format(hits, lag)
            else:
                return "Perfect! ({} hits, {}s lag.)".format(hits, lag)
        elif hits >= self.num_turns * 0.75:
            return "Great ({} hits, {}s lag.)".format(hits, lag)
        elif hits >= self.num_turns * 0.5:
            return "Good ({} hits, {}s lag.)".format(hits, lag)
        elif hits >= self.num_turns * 0.25:
            return "Almost ({} hits, {}s lag.)".format(hits, lag)
        else:
            return "Failure. ({} hits, {}s lag.)".format(hits, lag)

    def check_high_score(self, winner_player):
        """Checks if this game is a high score. Returns boolean"""
        high_score = self.high_scores_obj.get_high_score(self.HIGH_SCORE_NAME)
        if high_score is None:
            return True
        last_hits = int(high_score["data"]["hits"])
        last_lag = float(high_score["data"]["lag"])
        winner_hits = self.player_dict[winner_player]["hits"]
        winner_lag = self.player_dict[winner_player]["lag"]
        if winner_hits > last_hits:
            return True
        if winner_hits == last_hits and winner_lag < last_lag:
            return True
        return False

    def update_high_score(self, winner_player):
        """Updates the high score with current game. Checks that it is high score first."""
        if not self.check_high_score(winner_player):
            return False
        winner_hits = self.player_dict[winner_player]["hits"]
        winner_lag = self.player_dict[winner_player]["lag"]
        winner_score = "{0} hits, {1:.3f}s lag".format(winner_hits, winner_lag)
        game_data = {"hits": winner_hits, "lag": winner_lag}
        self.high_scores_obj.add_high_score(
            self.HIGH_SCORE_NAME, winner_score, winner_player.name, game_data
        )
        return True

    def can_join(self):
        """Boolean, whether players can join."""
        return self.can_join

    def is_game_over(self):
        """Boolean, whether the game is over."""
        return self.game_over

    def join_game(self, user_obj):
        if self.can_join:
            self.players.add(user_obj)
            self.player_dict[user_obj] = {"hits": 0, "lag": 0}
            return "{} has joined.".format(user_obj.name)
        else:
            return "This game cannot be joined now."

    def make_move(self, direction, user_obj):
        if user_obj not in self.players:
            return
        if user_obj in self.players_moved:
            return
        self.players_moved.add(user_obj)
        if direction == self.last_move:
            lag = time.time() - self.last_time
            self.player_dict[user_obj]["hits"] += 1
            self.player_dict[user_obj]["lag"] += lag
        return

    def quit_game(self, user_obj):
        if user_obj not in self.players:
            return "You're not playing"
        self.players.remove(user_obj)
        del self.player_dict[user_obj]
        if len(self.players) == 0:
            self.game_over = True
            return "All players quit. game over."
        else:
            return "{} has quit the game.".format(user_obj.name)
