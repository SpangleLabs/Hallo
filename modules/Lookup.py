from Function import Function
from inc.commons import Commons
import random
from xml.dom import minidom
import difflib
import re

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
        
class InSpace(Function):
    '''
    Looks up the current amount and names of people in space
    '''
    #Name for use in help listing
    mHelpName = "in space"
    #Names which can be used to address the function
    mNames = set(["in space","inspace","space"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the number of people in space right now, and their names. Format: in space"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        spaceDict = Commons.loadUrlJson("http://www.howmanypeopleareinspacerightnow.com/space.json")
        spaceNumber = str(spaceDict['number'])
        spaceNames = ", ".join(person['name'] for person in spaceDict['people'])
        outputString = "There are " + spaceNumber + " people in space right now. "
        outputString += "Their names are: " + spaceNames + "."

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set(Function.EVENT_MESSAGE)
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.lower()
        if("in space" in cleanFullLine and ("who" in cleanFullLine or "how many" in cleanFullLine)):
            return self.run(cleanFullLine,userObject,channelObject)

class TimestampToDate(Function):
    '''
    Converts an unix timestamp to a date
    '''
    #Name for use in help listing
    mHelpName = "date"
    #Names which can be used to address the function
    mNames = set(["timestamp to date","unix timestamp","unix","unix timestamp to date"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the date from a given unix timestamp. Format: date <timestamp>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        try:
            line = int(line)
        except:
            return "Invalid timestamp"
        return Commons.formatUnixTime(line) + "."

class Wiki(Function):
    '''
    Lookup wiki article and return the first paragraph or so.
    '''
    #Name for use in help listing
    mHelpName = "wiki"
    #Names which can be used to address the function
    mNames = set(["wiki","wikipedia"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Reads the first paragraph from a wikipedia article"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().replace(" ","_")
        url = 'http://en.wikipedia.org/w/api.php?format=json&action=query&titles='+lineClean+'&prop=revisions&rvprop=content&redirects=True'
        articleDict = Commons.loadUrlJson(url)
        pageCode = list(articleDict['query']['pages'])[0]
        articleText = articleDict['query']['pages'][pageCode]['revisions'][0]['*']
        oldScan = articleText
        newScan = re.sub('{{[^{^}]*}}','',oldScan)
        while(newScan!=oldScan):
            oldScan = newScan
            newScan = re.sub('{{[^{^}]*}}','',oldScan)
        plainText = newScan.replace('\'\'','')
        plainText = re.sub(r'<ref[^<]*</ref>','',plainText)
        plainText = re.sub(r'\[\[([^]]*)]]',r'\1',plainText)
        plainText = re.sub(r'\[\[[^]^|]*\|([^]]*)]]',r'\1',plainText)
        plainText = re.sub(r'<!--[^>]*-->','',plainText)
        plainText = re.sub(r'<ref[^>]*/>','',plainText)
        firstParagraph = plainText.strip().split('\n')[0]
        return firstParagraph