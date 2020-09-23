import difflib
from xml.dom import minidom

from hallo.function import Function


class Cocktail(Function):
    """
    Cocktail lookup function.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "cocktail"
        # Names which can be used to address the function
        self.names = {"cocktail"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Returns ingredients and instructions for a given cocktail (or closest guess). "
            "Format: cocktail <name>"
        )

    def run(self, event):
        """Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>"""
        doc = minidom.parse("store/cocktail_list.xml")
        cocktail_list_elem = doc.getElementsByTagName("cocktail_list")[0]
        cocktail_names = []
        # Loop through cocktails, adding names to list
        cocktail_elem = None
        for cocktail_elem in cocktail_list_elem.getElementsByTagName("cocktail"):
            cocktail_name = cocktail_elem.getElementsByTagName("name")[
                0
            ].firstChild.data
            cocktail_names.append(cocktail_name)
        # Find the closest matching names
        closest_matches = difflib.get_close_matches(
            event.command_args.lower(), cocktail_names
        )
        # If there are no close matches, return error
        if len(closest_matches) == 0 or closest_matches[0] == "":
            return event.create_response("I haven't got anything close to that name.")
        # Get closest match XML
        closest_match_name = closest_matches[0]
        for cocktail_elem in cocktail_list_elem.getElementsByTagName("cocktail"):
            cocktail_name = cocktail_elem.getElementsByTagName("name")[
                0
            ].firstChild.data
            if cocktail_name.lower() == closest_match_name.lower():
                break
        # Get instructions
        cocktail_instructions = cocktail_elem.getElementsByTagName("instructions")[
            0
        ].firstChild.data
        # Get list of ingredients
        ingredient_list = []
        for ingredient_elem in cocktail_elem.getElementsByTagName("ingredients"):
            ingredient_amount = ingredient_elem.getElementsByTagName("amount")[
                0
            ].firstChild.data
            ingredient_name = ingredient_elem.getElementsByTagName("name")[
                0
            ].firstChild.data
            ingredient_list.append(ingredient_amount + ingredient_name)
        # Construct output
        output_string = "Closest I have is {}.".format(closest_match_name)
        output_string += "The ingredients are: {}.".format(", ".join(ingredient_list))
        output_string += "The recipe is: {}".format(cocktail_instructions)
        if output_string[-1] != ".":
            output_string += "."
        return event.create_response(output_string)