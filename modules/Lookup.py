from Function import Function
from inc.commons import Commons
from xml.dom import minidom
import difflib
import re
import urllib.parse
import struct       #UrlDetect image size
import imghdr       #UrlDetect image size
import math
import html.parser
import datetime

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
        randomCocktailXml = Commons.getRandomChoice(cocktailListXml.getElementsByTagName("cocktail"))
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
        spaceNames = ", ".join(person['name'].strip() for person in spaceDict['people'])
        outputString = "There are " + spaceNumber + " people in space right now. "
        outputString += "Their names are: " + spaceNames + "."
        return outputString

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set([Function.EVENT_MESSAGE])
    
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
        newScan = re.sub('{{[^{^}]*}}','',oldScan) #Strip templates
        while(newScan!=oldScan):
            oldScan = newScan
            newScan = re.sub('{{[^{^}]*}}','',oldScan) #Keep stripping templates until they're gone
        plainText = newScan.replace('\'\'','')
        plainText = re.sub(r'<ref[^<]*</ref>','',plainText) #Strip out references
        oldScan = plainText
        newScan = re.sub(r'(\[\[File:[^\][]+)\[\[[^\]]+]]',r'\1',oldScan) #Repeatedly strip links from image descriptions
        while(newScan!=oldScan):
            oldScan = newScan
            newScan = re.sub(r'(\[\[File:[^\][]+)\[\[[^\]]+]]',r'\1',oldScan)
        plainText = newScan
        plainText = re.sub(r'\[\[File:[^\]]+]]','',plainText) #Strip out images
        plainText = re.sub(r'\[\[[^\]^|]*\|([^\]]*)]]',r'\1',plainText) #Strip out links with specified names
        plainText = re.sub(r'\[\[([^\]]*)]]',r'\1',plainText) #Strip out links
        plainText = re.sub(r'<!--[^>]*-->','',plainText) #Strip out comments
        plainText = re.sub(r'<ref[^>]*/>','',plainText) #Strip out remaining references
        firstParagraph = plainText.strip().split('\n')[0]
        return firstParagraph
    
