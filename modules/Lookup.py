from Function import Function
from inc.commons import Commons
import random
from xml.dom import minidom
import difflib

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

class Cocktail(Function):
    '''
    Cocktail lookup function.
    '''
    #Name for use in help listing
    mHelpName = "cocktail"
    #Names which can be used to address the function
    mNames = set(["cocktail"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        'Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>'
        doc = minidom.parse("store/cocktail_list.xml")
        cocktailListXml = doc.getElementsByTagName("cocktail_list")[0]
        cocktailNames = []
        #Loop through cocktails, adding names to list
        for cocktailXml in cocktailListXml.getElementsByTagName("cocktail"):
            cocktailName = cocktailXml.getElementsByTagName("name")[0].firstChild.data
            cocktailNames.append(cocktailName)
        #Find the closest matching names
        closestMatches = difflib.get_close_matches(line.lower(),cocktailNames)
        #If there are no close matches, return error
        if(len(closestMatches)==0 or closestMatches[0]==''):
            return "I haven't got anything close to that name."
        #Get closest match XML
        closestMatchName = closestMatches[0]
        for cocktailXml in cocktailListXml.getElementsByTagName("cocktail"):
            cocktailName = cocktailXml.getElementsByTagName("name")[0].firstChild.data
            if(cocktailName.lower()==closestMatchName.lower()):
                break
        #Get instructions
        cocktailInstructions = cocktailXml.getElementsByTagName("instructions")[0].firstChild.data
        #Get list of ingredients
        ingredientList = []
        for ingredientXml in cocktailXml.getElementsByTagName("ingredients"):
            ingredientAmount = ingredientXml.getElementsByTagName("amount")[0].firstChild.data
            ingredientName = ingredientXml.getElementsByTagName("name")[0].firstChild.data
            ingredientList.append(ingredientAmount + ingredientName)
        #Construct output
        outputString = "Closest I have is " + closestMatchName + "."
        outputString += "The ingredients are: " + ", ".join(ingredientList) + "."
        outputString += "The recipe is: " + cocktailInstructions
        if(outputString[-1]!="."):
            outputString += "."
        return outputString
        
        
        
        
        
        
    