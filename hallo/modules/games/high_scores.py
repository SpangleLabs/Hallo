import time
from xml.dom import minidom

from hallo.function import Function
from hallo.inc.commons import Commons


class HighScores(Function):
    """
    High scores function, also stores all high scores.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "highscores"
        # Names which can be used to address the function
        self.names = {
            "highscores",
            "high scores",
            "highscore",
            "high score",
            "hiscore",
            "hiscores",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "View the highscores for all games. Format: highscores"
        self.high_scores = {}

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        try:
            high_score_dict = {}
            doc = minidom.parse("store/high_score_list.xml")
            # Loop through high scores
            for high_score_elem in doc.getElementsByTagName("high_score"):
                game_dict = {}
                # Get name
                game_name = high_score_elem.getElementsByTagName("game_name")[
                    0
                ].firstChild.data
                # Get date, add to dict
                game_date = high_score_elem.getElementsByTagName("date")[
                    0
                ].firstChild.data
                game_dict["date"] = float(game_date)
                # Get player name, add to dict
                player_name = high_score_elem.getElementsByTagName("player_name")[
                    0
                ].firstChild.data
                game_dict["player"] = player_name
                # Get score, add to dict
                game_score = high_score_elem.getElementsByTagName("score")[
                    0
                ].firstChild.data
                game_dict["score"] = game_score
                # Get extra data
                game_data = {}
                for data_elem in high_score_elem.getElementsByTagName("data"):
                    data_var = data_elem.getElementsByTagName("var")[0].firstChild.data
                    data_value = data_elem.getElementsByTagName("value")[
                        0
                    ].firstChild.data
                    game_data[data_var] = data_value
                game_dict["data"] = game_data
                # Add game to list
                high_score_dict[game_name] = game_dict
            # Create new object, set the highscore list and return it
            new_high_scores = HighScores()
            new_high_scores.high_scores = high_score_dict
            return new_high_scores
        except (FileNotFoundError, IOError):
            return HighScores()

    def save_function(self):
        """Saves the function, persistent functions only."""
        # Create document, with DTD
        doc_imp = minidom.DOMImplementation()
        doc_type = doc_imp.createDocumentType(
            qualifiedName="high_score_list",
            publicId="",
            systemId="high_score_list.dtd",
        )
        doc = doc_imp.createDocument(None, "high_score_list", doc_type)
        # get root element
        root = doc.getElementsByTagName("high_score_list")[0]
        # Loop through games
        for game_name in self.high_scores:
            high_score_elem = doc.createElement("high_score")
            # add game_name element
            game_name_elem = doc.createElement("game_name")
            game_name_elem.appendChild(doc.createTextNode(game_name))
            high_score_elem.appendChild(game_name_elem)
            # Add date element
            date_elem = doc.createElement("date")
            date_elem.appendChild(
                doc.createTextNode(str(self.high_scores[game_name]["date"]))
            )
            high_score_elem.appendChild(date_elem)
            # add player_name element
            player_name_elem = doc.createElement("player_name")
            player_name_elem.appendChild(
                doc.createTextNode(self.high_scores[game_name]["player"])
            )
            high_score_elem.appendChild(player_name_elem)
            # add score element
            score_elem = doc.createElement("score")
            score_elem.appendChild(
                doc.createTextNode(self.high_scores[game_name]["score"])
            )
            high_score_elem.appendChild(score_elem)
            # Loop through extra data, adding that.
            for data_var in self.high_scores[game_name]["data"]:
                data_elem = doc.createElement("data")
                # Add variable name element
                var_elem = doc.createElement("var")
                var_elem.appendChild(doc.createTextNode(data_var))
                data_elem.appendChild(var_elem)
                # Add value name element
                value_elem = doc.createElement("value")
                value_elem.appendChild(
                    doc.createTextNode(self.high_scores[game_name]["data"][data_var])
                )
                data_elem.appendChild(value_elem)
                # Add the data element to the high score
                high_score_elem.appendChild(data_elem)
            root.appendChild(high_score_elem)
        # save XML
        doc.writexml(
            open("store/high_score_list.xml", "w"), addindent="\t", newl="\r\n"
        )

    def run(self, event):
        output_lines = ["High scores:"]
        for game_name in self.high_scores:
            score = self.high_scores[game_name]["score"]
            player = self.high_scores[game_name]["player"]
            date = self.high_scores[game_name]["date"]
            output_lines.append(
                "{}> Score: {}, Player: {}, Date: {}".format(
                    game_name, score, player, Commons.format_unix_time(date)
                )
            )
        return event.create_response("\n".join(output_lines))

    def add_high_score(self, game_name, score, user_name, data=None):
        """Adds a new highscore to the list. Overwriting the old high score for that game if it exists"""
        if data is None:
            data = {}
        new_dict = {
            "score": score,
            "player": user_name,
            "date": time.time(),
            "data": data,
        }
        self.high_scores[game_name] = new_dict

    def get_high_score(self, game_name):
        """Returns the high score for a specified game."""
        if game_name in self.high_scores:
            return self.high_scores[game_name]
        return None
