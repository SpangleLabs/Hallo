from Function import Function
from inc.commons import Commons
import random
from xml.dom import minidom

class UrbanDictionary(Function):
    '''
    Urban Dictionary lookup function.
    '''
    #Name for use in help listing
    mHelpName = "urban dictionary"
    #Names which can be used to address the function
    mNames = set(["urban dictionary","urban","urbandictionary","ud"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Gives the top urban dictionary definition for a word. Format: urban dictionary <word>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        urlLine = line.replace(' ','+').lower()
        url = 'http://api.urbandictionary.com/v0/define?term=' + urlLine
        urbandict = Commons.loadUrlJson(url)
        if(len(urbandict['list'])>0):
            definition = urbandict['list'][0]['definition'].replace("\r",'').replace("\n",'')
            return definition
        else:
            return "Sorry, I cannot find a definition for " + line + "."
        
class RandomCocktail(Function):
    '''
    Selects and outputs a random cocktail from store/cocktail_list.xml
    '''
    #Name for use in help listing
    mHelpName = "random cocktail"
    #Names which can be used to address the function
    mNames = set(["random cocktail","randomcocktail"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Delivers ingredients and recipes for a random cocktail. Format: random cocktail"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/cocktail_list.xml")
        cocktailListXml = doc.getElementsByTagName("cocktail_list")[0]
        randomCocktailXml = random.choice(cocktailListXml.getElementsByTagName("cocktail"))
        randomCocktailName = randomCocktailXml.getElementsByTagName("name")[0].firstChild.data
        randomCocktailInstructions = randomCocktailXml.getElementsByTagName("instructions")[0].firstChild.data
        outputString = "Randomly selected cocktail is: " + randomCocktailName + ". The ingredients are: "
        ingredientList = []
        for ingredientXml in randomCocktailXml.getElementsByTagName("ingredients"):
            ingredientAmount = ingredientXml.getElementsByTagName("amount")[0].firstChild.data
            ingredientName = ingredientXml.getElementsByTagName("name")[0].firstChild.data
            ingredientList.append(ingredientAmount + ingredientName)
        outputString += ", ".join(ingredientList) + ". The recipe is: " + randomCocktailInstructions
        if(outputString[-1]!='.'):
            outputString += "."
        return outputString
    