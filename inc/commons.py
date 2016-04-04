import time
import datetime
import urllib.request
import re
import json
import random
from datetime import timedelta


class ISO8601ParseError(SyntaxError):
    """
    ISO-8601 parsing error
    """
    pass


class Commons(object):
    """
    Class of commons methods, useful anywhere, but all static.
    """
    mEndLine = '\r\n'
    BOOL_STRING_DICT = {True: "True", False: "False", None: "None"}
    ALL_CHANNELS = "all_channels"
    ALL_SERVERS = "all_servers"

    @staticmethod
    def currentTimestamp():
        """
        Constructor
        """
        return "[{:02d}:{:02d}:{:02d}]".format(*time.gmtime()[3:6])

    @staticmethod
    def chunkString(string, length):
        return (string[0 + i:length + i] for i in range(0, len(string), length))

    @staticmethod
    def chunkStringDot(string, length):
        if len(string) < length:
            return [string]
        else:
            listOfStrings = [string[:length - 3] + '...']
            restOfString = string[length - 3:]
            while len(restOfString) > length - 3:
                listOfStrings += ['...' + restOfString[:length - 6] + '...']
                restOfString = restOfString[length - 6:]
            listOfStrings += ['...' + restOfString]
            return listOfStrings

    @staticmethod
    def readFiletoList(filename):
        f = open(filename, "r")
        fileList = []
        rawLine = f.readline()
        while rawLine != '':
            fileList.append(rawLine.replace("\n", ''))
            rawLine = f.readline()
        return fileList

    @staticmethod
    def getDomainName(url):
        """
        Gets the domain name of a URL, removing the TLD
        :param url: URL to find domain of
        """
        # Sanitise the URL, removing protocol and directories
        url = url.split("://")[-1]
        url = url.split("/")[0]
        url = url.split(":")[0]
        # Get the list of TLDs, from mozilla's http://publicsuffix.org
        tldList = [x.strip() for x in open("store/tld_list.txt", "rb").read().decode("utf-8").split("\n")]
        urlSplit = url.split(".")
        urlTld = None
        for tldTest in ['.'.join(urlSplit[x:]) for x in range(len(urlSplit))]:
            if tldTest in tldList:
                urlTld = tldTest
                break
        # If you didn't find the TLD, just return the longest bit.
        if urlTld is None:
            return urlSplit.sort(key=len)[-1]
        # Else return the last part before the TLD
        return url[:-len(urlTld) - 1].split('.')[-1]

    @staticmethod
    def stringToBool(string):
        """
        Converts a string to a boolean.
        :param string: String to convert to boolean
        """
        string = string.lower()
        if string in [1, '1', 'true', 't', 'yes', 'y', 'on', 'enabled', 'enable']:
            return True
        if string in [0, '0', 'false', 'f', 'no', 'n', 'off', 'disabled', 'disable']:
            return False
        return None

    @staticmethod
    def isStringNull(string):
        """
        Checks if a string could mean null.
        :param string: String to check for meaning null
        """
        string = string.lower()
        if string in [0, '0', 'false', 'off', 'disabled', 'disable', '', 'nul', 'null', 'none', 'nil']:
            return True
        return False

    @staticmethod
    def stringFromFile(string):
        """
        Loads a string from a file. Converting booleans or null values accordingly.
        :param string: String to load as true, false, null or original string
        """
        inputBool = Commons.stringToBool(string)
        if inputBool in [True, False]:
            return inputBool
        if Commons.isStringNull(string):
            return None
        return string

    @staticmethod
    def ordinal(number):
        """
        Returns the ordinal of a number
        :param number: Number to get ordinal string for
        """
        if number % 10 == 1 and number % 100 != 11:
            return str(number) + "st"
        elif number % 10 == 2 and number % 100 != 12:
            return str(number) + "nd"
        elif number % 10 == 3 and number % 100 != 13:
            return str(number) + "rd"
        else:
            return str(number) + "th"

    @staticmethod
    def formatUnixTime(timeStamp):
        """
        Returns a string, formatted datetime from a timestamp
        :param timeStamp: unix timestamp
        """
        return str(datetime.datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S'))

    @staticmethod
    def loadUrlString(url, headers=None):
        """
        Takes a url to an xml resource, pulls it and returns a dictionary.
        :param url: URL to download
        :param headers: List of HTTP headers to add to request
        """
        if headers is None:
            headers = []
        pageRequest = urllib.request.Request(url)
        pageRequest.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        for header in headers:
            pageRequest.add_header(header[0], header[1])
        pageOpener = urllib.request.build_opener()
        code = pageOpener.open(pageRequest).read().decode('utf-8')
        return code

    @staticmethod
    def loadUrlJson(url, headers=None, jsonFix=False):
        """Takes a url to a json resource, pulls it and returns a dictionary.
        :param url: URL of json to download
        :param headers: List of HTTP headers to add to request
        :param jsonFix: Whether to "fix" the JSON being returned for parse errors
        """
        if headers is None:
            headers = []
        code = Commons.loadUrlString(url, headers)
        if jsonFix:
            code = re.sub(',+', ',', code)
            code = code.replace('[,', '[').replace(',]', ']')
        outputDict = json.loads(code)
        return outputDict

    @staticmethod
    def checkNumbers(message):
        """
        Checks that an argument is purely numbers
        :param message: String to check for pure number-ness
        """
        message = message.lower()
        if message.count(".") > 1:
            return False
        if message.replace(".", "").isdigit():
            return True
        return False

    @staticmethod
    def checkCalculation(message):
        """
        Checks that an argument is purely numbers and calculation characters
        :param message: String to be checked to see if it's a calculation
        """
        message = message.strip().lower()
        validChars = [str(x) for x in range(10)]
        validChars += [".", ")", "^", "*", "x", "/", "%", "+", "-", "pi", "e", " "]
        validChars += ["acos(", "asin(", "atan(", "cos(", "sin(", "tan(", "sqrt(", "log("]
        validChars += ["acosh(", "asinh(", "atanh(", "cosh(", "sinh(", "tanh(", "gamma(", "("]
        for char in validChars:
            message = message.replace(char, "")
        if message == "":
            return True
        else:
            return False

    @staticmethod
    def isFloatString(floatString):
        """
        Checks whether a string is a valid float
        :param floatString: String to check for validity in float conversion
        """
        try:
            float(floatString)
            return True
        except ValueError:
            return False

    @staticmethod
    def getDigitsFromStartOrEnd(string):
        """
        Gets the longest string of digits from the start of a string, or None
        :param string: String to find sequence of digits from
        """
        return ([string[:x] for x in range(1, len(string)+1) if Commons.isFloatString(string[:x])][::-1]+[string[x:] for x in range(len(string))if Commons.isFloatString(string[x:])]+[None])[0]

    @staticmethod
    def listGreater(listOne, listTwo):
        """
        Checks whether listOne is "greater" than listTwo.
        Checks if an earlier element of listOne is greater than the equally placed element in listTwo
        :param listOne: List of elements, for checking against listTwo
        :param listTwo: List of elements, to check against listOne
        """
        if len(listOne) != len(listTwo):
            return Exception("Lists must be the same length.")
        for index in range(len(listOne)):
            if listOne[index] == listTwo[index]:
                continue
            if listOne[index] > listTwo[index]:
                return True
            return False
        return None

    @staticmethod
    def getRandomInt(minInt, maxInt, count=1):
        """Returns a list of random integers in a given range
        :param minInt: Minimum integer to return
        :param maxInt: Maximum integer to return
        :param count: Number of random integers to return
        """
        # Try and get random numbers from random.org
        if minInt == maxInt:
            return [minInt]
        randomOrgUrl = "https://www.random.org/integers/?num=" + str(count) + "&format=plain&min=" + \
                       str(minInt) + "&max=" + str(maxInt) + "&col=1&base=10"
        userAgentHeaders = [["User-Agent", "Hallo IRCBot hallo@dr-spangle.com"]]
        apiResponse = Commons.loadUrlString(randomOrgUrl, userAgentHeaders)
        if "Error:" not in apiResponse:
            return [int(x) for x in apiResponse.split("\n") if x != ""]
        # Otherwise, use random module
        outputList = []
        for _ in range(count):
            outputList.append(random.randint(minInt, maxInt))
        return outputList

    @staticmethod
    def getRandomChoice(choiceList, count=1):
        # Replacement for random.choice, using random.org API
        randInt = Commons.getRandomInt(0, len(choiceList) - 1, count)
        outputList = []
        for x in range(count):
            outputList.append(choiceList[randInt[x]])
        return outputList

    @staticmethod
    def loadTimeDelta(deltaString):
        """
        Loads a timedelta object from an ISO8601 period string
        :param deltaString: string
        :return: timedelta
        """
        if deltaString[0] != "P" or deltaString[-1] != "S":
            raise ISO8601ParseError("Invalid ISO-8601 period string")
        cleanString = deltaString[1:-1]
        splitString = cleanString.split("T")
        if len(splitString) != 2:
            raise ISO8601ParseError("Invalid ISO-8601 period string")
        newDelta = timedelta(int(splitString[0]), int(splitString[1]))
        return newDelta

    @staticmethod
    def formatTimeDelta(delta):
        """
        Exports a timedelta into an ISO806 format string
        :param delta: timedelta
        :type delta: timedelta
        :return: string
        """
        output = "P" + str(delta.days) + "T" + str(delta.seconds) + "S"
        return output
