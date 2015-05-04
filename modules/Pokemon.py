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
        #Loop through pony episodes, adding to episodeList (or songList, if there is a song)
        for pokemonXml in pokemonListXml.getElementsByTagName("pony_episode"):
            pokemonDict = {}
            pokemonDict['name'] = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            pokemonList.append(pokemonDict)
        randomPokemon = random.choice(pokemonList)
        return "I choose you, " + randomPokemon['Name'] + "!"

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
        #Loop through pony episodes, adding to episodeList (or songList, if there is a song)
        for pokemonXml in pokemonListXml.getElementsByTagName("pony_episode"):
            pokemonDict = {}
            pokemonDict['name'] = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            pokemonList.append(pokemonDict)
        randomPokemonTeam = random.sample(pokemonList,6)
        return "Your team is: " + ", ".join([pokemon['Name'] for pokemon in randomPokemonTeam[:5]]) + " and " + randomPokemonTeam[5]['Name'] + "."

class FullyEvolvedTeam(Function):
    '''
    Function to select a random pokemon team
    '''
    #Name for use in help listing
    mHelpName = "fully evolved team"
    #Names which can be used to address the function
    mNames = set(["pick a fully evolved team","fully evolved team","fullyevolvedteam"])
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
        #Loop through pony episodes, adding to episodeList (or songList, if there is a song)
        for pokemonXml in pokemonListXml.getElementsByTagName("pony_episode"):
            pokemonDict = {}
            pokemonDict['name'] = pokemonXml.getElementsByTagName("name")[0].firstChild.data
            evolutionChoices = len(pokemonXml.getElementsByTagName("evolve_to"))
            if(evolutionChoices==0):
                pokemonList.append(pokemonDict)
        randomPokemonTeam = random.sample(pokemonList,6)
        return "Your team is: " + ", ".join([pokemon['Name'] for pokemon in randomPokemonTeam[:5]]) + " and " + randomPokemonTeam[5]['Name'] + "."