class Translate(Function):
    '''
    Uses google translate to translate a phrase to english, or to any specified language
    '''
    #Name for use in help listing
    mHelpName = "translate"
    #Names which can be used to address the function
    mNames = set(["translate"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Translates a given block of text. Format: translate <from>-><to> <text>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        if(len(line.split())<=1):
            langChange = ''
            transString = line
        else:
            langChange = line.split()[0]
            transString = ' '.join(line.split()[1:])
        if('->' not in langChange):
            langFrom = "auto"
            langTo = "en"
            transString = langChange+' '+transString
        else:
            langFrom = langChange.split('->')[0]
            langTo = langChange.split('->')[1]
        transSafe = urllib.parse.quote(transString.strip(),'')
        #This uses google's secret translate API, it's not meant to be used by robots, and often it won't work
        url = "http://translate.google.com/translate_a/t?client=t&text="+transSafe+"&hl=en&sl="+langFrom+"&tl="+langTo+"&ie=UTF-8&oe=UTF-8&multires=1&otf=1&pc=1&trs=1&ssel=3&tsel=6&sc=1"
        transDict = Commons.loadUrlJson(url,[],True)
        translationString = " ".join([x[0] for x in transDict[0]])
        return "Translation: "+translationString

class WeatherLocationRepo:
    '''
    Helper class to hold user's locations for weather-related functions.
    '''
    mListLocations = None
    
    def __init__(self):
        self.mListLocations = []
    
    def addEntry(self,newEntry):
        userName = newEntry.getUser()
        serverName = newEntry.getServer()
        testEntry = self.getEntryByUserNameAndServerName(userName,serverName)
        if(testEntry is None):
            self.mListLocations.append(newEntry)
        else:
            newList = [x if x != testEntry else newEntry for x in self.mListLocations]
            self.mListLocations = newList
    
    def getEntryByUserNameAndServerName(self,userName,serverName):
        'Returns an entry matching the given user name and server name, or None.'
        for locationEntry in self.mListLocations:
            if(locationEntry.getUser() != userName):
                continue
            if(locationEntry.getServer() != serverName):
                continue
            return locationEntry
        return None
        
    def getEntryByUserObject(self,userObject):
        'Returns an entry matching the given userObject, or None.'
        userName = userObject.getName()
        serverName = userObject.getServer().getName()
        return self.getEntryByUserNameAndServerName(userName,serverName)

    @staticmethod
    def loadFromXml():
        'Loads user locations from XML'
        newRepo = WeatherLocationRepo()
        try:
            doc = minidom.parse("store/weather_location_list.xml")
        except (IOError,OSError):
            return newRepo
        for weatherLocationXml in doc.getElementsByTagName("weather_location"):
            weatherLocation = WeatherLocationEntry.fromXml(weatherLocationXml.toxml())
            newRepo.addEntry(weatherLocation)
        return newRepo
    
    def saveToXml(self):
        'Saves user locations to XML'
        #Create document with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='weather_location_list',
            publicId='',
            systemId='weather_location_list.dtd'
        )
        doc = docimp.createDocument(None,'weather_location_list',doctype)
        #Get root element
        root = doc.getElementsByTagName("weather_location_list")[0]
        #Add entries
        for entryObject in self.mListLocations:
            entryElement = minidom.parseString(entryObject.toXml()).firstChild
            root.appendChild(entryElement)
        #Save XML
        doc.writexml(open("store/weather_location_list.xml","w"),addindent="\t",newl="\n")

class WeatherLocationEntry:
    '''
    Helper class that stores weather location data for a given user
    '''
    mServer = None
    mUser = None
    mCountryCode = None
    mType = None
    mCityName = None
    mZipCode = None
    mLatitude = None
    mLongitude = None
    
    TYPE_CITY = "city"
    TYPE_COORDS = "coords"
    TYPE_ZIP = "zip"

    def __init__(self,serverName,userName):
        self.mServer = serverName
        self.mUser = userName
    
    def getServer(self):
        'Returns server name'
        return self.mServer

    def getUser(self):
        'Returns user name'
        return self.mUser
    
    def getType(self):
        'Returns type'
        return self.mType
    
    def setCountryCode(self,newCountryCode):
        'Sets the country code of the location entry'
        self.mCountryCode = newCountryCode
    
    def setCity(self,newCity):
        'Sets the city of the location entry'
        self.mType = self.TYPE_CITY
        self.mCityName = newCity
    
    def setCoords(self,latitude,longitude):
        'Sets the coordinates of the location entry'
        self.mType = self.TYPE_COORDS
        self.mLatitude = latitude
        self.mLongitude = longitude
        
    def setZipCode(self,newZip):
        'Sets the zip code of the location entry'
        self.mType = self.TYPE_ZIP
        self.mZipCode = newZip
    
    def setFromInput(self,inputLine):
        #Check if zip code is given
        if(re.match(r'^\d{5}(?:[-\s]\d{4})?$',inputLine)):
            self.setZipCode(inputLine)
            return "Set location for "+self.mUser+" as zip code: "+inputLine
        #Check if coordinates are given
        coordMatch = re.match(r'^(\-?\d+(\.\d+)?)[ ,]*(\-?\d+(\.\d+)?)$',inputLine)
        if(coordMatch):
            newLat = coordMatch.group(1)
            newLong = coordMatch.group(3)
            self.setCoords(newLat,newLong)
            return "Set location for "+self.mUser+" as coords: "+newLat+", "+newLong
        #Otherwise, assume it's a city
        newCity = inputLine
        self.setCity(newCity)
        return "Set location for "+self.mUser+" as city: "+newCity
    
    def createQueryParams(self):
        'Creates query parameters for API call.'
        if(self.getType() == self.TYPE_CITY):
            query = "?q="+self.mCityName.replace(" ","+")
            if(self.mCountryCode is not None):
                query += ","+self.mCountryCode
            return query
        if(self.getType() == self.TYPE_COORDS):
            query = "?lat="+self.mLatitude+"&lon="+self.mLongitude
            return query
        if(self.getType() == self.TYPE_ZIP):
            query = "?zip="+self.mZipCode
            if(self.mCountryCode is not None):
                query += ","+self.mCountryCode
            return query
    
    @staticmethod
    def fromXml(xmlString):
        #Load document
        doc = minidom.parseString(xmlString)
        #Get server and username and create entry
        newServer = doc.getElementsByTagName("server")[0].firstChild.data
        newUser = doc.getElementsByTagName("user")[0].firstChild.data
        newEntry = WeatherLocationEntry(newServer,newUser)
        #Get country code, if applicable
        if(len(doc.getElementsByTagName("country_code"))>0):
            newCountryCode = doc.getElementsByTagName("country_code")[0].firstChild.data
            newEntry.setCountryCode(newCountryCode)
        #Check if entry is a city name
        if(len(doc.getElementsByTagName("city_name"))>0):
            newCity = doc.getElementsByTagName("city_name")[0].firstChild.data
            newEntry.setCity(newCity)
        #Check if entry is coordinates
        if(len(doc.getElementsByTagName("coords"))>0):
            newLat = doc.getElementsByTagName("latitude")[0].firstChild.data
            newLong = doc.getElementsByTagName("longitude")[0].firstChild.data
            newEntry.setCoords(newLat,newLong)
        #Check if entry is zip code
        if(len(doc.getElementsByTagName("zip_code"))>0):
            newZip = doc.getElementsByTagName("zip_code")[0].firstChild.data
            newEntry.setZipCode(newZip)
        #Return entry
        return newEntry

    def toXml(self):
        'Writes out Entry as XML'
        #Create document
        doc = minidom.Document()
        #Create root element
        root = doc.createElement("weather_location")
        doc.appendChild(root)
        #Add server element
        serverElement = doc.createElement("server")
        serverElement.appendChild(doc.createTextNode(self.mServer))
        root.appendChild(serverElement)
        #Add user element
        userElement = doc.createElement("user")
        userElement.appendChild(doc.createTextNode(self.mUser))
        root.appendChild(userElement)
        #Add country code, if set
        if(self.mCountryCode is not None):
            countryCodeElement = doc.createElement("country_code")
            countryCodeElement.appendChild(doc.createTextNode(self.mCountryCode))
            root.appendChild(countryCodeElement)
        #Depending on type, add relevant elements
        if(self.mType == self.TYPE_CITY):
            cityElement = doc.createElement("city_name")
            cityElement.appendChild(doc.createTextNode(self.mCityName))
            root.appendChild(cityElement)
        elif(self.mType == self.TYPE_COORDS):
            coordsElement = doc.createElement("coords")
            latElement = doc.createElement("latitude")
            latElement.appendChild(doc.createTextNode(self.mLatitude))
            coordsElement.appendChild(latElement)
            longElement = doc.createElement("longitude")
            longElement.appendChild(doc.createTextNode(self.mLongitude))
            coordsElement.appendChild(longElement)
            root.appendChild(coordsElement)
        elif(self.mType == self.TYPE_ZIP):
            zipElement = doc.createElement("zip_code")
            zipElement.appendChild(doc.createTextNode(self.mZipCode))
            root.appendChild(zipElement)
        #Output XML
        return doc.toxml()

class WeatherLocation(Function):
    '''
    Sets the location of user for Weather functions.
    '''
    #Name for use in help listing
    mHelpName = "weather location"
    #Names which can be used to address the function
    mNames = set(["weather location","weather location set","set weather location","weather set location"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets a user's location for weather-related functions"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        #Load up Weather locations repo
        weatherRepo = WeatherLocationRepo.loadFromXml()
        userName = userObject.getName()
        serverObj = userObject.getServer()
        serverName = serverObj.getName()
        #Check that an argument is provided
        if(len(lineClean.split())==0):
            return "Please specify a city, coordinates or zip code"
        #Check if first argument is a specified user for given server
        firstArg = lineClean.split()[0]
        testUser = serverObj.getUserByName(firstArg)
        if(destinationObject is not None and destinationObject.isChannel()):
            if(destinationObject.isUserInChannel(testUser)):
                userName = testUser.getName()
                lineClean = lineClean[len(firstArg):].strip()
        #Create entry
        newEntry = WeatherLocationEntry(serverName,userName)
        #Set Entry location by input
        output = newEntry.setFromInput(lineClean)
        weatherRepo.addEntry(newEntry)
        weatherRepo.saveToXml()
        return output

class CurrentWeather(Function):
    '''
    Returns the current weather in your location, or asks for your location.
    '''
    #Name for use in help listing
    mHelpName = "current weather"
    #Names which can be used to address the function
    mNames = set(["current weather","weather current","current weather in"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the current weather in your location (if known) or in provided location."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        if(lineClean == ""):
            locationRepo = WeatherLocationRepo.loadFromXml()
            locationEntry = locationRepo.getEntryByUserObject(userObject)
            if(locationEntry is None):
                return "No location stored for this user. Please specify a location or store one with the \"weather location\" function."
        else:
            #Check if a user was specified
            testUser = userObject.getServer().getUserByName(lineClean)
            if(destinationObject is not None and destinationObject.isChannel() and destinationObject.isUserInChannel(testUser)):
                locationRepo = WeatherLocationRepo.loadFromXml()
                locationEntry = locationRepo.getEntryByUserObject(testUser)
                if(locationEntry is None):
                    return "No location stored for this user. Please specify a location or store one with the \"weather location\" function."
            else:
                userName = userObject.getName()
                serverName = userObject.getServer().getName()
                locationEntry = WeatherLocationEntry(userName,serverName)
                locationEntry.setFromInput(lineClean)
        apiKey = userObject.getServer().getHallo().getApiKey("openweathermap")
        if(apiKey is None):
            return "No API key loaded for openweathermap."
        url = "http://api.openweathermap.org/data/2.5/weather"+locationEntry.createQueryParams()+"&APPID="+apiKey
        response = Commons.loadUrlJson(url)
        if(str(response['cod']) != "200"):
            return "Location not recognised."
        cityName = response['name']
        weatherMain = response['weather'][0]['main']
        weatherDesc = response['weather'][0]['description']
        weatherTemp = response['main']['temp']-273.15
        weatherHumidity = response['main']['humidity']
        weatherWindSpeed = response['wind']['speed']
        output = "Current weather in "+cityName+" is "+weatherMain+" ("+weatherDesc+"). "
        output += "Temp: "+"{0:.2f}".format(weatherTemp)+"C, "
        output += "Humidity: "+str(weatherHumidity)+"%, "
        output += "Wind speed: "+str(weatherWindSpeed)+"m/s"
        return output
    
class Weather(Function):
    '''
    Currently returns a random weather phrase. In future perhaps nightvale weather?
    '''
    #Name for use in help listing
    mHelpName = "weather"
    #Names which can be used to address the function
    mNames = set(["weather","weather in"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Random weather"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        regexFluff = re.compile(r'\b(for|[io]n)\b')
        #Clear input fluff
        lineClean = regexFluff.sub("",lineClean).strip()
        #Hunt for the days offset
        daysOffset = 0
        regexNow = re.compile(r'(now|current(ly)?|today)')
        regexTomorrow = re.compile(r'(to|the\s+)morrow')
        regexWeekday = re.compile(r'\b(this\s+|next\s+|)(mo(n(day)?)?|tu(e(s(day)?)?)?|we(d(nesday)?)?|th(u(r(sday)?)?)?|fr(i(day)?)?|sa(t(urday)?)?|su(n(day)?)?)\b')
        regexDays = re.compile(r'(([0-9]+)\s*d(ays?)?)')
        regexWeeks = re.compile(r'(([0-9]+)\s*w(eeks?)?)')
        if(regexNow.search(lineClean)):
            daysOffset = 0
            lineClean = regexNow.sub("",lineClean).strip()
        elif(regexTomorrow.search(lineClean)):
            daysOffset = 1
            lineClean = regexTomorrow.sub("",lineClean).strip()
        elif(regexWeekday.search(lineClean)):
            match = regexWeekday.search(lineClean)
            currentWeekday = datetime.date.today().weekday()
            specifiedWeekday = self.weekdayToNumber(match.group(2))
            daysOffset = (specifiedWeekday-currentWeekday)%7
            lineClean = regexWeekday.sub("",lineClean).strip()
        elif(regexDays.search(lineClean)):
            match = regexDays.search(lineClean)
            daysOffset = int(match.group(2))
            lineClean = regexDays.sub("",lineClean).strip()
        elif(regexWeeks.search(lineClean)):
            match = regexWeeks.search(lineClean)
            daysOffset = 7*int(match.group(2))
            lineClean = regexWeeks.sub("",lineClean).strip()
        #Figure out if a user or city was specified
        if(lineClean == ""):
            weatherRepo = WeatherLocationRepo.loadFromXml()
            locationEntry = weatherRepo.getEntryByUserObject(userObject)
            if(locationEntry == None):
                return "No location stored for this user. Please specify a location or store one with the \"weather location\" function."
        else:
            testUser = userObject.getServer().getUserByName(lineClean)
            if(destinationObject is not None and destinationObject.isChannel() and destinationObject.isUserInChannel(testUser)):
                weatherRepo = WeatherLocationRepo.loadFromXml()
                locationEntry = weatherRepo.getEntryByUserObject(testUser)
                if(locationEntry == None):
                    return "No location stored for this user. Please specify a location or store one with the \"weather location\" function."
            else:
                userName = userObject.getName()
                serverName = userObject.getServer().getName()
                locationEntry = WeatherLocationEntry(userName,serverName)
                locationEntry.setFromInput(lineClean)
        #Get API response
        apiKey = userObject.getServer().getHallo().getApiKey("openweathermap")
        if(apiKey is None):
            return "No API key loaded for openweathermap."
        url = "http://api.openweathermap.org/data/2.5/forecast/daily"+locationEntry.createQueryParams()+"&cnt=16&APPID="+apiKey
        response = Commons.loadUrlJson(url)
        #Check API responded well
        if(str(response['cod']) != "200"):
            return "Location not recognised."
        #Check that days is within bounds for API response
        daysAvailable = len(response['list'])
        if(daysOffset>daysAvailable):
            return "I cannot predict the weather that far in the future. I can't predict much further than 2 weeks."
        #Format and return output
        cityName = response['city']['name']
        if(daysOffset == 0):
            todayMain = response['list'][0]['weather'][0]['main']
            todayDesc = response['list'][0]['weather'][0]['description']
            todayTemp = response['list'][0]['temp']['day']-273.15
            todayHumi = response['list'][0]['humidity']
            todaySpee = response['list'][0]['speed']
            tomorMain = response['list'][1]['weather'][0]['main']
            tomorDesc = response['list'][1]['weather'][0]['description']
            tomorTemp = response['list'][1]['temp']['day']-273.15
            tomorHumi = response['list'][1]['humidity']
            tomorSpee = response['list'][1]['speed']
            dayafMain = response['list'][2]['weather'][0]['main']
            dayafDesc = response['list'][2]['weather'][0]['description']
            dayafTemp = response['list'][2]['temp']['day']-273.15
            dayafHumi = response['list'][2]['humidity']
            dayafSpee = response['list'][2]['speed']
            output = "Weather in "+cityName+" today will be "+todayMain+" ("+todayDesc+") "
            output += "Temp: "+"{0:.2f}".format(todayTemp)+"C, "
            output += "Humidity: "+str(todayHumi)+"%, "
            output += "Wind speed: "+str(todaySpee)+"m/s. "
            #Add tomorrow output
            output += "Tomorrow: "+tomorMain+" ("+tomorDesc+") "
            output += "{0:.2f}".format(tomorTemp)+"C "
            output += str(tomorHumi)+"% "
            output += str(tomorSpee)+"m/s. "
            #Day after output
            output += "Day after: "+dayafMain+" ("+dayafDesc+") "
            output += "{0:.2f}".format(dayafTemp)+"C "
            output += str(dayafHumi)+"% "
            output += str(dayafSpee)+"m/s."
            return output
        responseWeather = response['list'][daysOffset]
        weatherMain = responseWeather['weather'][0]['main']
        weatherDesc = responseWeather['weather'][0]['description']
        weatherTemp = responseWeather['temp']['day']-273.15
        weatherHumidity = responseWeather['humidity']
        weatherWindSpeed = responseWeather['speed']
        output = "Weather in "+cityName+" "+self.numberDays(daysOffset)+" will be "+weatherMain+" ("+weatherDesc+"). "
        output += "Temp: "+"{0:.2f}".format(weatherTemp)+"C, "
        output += "Humidity: "+str(weatherHumidity)+"%, "
        output += "Wind speed: "+str(weatherWindSpeed)+"m/s"
        return output

    def weekdayToNumber(self,weekday):
        'Converts weekday text to integer. Monday = 0'
        weekdayClean = weekday.lower().strip()
        weekdayRegexList = [re.compile(r'mo(n(day)?)?'),
                            re.compile(r'tu(e(s(day)?)?)?'),
                            re.compile(r'we(d(nesday)?)?'),
                            re.compile(r'th(u(r(sday)?)?)?'),
                            re.compile(r'fr(i(day)?)?'),
                            re.compile(r'sa(t(urday)?)?'),
                            re.compile(r'su(n(day)?)?')]
        for weekdayInt in range(len(weekdayRegexList)):
            weekdayRegex = weekdayRegexList[weekdayInt]
            if(weekdayRegex.match(weekdayClean)):
                return weekdayInt
        return None
    
    def numberDays(self,daysOffset):
        if(daysOffset == 0):
            return "today"
        if(daysOffset == 1):
            return "tomorrow"
        return "in "+str(daysOffset)+" days"

class UrlDetect(Function):
    '''
    URL detection and title printing.
    '''
    #Name for use in help listing
    mHelpName = "urldetect"
    #Names which can be used to address the function
    mNames = set(["urldetect"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "URL detection."
    
    mHalloObject = None
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        return "This function does not take input."

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set([Function.EVENT_MESSAGE])

    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        #Get hallo object for stuff to use
        self.mHalloObject = serverObject.getHallo()
        #Search for a link
        urlRegex = re.compile(r'\b((https?://|www.)[-A-Z0-9+&?%@#/=~_|$:,.]*[A-Z0-9+\&@#/%=~_|$])',re.I)
        urlSearch = urlRegex.search(fullLine)
        if(not urlSearch):
            return None
        #Get link address
        urlAddress = urlSearch.group(1)
        #Add protocol if missing
        if("://" not in urlAddress):
            urlAddress = "http://" + urlAddress
        #Ignore local links.
        if('127.0.0.1' in urlAddress or '192.168.' in urlAddress or '10.' in urlAddress or '172.' in urlAddress):
            return None
        #Get page info
        pageRequest = urllib.request.Request(urlAddress)
        pageRequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageOpener = urllib.request.build_opener()
        pageInfo = str(pageOpener.open(pageRequest).info())
        if("Content-Type:" in pageInfo):
            pageType = pageInfo.split()[pageInfo.split().index('Content-Type:')+1]
        else:
            pageType = ''
        #Get the website name
        urlSite = Commons.getDomainName(urlAddress).lower()
        #Get response if link is an image
        if("image" in pageType):
            return self.urlImage(urlAddress,pageOpener,pageRequest,pageType)
        #Get a response depending on the website
        if(urlSite=="amazon"):
            return self.siteAmazon(urlAddress,pageOpener,pageRequest)
        if(urlSite=="e621"):
            return self.siteE621(urlAddress,pageOpener,pageRequest)
        if(urlSite=="ebay"):
            return self.siteEbay(urlAddress,pageOpener,pageRequest)
        if(urlSite=="f-list"):
            return self.siteFList(urlAddress,pageOpener,pageRequest)
        if(urlSite=="furaffinity" or urlSite=="facdn"):
            return self.siteFuraffinity(urlAddress,pageOpener,pageRequest)
        if(urlSite=="imdb"):
            return self.siteImdb(urlAddress,pageOpener,pageRequest)
        if(urlSite=="imgur"):
            return self.siteImgur(urlAddress,pageOpener,pageRequest)
        if(urlSite=="speedtest"):
            return self.siteSpeedtest(urlAddress,pageOpener,pageRequest)
        if(urlSite=="reddit" or urlSite=="redd"):
            return self.siteReddit(urlAddress,pageOpener,pageRequest)
        if(urlSite=="wikipedia"):
            return self.siteWikipedia(urlAddress,pageOpener,pageRequest)
        if(urlSite=="youtube" or urlSite=="youtu"):
            return self.siteYoutube(urlAddress,pageOpener,pageRequest)
        #If other url, return generic URL response
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def urlImage(self,urlAddress,pageOpener,pageRequest,pageType):
        'Handling direct image links'
        #Get the website name
        urlSite = Commons.getDomainName(urlAddress).lower()
        #If website name is speedtest or imgur, hand over to those handlers
        if(urlSite=="speedtest"):
            return self.siteSpeedtest(urlAddress,pageOpener,pageType)
        if(urlSite=="imgur"):
            return self.siteImgur(urlAddress,pageOpener,pageType)
        #Image handling
        imageData = pageOpener.open(pageRequest).read()
        imageWidth, imageHeight = self.getImageSize(imageData)
        imageSize = len(imageData)
        imageSizeStr = self.fileSizeToString(imageSize)
        return "Image: " + pageType + " (" + str(imageWidth) + "px by " + str(imageHeight) + "px) " + imageSizeStr + "."

    def urlGeneric(self,urlAddress,pageOpener,pageRequest):
        'Handling for generic links not caught by any other url handling function.'
        pageCode = pageOpener.open(pageRequest).read(4096).decode('utf-8','ignore')
        if(pageCode.count('</title>')==0):
            return None
        titleSearch = re.search('<title[^>]*>([^<]*)</title>',pageCode,re.I)
        if(titleSearch is None):
            return None
        titleText = titleSearch.group(1)
        htmlParser = html.parser.HTMLParser()
        titleClean = htmlParser.unescape(titleText).replace("\n","").strip()
        if(titleClean!=""):
            return "URL title: " + titleClean.replace("\n","")
        return None

    def siteAmazon(self,urlAddress,pageOpener,pageRequest):
        'Handling for amazon links'
        #I spent ages trying to figure out the amazon API, and I gave up.
        #TODO: write amazon link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteE621(self,urlAddress,pageOpener,pageRequest):
        'Handling for e621 links'
        #TODO: write e621 link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteEbay(self,urlAddress,pageOpener,pageRequest):
        'Handling for ebay links'
        #Get the ebay item id
        itemId = urlAddress.split("/")[-1]
        apiKey = self.mHalloObject.getApiKey("ebay")
        if(apiKey is None):
            return None
        #Get API response
        apiUrl = "http://open.api.ebay.com/shopping?callname=GetSingleItem&responseencoding=JSON&appid="+apiKey+"&siteid=0&version=515&ItemID="+itemId+"&IncludeSelector=Details"
        apiDict = Commons.loadUrlJson(apiUrl)
        #Get item data from api response
        itemTitle = apiDict["Item"]["Title"]
        itemPrice = str(apiDict["Item"]["CurrentPrice"]["Value"])+" "+apiDict["Item"]["CurrentPrice"]["CurrencyID"]
        itemEndTime = apiDict["Item"]["EndTime"][:19].replace("T"," ")
        #Start building output
        output = "eBay> Title: " + itemTitle + " | "
        output += "Price: " + itemPrice + " | "
        #Check listing type
        if(apiDict["Item"]["ListingType"]=="Chinese"):
            #Listing type: bidding
            itemBidCount = str(apiDict["Item"]["BidCount"])
            if(itemBidCount=="1"):
                output += "Auction, " + str(itemBidCount) + " bid"
            else:
                output += "Auction, " + str(itemBidCount) + " bids"
        elif(apiDict["Item"]["ListingType"]=="FixedPriceItem"):
            #Listing type: buy it now
            output += "Buy it now | "
        output += "Ends: " + itemEndTime
        return output

    def siteFList(self,urlAddress,pageOpener,pageRequest):
        'Handling for f-list links'
        #TODO: write f-list link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteFuraffinity(self,urlAddress,pageOpener,pageRequest):
        'Handling for furaffinity links'
        #TODO: write furaffinity link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteImdb(self,urlAddress,pageOpener,pageRequest):
        'Handling for imdb links'
        #If URL isn't to an imdb title, just do normal url handling.
        if('imdb.com/title' not in urlAddress):
            return self.siteGeneric(urlAddress,pageOpener,pageRequest)
        #Get the imdb movie ID
        movieIdSearch = re.search('title/(tt[0-9]*)',urlAddress)
        if(movieIdSearch is None):
            return self.siteGeneric(urlAddress,pageOpener,pageRequest)
        movieId = movieIdSearch.group(1)
        #Download API response
        apiUrl = 'http://www.omdbapi.com/?i=' + movieId
        apiDict = Commons.loadUrlJson(apiUrl)
        #Get movie information from API response
        movieTitle = apiDict['Title']
        movieYear = apiDict['Year']
        movieGenre = apiDict['Genre']
        movieRating = apiDict['imdbRating']
        movieVotes = apiDict['imdbVotes']
        #Construct output
        output = "IMDB> Title: " +movieTitle + " (" + movieYear + ") | "
        output += "Rating "+movieRating+"/10, "+movieVotes+" votes. | "
        output += "Genres: " + movieGenre  + "."
        return output

    def siteImgur(self,urlAddress,pageOpener,pageRequest):
        'Handling imgur links'
        #Hand off imgur album links to a different handler function.
        if("/a/" in urlAddress):
            return self.siteImgurAlbum(urlAddress,pageOpener,pageRequest)
        #Handle individual imgur image links
        #Example imgur links: http://i.imgur.com/2XBqIIT.jpg http://imgur.com/2XBqIIT
        imgurId = urlAddress.split('/')[-1].split('.')[0]
        apiUrl = 'https://api.imgur.com/3/image/' + imgurId
        #Load API response (in json) using Client-ID.
        apiKey = self.mHalloObject.getApiKey("imgur")
        if(apiKey is None):
            return None
        apiDict = Commons.loadUrlJson(apiUrl,[['Authorization',apiKey]])
        #Get title, width, height, size, and view count from API data
        imageTitle = str(apiDict['data']['title'])
        imageWidth = str(apiDict['data']['width'])
        imageHeight = str(apiDict['data']['height'])
        imageSize = int(apiDict['data']['size'])
        imageSizeString = self.fileSizeToString(imageSize)
        imageViews = apiDict['data']['views']
        #Create output and return
        output = "Imgur> Title: " + imageTitle + " | "
        output += "Size: " + imageWidth + "x" + imageHeight + " | "
        output += "Filesize: " + imageSizeString + " | "
        output += "Views: " + "{:,}".format(imageViews) + "."
        return output

    def siteImgurAlbum(self,urlAddress,pageOpener,pageRequest):
        'Handling imgur albums'
        #http://imgur.com/a/qJctj#0 example imgur album
        imgurId = urlAddress.split('/')[-1].split('#')[0]
        apiUrl = 'https://api.imgur.com/3/album/' + imgurId
        #Load API response (in json) using Client-ID.
        apiKey = self.mHalloObject.getApiKey("imgur")
        if(apiKey is None):
            return None
        apiDict = Commons.loadUrlJson(apiUrl,[['Authorization',apiKey]])
        #Get album title and view count from API data
        albumTitle = apiDict['data']['title']
        albumViews = apiDict['data']['views']
        #Start on output
        output = "Imgur album> "
        output += "Album title: " + albumTitle + " | " 
        output += "Gallery views: " + "{:,}".format(albumViews) + " | "
        if('section' in apiDict['data']):
            albumSection = apiDict['data']['section']
            output += "Section: " + albumSection + " | "
        albumCount = apiDict['data']['images_count']
        #If an image was specified, show some information about that specific image
        if("#" in urlAddress):
            imageNumber = int(urlAddress.split('#')[-1])
            imageWidth = apiDict['data']['images'][imageNumber]['width']
            imageHeight = apiDict['data']['images'][imageNumber]['height']
            imageSize = int(apiDict['data']['images'][imageNumber]['size'])
            imageSizeString = self.fileSizeToString(imageSize)
            output += "Image " + str(imageNumber+1) + " of " + str(albumCount) + " | "
            output += "Current image: " + str(imageWidth) + "x" + str(imageHeight) + ", " + imageSizeString + "."
            return output
        output += str(albumCount) + "images."
        return output
    
    def sitePastebin(self,urlAddress,pageOpener,pageRequest):
        'Handling pastebin links'
        #TODO: write pastebin link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)
    
    def siteReddit(self,urlAddress,pageOpener,pageRequest):
        'Handling reddit links'
        #TODO: write reddit link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteSpeedtest(self,urlAddress,pageOpener,pageRequest):
        'Handling speedtest links'
        if(urlAddress[-4:]=='.png'):
            urlNumber = urlAddress[32:-4]
            urlAddress = 'http://www.speedtest.net/my-result/' + urlNumber
            pageRequest = urllib.request.Request(urlAddress)
            pageRequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
            pageOpener = urllib.request.build_opener()
        pageCode = pageOpener.open(pageRequest).read().decode('utf-8')
        pageCode = re.sub(r'\s+','',pageCode)
        download = re.search('<h3>Download</h3><p>([0-9\.]*)',pageCode).group(1)
        upload = re.search('<h3>Upload</h3><p>([0-9\.]*)',pageCode).group(1)
        ping = re.search('<h3>Ping</h3><p>([0-9]*)',pageCode).group(1)
        return "Speedtest> Download: " + download + "Mb/s | Upload: " + upload + "Mb/s | Ping: " + ping + "ms"

    def siteWikipedia(self,urlAddress,pageOpener,pageRequest):
        'Handling for wikipedia links'
        #TODO: write wikipedia link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteYoutube(self,urlAddress,pageOpener,pageRequest):
        'Handling for youtube links'
        #Find video id
        if("youtu.be" in urlAddress):
            videoId = urlAddress.split("/")[-1].split("?")[0]
        else:
            videoId = urlAddress.split("/")[-1].split("=")[1].split("&")[0]
        #Find API url
        apiKey = self.mHalloObject.getApiKey("youtube")
        if(apiKey is None):
            return None
        apiUrl = "https://www.googleapis.com/youtube/v3/videos?id="+videoId+"&part=snippet,contentDetails,statistics&key="+apiKey
        #Load API response (in json).
        apiDict = Commons.loadUrlJson(apiUrl)
        #Get video data from API response.
        videoTitle = apiDict['items'][0]['snippet']['title']
        videoDuration = apiDict['items'][0]['contentDetails']['duration'][2:].lower()
        videoViews = apiDict['items'][0]['statistics']['viewCount']
        #Create output
        output = "Youtube video> Title: " + videoTitle + " | "
        output += "Length: " + videoDuration + " | "
        output += "Views: " + videoViews + "."
        return output





    def getImageSize(self,imageData):
        '''Determine the image type of fhandle and return its size.
        from draco'''
        #This function is from here: http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
        imageHead = imageData[:24]
        if len(imageHead) != 24:
            return
        if imghdr.what(None,imageData) == 'png':
            check = struct.unpack('>i', imageHead[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', imageHead[16:24])
        elif imghdr.what(None,imageData) == 'gif':
            width, height = struct.unpack('<HH', imageHead[6:10])
        elif imghdr.what(None,imageData) == 'jpeg':
            try:
                byteOffset = 0
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    byteOffset += size
                    byte = imageData[byteOffset]
                    byteOffset += 1
                    while byte == 0xff:
                        byte = imageData[byteOffset]
                        byteOffset += 1
                    ftype = byte
                    size = struct.unpack('>H', imageData[byteOffset:byteOffset+2])[0] - 2
                    byteOffset += 2
                # We are at a SOFn block
                byteOffset += 1  # Skip `precision' byte.
                height, width = struct.unpack('>HH', imageData[byteOffset:byteOffset+4])
                byteOffset += 4
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height

    def fileSizeToString(self,size):
        if(size<2048):
            sizeString = str(size) + "Bytes"
        elif(size<(2048*1024)):
            sizeString = str(math.floor(float(size)/10.24)/100) + "KiB"
        elif(size<(2048*1024*1024)):
            sizeString = str(math.floor(float(size)/(1024*10.24))/100) + "MiB"
        else:
            sizeString = str(math.floor(float(size)/(1024*1024*10.24))/100) + "GiB"
        return sizeString

