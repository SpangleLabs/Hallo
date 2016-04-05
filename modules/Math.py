from Function import Function
from inc.commons import Commons
import math


class Hailstone(Function):
    """
    Runs a collatz (or hailstone) function on a specified number, returning the sequence generated.
    """
    # Name for use in help listing
    mHelpName = "hailstone"
    # Names which can be used to address the Function
    mNames = {"hailstone", "collatz", "collatz sequence"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "The hailstone function has to be given with a number (to generate the collatz sequence of.)"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """Returns the hailstone sequence for a given number. Format: hailstone <number>"""
        lineClean = line.strip().lower()
        if not lineClean.isdigit():
            return "The hailstone function has to be given with a number (to generate the collatz sequence of.)"
        else:
            number = int(lineClean)
            sequence = self.collatzSequence([number])
            outputString = "Hailstone (Collatz) sequence for " + str(number) + ": "
            outputString += '->'.join(str(x) for x in sequence) + " (" + str(len(sequence)) + " steps.)"
            return outputString

    def collatzSequence(self, sequence):
        num = int(sequence[-1])
        if num == 1:
            return sequence
        elif num % 2 == 0:
            sequence.append(num // 2)
            return self.collatzSequence(sequence)
        else:
            sequence.append(3 * num + 1)
            return self.collatzSequence(sequence)


class NumberWord(Function):
    """
    Converts a number to the textual representation of that number.
    """
    # Name for use in help listing
    mHelpName = "number"
    # Names which can be used to address the Function
    mNames = {"number", "number word", "numberword"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the textual representation of a given number. Format: number <number>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        if line.count(' ') == 0:
            number = line
            lang = "american"
        elif line.split()[1].lower() in ["british", "english"]:
            number = line.split()[0]
            lang = "english"
        elif line.split()[1].lower() in ["european", "french"]:
            number = line.split()[0]
            lang = "european"
        else:
            number = line.split()[0]
            lang = "american"
        if Commons.checkNumbers(number):
            number = number
            # TODO: implement this, once calc is transferred
        #        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,number)):
        #            number = mod_calc.fn_calc(self,number,client,destination)
        #            if(str(number)[-1]=='.'):
        #                number = number[:-1]
        else:
            return "You must enter a valid number or calculation."
        return self.numberWord(number, lang) + "."

    def numberWord(self, number, lang="american"):
        # Set up some arrays
        digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
                  'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['zero', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        normalSegs = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion', 'sextillion',
                      'septillion', 'octillion', 'nonillion', 'decillion', 'undecillion', 'duodecillion',
                      'tredecillion']
        europeanSegs = ['', 'thousand', 'million', 'milliard', 'billion', 'billiard', 'trillion', 'trilliard',
                        'quadrillion', 'quadrilliard', 'quintillion', 'quintilliard', 'sextillion', 'sextilliard',
                        'septillion']
        englishSegs = ['', 'thousand', 'million', 'thousand million', 'billion', 'thousand billion', 'trillion',
                       'thousand trillion', 'quadrillion', 'thousand quadrillion', 'quintillion',
                       'thousand quintillion', 'sextillion', 'thousand sextillion', 'septillion']
        # Check for amount of decimal points
        if number.count('.') > 1:
            return "There's too many decimal points in that."
        # If there's a decimal point, write decimal parts
        elif number.count('.') == 1:
            expNumber = number.split('.')
            numberDecimal = expNumber[1]
            number = expNumber[0]
            decimal = " point"
            for num in numberDecimal:
                decimal = decimal + " " + digits[int(num)]
        else:
            decimal = ""
        # Convert number to a string, to string
        number = str(number)
        # Check if number is negative
        if number[0] == "-":
            number = number[1:]
            string = 'negative '
        else:
            string = ''
        # find number of segments, and justify up to a number of digits divisible by 3
        segments = int(math.ceil(float(len(number)) / 3) + 0.01)
        number = number.rjust(3 * segments, '0')
        # If number is zero, say zero.
        if number == "000":
            string += "zero"
        # Write out segments
        for seg in range(segments):
            start = seg * 3
            end = start + 3
            segment = number[start:end]
            # string = string + "(" + segment + ")"
            # Convert first number of segment
            if segment[0] != "0":
                string = string + digits[int(segment[0])] + " hundred "
                if int(segment[1:]) != 0:
                    string += "and "
            elif seg != 0 and int(segment[1:]) != 0:
                string += "and "
            # Convert second and third numbers of segment
            if int(segment[1:]) == 0:
                pass
            elif int(segment[1:]) < 20:
                string = string + digits[int(segment[1:])]
            else:
                string += tens[int(segment[1])]
                if segment[2] != "0":
                    string = string + "-" + digits[int(segment[2])]
            # Add segment cardinal.
            if seg != (segments - 1) and segment != "000":
                if lang.lower() == "american":
                    string = string + " " + normalSegs[segments - seg - 1]
                elif lang.lower() == "english":
                    string = string + " " + englishSegs[segments - seg - 1]
                elif lang.lower() == "european":
                    string = string + " " + europeanSegs[segments - seg - 1]
                else:
                    string = string + " " + normalSegs[segments - seg - 1]
            if seg != (segments - 1) and int(number[end:end + 3]) != 0:
                string += ', '
        # Put string together and output
        string += decimal
        return string


class PrimeFactors(Function):
    """
    Finds prime factors of a specified number
    """
    # Name for use in help listing
    mHelpName = "prime factors"
    # Names which can be used to address the Function
    mNames = {"prime factors", "prime factor", "primefactors", "primefactor"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the prime factors of a given number. Format: prime factors <number>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        lineClean = line.strip().lower()
        if lineClean.isdigit():
            number = int(lineClean)
            # TODO: implement this, once calc is transferred
        #        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,args)):
        #            args = mod_calc.mod_calc.fn_calc(self,args,client,destination)
        #            if(str(args)[-1]=='.'):
        #                args = args[:-1]
        #            args = int(args)
        else:
            return "This is not a valid number or calculation."
        prime_factors = self.findPrimeFactors(number)
        return "The prime factors of " + str(number) + " are: " + 'x'.join(str(x) for x in prime_factors) + "."

    def findPrimeFactors(self, number):
        number = int(number)
        factors = []
        notPrime = False
        for x in range(2, int(math.sqrt(number)) + 1):
            if number % x == 0:
                factors.append(x)
                factors.extend(self.findPrimeFactors(number // x))
                notPrime = True
                break
        if not notPrime:
            return [number]
        else:
            return factors


class ChangeOptions(Function):
    """
    Returns the number of options for change in UK currency for a certain value
    """
    # Name for use in help listing
    mHelpName = "change options"
    # Names which can be used to address the Function
    mNames = {"change options", "changeoptions", "change", "change ways"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the different ways to give change for a given amount (in pence, using british coins.) " \
                "Format: change_options <number>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """
        Returns the number of ways to give change for a given amount (in pence, using british coins.)
        Format: change_options <number>
        """
        lineClean = line.strip().lower()
        try:
            number = int(lineClean)
        except ValueError:
            return "That's not a valid number."
        if number > 20:
            return "For reasons of output length, I can't return change options for more than 20 pence."
        coins = [200, 100, 50, 20, 10, 5, 2, 1]
        options = self.changeOptions(coins, 0, number)
        outputString = 'Possible ways to give that change: '
        for option in options:
            outputString += '[' + ','.join(str(x) for x in option) + '],'
        return outputString + "."

    def changeOptions(self, coins, coinnum, amount):
        coinamount = amount // coins[coinnum]
        change = []
        if amount == 0:
            return change
        elif coinnum == len(coins) - 1:
            change.append([coins[coinnum]] * (amount // coins[coinnum]))
        else:
            for x in range(coinamount, -1, -1):
                remaining = amount - x * coins[coinnum]
                if remaining == 0:
                    change.append(x * [coins[coinnum]])
                else:
                    changeadd = self.changeOptions(coins, coinnum + 1, remaining)
                    for changeoption in changeadd:
                        change.append(x * [coins[coinnum]] + changeoption)
        return change


class Average(Function):
    """
    Finds the average of a given list of numbers.
    """
    # Name for use in help listing
    mHelpName = "average"
    # Names which can be used to address the Function
    mNames = {"average", "avg", "mean"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Finds the average of a list of numbers. Format: average <number1> <number2> ... <number n>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        numberList = line.split()
        try:
            numberSum = sum(float(x) for x in numberList)
        except ValueError:
            return "Please only input a list of numbers"
        return "The average of " + ', '.join(numberList) + " is: " + str(numberSum / float(len(numberList))) + "."


class HighestCommonFactor(Function):
    """
    Finds the highest common factor of a pair of numbers.
    """
    # Name for use in help listing
    mHelpName = "highest common factor"
    # Names which can be used to address the Function
    mNames = {"highest common factor", "highestcommonfactor", "hcf"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the highest common factor of two numbers. Format: highest common factor <number1> <number2>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        # Getting functionDispatcher and required function objects
        halloObject = userObject.get_server().get_hallo()
        functionDispatcher = halloObject.get_function_dispatcher()
        primeFactorsClass = functionDispatcher.get_function_by_name("prime factors")
        eulerClass = functionDispatcher.get_function_by_name("euler")
        primeFactorsObject = functionDispatcher.get_function_object(primeFactorsClass)
        eulerObject = functionDispatcher.get_function_object(eulerClass)
        # Preflight checks
        if len(line.split()) != 2:
            return "You must provide two arguments."
        inputOne = line.split()[0]
        inputTwo = line.split()[1]
        try:
            numberOne = int(inputOne)
            numberTwo = int(inputTwo)
        except ValueError:
            return "Both arguments must be integers."
        # Get prime factors of each, get intersection, then product of that.
        numberOneFactors = primeFactorsObject.findPrimeFactors(numberOne)
        numberTwoFactors = primeFactorsObject.findPrimeFactors(numberTwo)
        commonFactors = eulerObject.listIntersection(numberOneFactors, numberTwoFactors)
        HCF = eulerObject.listProduct(commonFactors)
        return "The highest common factor of " + str(numberOne) + " and " + str(numberTwo) + " is " + str(HCF) + "."


class SimplifyFraction(Function):
    """
    Simplifies an inputted fraction
    """
    # Name for use in help listing
    mHelpName = "simplify fraction"
    # Names which can be used to address the Function
    mNames = {"simplify fraction", "simplifyfraction", "fraction", "simple fraction", "base fraction",
              "fraction simplify"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a fraction in its simplest form. Format: simplify fraction <numerator>/<denominator>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        # Getting functionDispatcher and required function objects
        halloObject = userObject.get_server().get_hallo()
        functionDispatcher = halloObject.get_function_dispatcher()
        primeFactorsClass = functionDispatcher.get_function_by_name("prime factors")
        eulerClass = functionDispatcher.get_function_by_name("euler")
        primeFactorsObject = functionDispatcher.get_function_object(primeFactorsClass)
        eulerObject = functionDispatcher.get_function_object(eulerClass)
        # preflight checks
        if line.count("/") != 1:
            return "Please give input in the form: <numerator>/<denominator>"
        # Get numerator and denominator
        numeratorString = line.split('/')[0]
        denominatorString = line.split('/')[1]
        try:
            numerator = int(numeratorString)
            denominator = int(denominatorString)
        except ValueError:
            return "Numerator and denominator must be integers."
        # Sort all this and get the value
        numeratorFactors = primeFactorsObject.findPrimeFactors(numerator)
        denominatorFactors = primeFactorsObject.findPrimeFactors(denominator)
        numeratorFactorsNew = eulerObject.listMinus(numeratorFactors,
                                                    eulerObject.listIntersection(denominatorFactors, numeratorFactors))
        denominatorFactorsNew = eulerObject.listMinus(denominatorFactors,
                                                      eulerObject.listIntersection(denominatorFactors,
                                                                                   numeratorFactors))
        numeratorNew = eulerObject.listProduct(numeratorFactorsNew)
        denominatorNew = eulerObject.listProduct(denominatorFactorsNew)
        return str(numerator) + "/" + str(denominator) + " = " + str(numeratorNew) + "/" + str(denominatorNew) + "."


class Calculate(Function):
    """
    Standard calculator function
    """
    # Name for use in help listing
    mHelpName = "calc"
    # Names which can be used to address the Function
    mNames = {"calc", "calculate", "calculator"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Calculate function, calculates the answer to mathematical expressions. Format: calc <calculation>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        calc = line
        # check for equals signs, and split at them if so.
        if calc.count('=') >= 1:
            calcParts = calc.split('=')
            ansParts = []
            numberAnswers = []
            num_calcs = 0
            for calcPart in calcParts:
                # run preflight checks, if it passes do the calculation, if it doesn't return the same text.
                try:
                    self.preflightChecks(calcPart)
                    calcPart = calcPart.replace(' ', '').lower()
                    anspart = self.processCalculation(calcPart)
                    ansParts.append(anspart)
                    numberAnswers.append(anspart)
                    num_calcs += 1
                except Exception as e:
                    print(str(e))
                    ansParts.append(calcPart)
            answer = '='.join(ansParts)
            # Check if all number results are equal.
            if not numberAnswers or numberAnswers.count(numberAnswers[0]) == len(numberAnswers):
                answer += "\n" + "Wait, that's not right..."
            return answer
        # If there's no equals signs, collapse it all together
        calc = calc.replace(' ', '').lower()
        try:
            self.preflightChecks(calc)
            answer = self.processCalculation(calc)
        except Exception as e:
            answer = str(e)
        return answer

    def getPassiveEvents(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def passiveRun(self, event, fullLine, serverObject, userObject=None, channelObject=None):
        """Replies to an event not directly addressed to the bot."""
        # Check if fullLine is a calculation, and is not just numbers, and contains numbers.
        if not Commons.checkCalculation(fullLine):
            return None
        if Commons.checkNumbers(fullLine):
            return None
        if not any([char in fullLine for char in [str(x) for x in range(10)] + ["e", "pi"]]):
            return None
        # Clean up the line and feed to the calculator.
        calc = fullLine.replace(' ', '').lower()
        try:
            self.preflightChecks(calc)
            answer = self.processCalculation(calc)
            return answer
        except Exception as e:
            print("Passive calc failed: "+str(e))
            return None

    def afterInfix(self, calc, subStr):
        # If substring is at the end, return empty string.
        if calc.endswith(subStr):
            return ""
        # Find position and get the calculation after that position.
        pos = calc.find(str(subStr))
        postCalc = calc[pos + len(subStr):]
        # Check each substring of postCalc for whether it's a valid float, starting from longest.
        for subPostCalc in [postCalc[:len(postCalc) - x] for x in range(len(postCalc))]:
            try:
                float(subPostCalc)
                return subPostCalc
            except ValueError:
                pass
        return ""

    def beforeInfix(self, calc, subStr):
        # If substring is at the start, return empty string.
        if calc.startswith(subStr):
            return ""
        # Find position and get the calculation before that position.
        pos = calc.find(str(subStr))
        preCalc = calc[:pos]
        # Check each substring of preCalc for whether it's a valid float, starting from longest.
        for subPreCalc in [preCalc[x:] for x in range(len(preCalc))]:
            try:
                float(subPreCalc)
                if subPreCalc[0] == "+":
                    subPreCalc = subPreCalc[1:]
                return subPreCalc
            except ValueError:
                pass
        return ""

    def preflightChecks(self, calc):
        # strip spaces
        calcClean = calc.replace(' ', '').lower()
        # make sure only legit characters are allowed
        if not Commons.checkCalculation(calcClean):
            raise Exception('Error, Invalid characters in expression')
        # make sure open brackets don't out-number close
        if calc.count('(') > calc.count(')'):
            raise Exception('Error, too many open brackets')
        return True

    def processTrigonometry(self, calc, runningCalc):
        tempAnswer = self.processCalculation(runningCalc)
        runningCalc = '(' + runningCalc + ')'
        before = calc.split(runningCalc)[0]
        trigDict = {'acos': math.acos, 'asin': math.asin, 'atan': math.atan, 'cos': math.cos, 'sin': math.sin,
                    'tan': math.tan, 'sqrt': math.sqrt, 'log': math.log, 'acosh': math.acosh, 'asinh': math.asinh,
                    'atanh': math.atanh, 'cosh': math.cosh, 'sinh': math.sinh, 'tanh': math.tanh, 'gamma': math.gamma}
        for trigName in trigDict:
            if before[-len(trigName):] == trigName:
                return [trigName + runningCalc, trigDict[trigName](float(tempAnswer))]
        return [runningCalc, tempAnswer]

    def processCalculation(self, calc):
        # Swapping "x" for "*"
        calc = calc.replace("x", "*")
        # constant evaluation
        while calc.count('pi') != 0:
            tempAnswer = math.pi
            if self.beforeInfix(calc, 'pi') != '':
                tempAnswer = '*' + str(tempAnswer)
            if self.afterInfix(calc, 'pi') != '':
                tempAnswer = str(tempAnswer) + '*'
            calc = calc.replace('pi', str(tempAnswer))
            del tempAnswer
        while calc.count('e') != 0:
            tempAnswer = math.e
            if self.beforeInfix(calc, 'e') != '':
                tempAnswer = '*' + str(tempAnswer)
            if self.afterInfix(calc, 'e') != '':
                tempAnswer = str(tempAnswer) + '*'
            calc = calc.replace('e', str(tempAnswer))
            del tempAnswer
        # bracket processing
        if calc.count(")-") != 0:
            calc = calc.replace(")-", ")+-")
        while calc.count('(') != 0:
            tempCalc = calc[calc.find('(') + 1:]
            bracket = 1
            runningCalc = ''
            # Loop through the string
            nextChar = None
            for nextChar in tempCalc:
                if nextChar == '(':
                    bracket += 1
                elif nextChar == ')':
                    bracket -= 1
                if bracket == 0:
                    # tempans = mod_calc.fnn_calc_process(self,runningCalc)
                    # runningCalc = '('+runningCalc+')'
                    trigcheck = self.processTrigonometry(calc, runningCalc)
                    tempAnswer = trigcheck[1]
                    runningCalc = trigcheck[0]
                    beforeRunningCalc = self.beforeInfix(calc, runningCalc)
                    if beforeRunningCalc != '':
                        runningCalc = beforeRunningCalc + runningCalc
                        tempAnswer = beforeRunningCalc + '*' + str(tempAnswer)
                    afterRunningCalc = self.afterInfix(calc, runningCalc)
                    if afterRunningCalc != '' and afterRunningCalc[0] != '+':
                        runningCalc = runningCalc + afterRunningCalc
                        tempAnswer = str(tempAnswer) + '*' + afterRunningCalc
                    calc = calc.replace(runningCalc, str(tempAnswer))
                    del tempAnswer
                    break
                runningCalc = runningCalc + nextChar
            del tempCalc, bracket, runningCalc, nextChar
        calc = calc.replace(')', '')
        # powers processing
        while calc.count('^') != 0:
            preCalc = self.beforeInfix(calc, '^')
            postCalc = self.afterInfix(calc, '^')
            calc = calc.replace(str(preCalc) + '^' + str(postCalc), str(float(preCalc) ** float(postCalc)), 1)
            del preCalc, postCalc
        # powers processing 2
        while calc.count('**') != 0:
            preCalc = self.beforeInfix(calc, '**')
            postCalc = self.afterInfix(calc, '**')
            calc = calc.replace(str(preCalc) + '**' + str(postCalc), str(float(preCalc) ** float(postCalc)), 1)
            del preCalc, postCalc
        # modulo processing
        while calc.count('%') != 0:
            preCalc = self.beforeInfix(calc, '%')
            postCalc = self.afterInfix(calc, '%')
            if float(postCalc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(preCalc) + '%' + str(postCalc), str(float(preCalc) % float(postCalc)), 1)
            del preCalc, postCalc
        # multiplication processing
        while calc.count('/') != 0:
            preCalc = self.beforeInfix(calc, '/')
            postCalc = self.afterInfix(calc, '/')
            if float(postCalc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(preCalc) + '/' + str(postCalc), str(float(preCalc) / float(postCalc)), 1)
            del preCalc, postCalc
        # multiplication processing
        while calc.count('*') != 0:
            preCalc = self.beforeInfix(calc, '*')
            postCalc = self.afterInfix(calc, '*')
            calc = calc.replace(str(preCalc) + '*' + str(postCalc), str(float(preCalc) * float(postCalc)), 1)
            del preCalc, postCalc
        # addition processing
        calc = calc.replace('-', '+-')
        answer = 0
        calc = calc.replace('e+', 'e')
        for tempAnswer in calc.split('+'):
            if tempAnswer != '':
                try:
                    answer += float(tempAnswer)
                except ValueError:
                    answer = answer
        answer = '{0:.10f}'.format(answer)
        if '.' in answer:
            while answer[-1] == '0':
                answer = answer[:-1]
        if answer[-1] == '.':
            answer = answer[:-1]
        return answer
