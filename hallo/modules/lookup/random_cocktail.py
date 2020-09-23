from xml.dom import minidom

from hallo.function import Function
from hallo.inc.commons import Commons


class RandomCocktail(Function):
    """
    Selects and outputs a random cocktail from store/cocktail_list.xml
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random cocktail"
        # Names which can be used to address the function
        self.names = {"random cocktail", "randomcocktail"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Delivers ingredients and recipes for a random cocktail. Format: random cocktail"

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/cocktail_list.xml")
        cocktail_list_elem = doc.getElementsByTagName("cocktail_list")[0]
        random_cocktail_elem = Commons.get_random_choice(
            cocktail_list_elem.getElementsByTagName("cocktail")
        )[0]
        random_cocktail_name = random_cocktail_elem.getElementsByTagName("name")[
            0
        ].firstChild.data
        random_cocktail_instructions = random_cocktail_elem.getElementsByTagName(
            "instructions"
        )[0].firstChild.data
        output_string = "Randomly selected cocktail is: {}. The ingredients are: ".format(
            random_cocktail_name
        )
        ingredient_list = []
        for ingredient_elem in random_cocktail_elem.getElementsByTagName("ingredients"):
            ingredient_amount = ingredient_elem.getElementsByTagName("amount")[
                0
            ].firstChild.data
            ingredient_name = ingredient_elem.getElementsByTagName("name")[
                0
            ].firstChild.data
            ingredient_list.append(ingredient_amount + ingredient_name)
        output_string += (
            ", ".join(ingredient_list)
            + ". The recipe is: "
            + random_cocktail_instructions
        )
        if output_string[-1] != ".":
            output_string += "."
        return event.create_response(output_string)
