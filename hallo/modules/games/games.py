from hallo.destination import Channel, User
from hallo.events import EventMessage
import random
import time

from hallo.inc.commons import Commons
from threading import Thread

import hallo.modules.games.cards


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
        self.deck = hallo.modules.games.cards.Deck()
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
        self.deck = hallo.modules.games.cards.Deck()
        self.deck.shuffle()
        self.player_hand = hallo.modules.games.cards.Hand()
        self.dealer_hand = hallo.modules.games.cards.Hand()
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
        if self.player_hand.contains_value(hallo.modules.games.cards.Card.CARD_ACE) and any(
            [
                self.player_hand.contains_value(value)
                for value in [
                    hallo.modules.games.cards.Card.CARD_10,
                    hallo.modules.games.cards.Card.CARD_JACK,
                    hallo.modules.games.cards.Card.CARD_QUEEN,
                    hallo.modules.games.cards.Card.CARD_KING,
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
            and self.dealer_hand.contains_value(hallo.modules.games.cards.Card.CARD_ACE)
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
