from Function import Function
from inc.Commons import Commons
from xml.dom import minidom


class RandomPokemon(Function):
    """
    Random pokemon function
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "i choose you"
        # Names which can be used to address the function
        self.names = {"i choose you", "ichooseyou", "random pokemon", "pokemon"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Picks a random pokemon from generation I to generation V. Format: i choose you"

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemon_list_elem = doc.getElementsByTagName("pokemon_list")[0]
        pokemon_list = []
        # Loop through pokemon, adding to pokemon_list
        for pokemon_elem in pokemon_list_elem.getElementsByTagName("pokemon"):
            pokemon_dict = {'name': pokemon_elem.getElementsByTagName("name")[0].firstChild.data}
            pokemon_list.append(pokemon_dict)
        random_pokemon = Commons.get_random_choice(pokemon_list)[0]
        return "I choose you, {}!".format(random_pokemon['name'])


class PickATeam(Function):
    """
    Function to select a random pokemon team
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "pick a team"
        # Names which can be used to address the function
        self.names = {"pick a team", "pickateam"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Generates a team of pokemon for you."

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemon_list_elem = doc.getElementsByTagName("pokemon_list")[0]
        pokemon_list = []
        # Loop through pokemon, adding to pokemon_list
        for pokemon_elem in pokemon_list_elem.getElementsByTagName("pokemon"):
            pokemon_dict = {'name': pokemon_elem.getElementsByTagName("name")[0].firstChild.data}
            pokemon_list.append(pokemon_dict)
        random_pokemon_team = Commons.get_random_choice(pokemon_list, 6)
        return "Your team is: {} and {}.".format(", ".join([pokemon['name'] for pokemon in random_pokemon_team[:5]]),
                                                 random_pokemon_team[5]['name'])


class FullyEvolvedTeam(Function):
    """
    Function to select a random fully evolved pokemon team
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "fully evolved team"
        # Names which can be used to address the function
        self.names = {"pick a fully evolved team", "fully evolved team", "fullyevolvedteam"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Pick a fully evolved pokemon team."

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemon_list_elem = doc.getElementsByTagName("pokemon_list")[0]
        pokemon_list = []
        # Loop through pokemon, adding to pokemon_list if they cannot evolve.
        for pokemon_elem in pokemon_list_elem.getElementsByTagName("pokemon"):
            pokemon_dict = {'name': pokemon_elem.getElementsByTagName("name")[0].firstChild.data}
            evolution_choices = len(pokemon_elem.getElementsByTagName("evolve_to"))
            if evolution_choices == 0:
                pokemon_list.append(pokemon_dict)
        random_pokemon_team = Commons.get_random_choice(pokemon_list, 6)
        return "Your team is: {} and {}.".format(", ".join([pokemon['name'] for pokemon in random_pokemon_team[:5]]),
                                                 random_pokemon_team[5]['name'])


class Pokedex(Function):
    """
    Function to return pokedex entries
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "pokedex"
        # Names which can be used to address the function
        self.names = {"pokedex", "dex"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random pokedex entry for a given pokemon."

    def run(self, event):
        line_clean = event.command_args.lower().split()
        # Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemon_list_elem = doc.getElementsByTagName("pokemon_list")[0]
        # Loop through pokemon, searching for the specified pokemon
        selected_pokemon_elem = None
        for pokemon_elem in pokemon_list_elem.getElementsByTagName("pony_episode"):
            pokemon_name = pokemon_elem.getElementsByTagName("name")[0].firstChild.data.lower()
            pokemon_number = pokemon_elem.getElementsByTagName("dex_number")[0].firstChild.data
            if line_clean == pokemon_name or line_clean == pokemon_number:
                selected_pokemon_elem = pokemon_elem
                break
        # If pokemon couldn't be found, return a message to the user
        if selected_pokemon_elem is None:
            return "No available pokedex data."
        # Select a random pokedex entry
        pokedex_entry_list_elem = selected_pokemon_elem.getElementsByTagName("dex_entry_list")
        pokedex_entry_elem = Commons.get_random_choice(pokedex_entry_list_elem.getElementsByTagName("dex_entry"))[0]
        pokedex_entry_text = pokedex_entry_elem.firstChild.data
        return pokedex_entry_text
