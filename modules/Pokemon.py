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
    
    mPokemonDict = {}
    
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

