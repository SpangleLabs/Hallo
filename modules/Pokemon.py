from Function import Function
from xml.dom import minidom
import random

class RandomPokemon(Function):
    '''
    Random pokemon function
    '''
    #Name for use in help listing
    mHelpName = "i choose you"
    #Names which can be used to address the function
    mNames = set(["i choose you","ichooseyou","random pokemon","pokemon"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Picks a random pokemon from generation I to generation V. Format: i choose you"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemonListXml = doc.getElementsByTagName("pokemon_list")[0]
        pokemonList = []
        #Loop through pokemon, adding to pokemonList
        for pokemonXml in pokemonListXml.getElementsByTagName("pokemon"):
            pokemonDict = {}
            pokemonDict['name'] = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            pokemonList.append(pokemonDict)
        randomPokemon = random.choice(pokemonList)
        return "I choose you, " + randomPokemon['name'] + "!"

class PickATeam(Function):
    '''
    Function to select a random pokemon team
    '''
    #Name for use in help listing
    mHelpName = "pick a team"
    #Names which can be used to address the function
    mNames = set(["pick a team","pickateam"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Generates a team of pokemon for you."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemonListXml = doc.getElementsByTagName("pokemon_list")[0]
        pokemonList = []
        #Loop through pokemon, adding to pokemonList
        for pokemonXml in pokemonListXml.getElementsByTagName("pokemon"):
            pokemonDict = {}
            pokemonDict['name'] = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            pokemonList.append(pokemonDict)
        randomPokemonTeam = random.sample(pokemonList,6)
        return "Your team is: " + ", ".join([pokemon['name'] for pokemon in randomPokemonTeam[:5]]) + " and " + randomPokemonTeam[5]['name'] + "."

class FullyEvolvedTeam(Function):
    '''
    Function to select a random fully evolved pokemon team
    '''
    #Name for use in help listing
    mHelpName = "fully evolved team"
    #Names which can be used to address the function
    mNames = set(["pick a fully evolved team","fully evolved team","fullyevolvedteam"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Pick a fully evolved pokemon team."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemonListXml = doc.getElementsByTagName("pokemon_list")[0]
        pokemonList = []
        #Loop through pokemon, adding to pokemonList if they cannot evolve.
        for pokemonXml in pokemonListXml.getElementsByTagName("pokemon"):
            pokemonDict = {}
            pokemonDict['name'] = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            evolutionChoices = len(pokemonXml.getElementsByTagName("evolve_to"))
            if(evolutionChoices==0):
                pokemonList.append(pokemonDict)
        randomPokemonTeam = random.sample(pokemonList,6)
        return "Your team is: " + ", ".join([pokemon['name'] for pokemon in randomPokemonTeam[:5]]) + " and " + randomPokemonTeam[5]['name'] + "."

class Pokedex(Function):
    '''
    Function to return pokedex entries
    '''
    #Name for use in help listing
    mHelpName = "pokedex"
    #Names which can be used to address the function
    mNames = set(["pokedex","dex"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random pokedex entry for a given pokemon."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.lower().split()
        #Load XML
        doc = minidom.parse("store/pokemon/pokemon.xml")
        pokemonListXml = doc.getElementsByTagName("pokemon_list")[0]
        #Loop through pokemon, searching for the specified pokemon
        selectedPokemonXml = None
        for pokemonXml in pokemonListXml.getElementsByTagName("pony_episode"):
            pokemonName = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            pokemonNumber = pokemonXml.getElementsByTagName("dex_number")[0].firstChild.data
            if(lineClean == pokemonName or lineClean == pokemonNumber):
                selectedPokemonXml = pokemonXml
                break
        #If pokemon couldn't be found, return a message to the user
        if(selectedPokemonXml is None):
            return "No available pokedex data."
        #Select a random pokedex entry
        pokedexEntryListXml = selectedPokemonXml.getElementsByTagName("dex_entry_list")
        pokedexEntryXml = random.choice(pokedexEntryListXml.getElementsByTagName("dex_entry"))
        pokedexEntryText = pokedexEntryXml.firstChild.data
        return pokedexEntryText
        




