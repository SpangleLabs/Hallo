from Function import Function
import math

class Euler(Function):
    '''
    euler project functions
    '''
    #Name for use in help listing
    mHelpName = "euler"
    #Names which can be used to address the Function
    mNames = set(["euler","euler project","project euler"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Project Euler functions. Format: \"euler list\" to list project euler solutions. \"euler <number>\" for the solution to project euler problem of the given number."
    
    mHalloObject = None
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Some functions might need this.
        self.mHalloObject = userObject.getServer().getHallo()
        lineClean = line.strip().lower()
        if(lineClean=="list"):
            return self.listAll()
        elif(lineClean.isdigit()):
            return self.runFunction(lineClean)
        else:
            countSolutions = len(funcName for funcName in dir(self) if funcName[:5] == 'euler' and funcName[5:].isdigit())
            outputString = "I'm learning to complete the project Euler programming problems."
            outputString += "I've not done many so far, I've only done " + str(countSolutions) + " of the 514 problems."
            outputString += "But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, "
            outputString += "say 'Hallo Euler {num}' for the answer to challenge number {num}."
            return outputString
    
    def listAll(self):
        #list all available project Euler answers
        problemFuncNames = []
        for funcName in dir(self):
            if(funcName[:5] == 'euler' and funcName[5:].isdigit()):
                problemFuncNames.append(funcName[5:])
        problemFuncNames = sorted(problemFuncNames,key=int)
        outputString = "Currently I can do "+str(len(problemFuncNames))+" Project Euler problems " 
        outputString += ', '.join(problemFuncNames[:-1]) 
        outputString += " and " + problemFuncNames[-1] + "."
        return outputString
    
    def runFunction(self,numberString):
        functionName = "euler"+numberString
        functionNames = [funcName for funcName in dir(self) if funcName[:5] == 'euler' and funcName[5:].isdigit()]
        if(functionName not in functionNames):
            return "I don't think I've solved that one yet."
        functionObject = getattr(self,functionName)
        if(not hasattr(functionObject,"__call__")):
            return "That doesn't seem to work."
        try:
            outputString = "Euler project problem " + numberString + "? I think the answer is: " + str(functionObject()) + "."
        except Exception as e:
            outputString = "Hmm, seems that one doesn't work... darnit."
            print("EULER ERROR: " + str(e))
        return outputString
    
    def euler1(self):
        threeCount = math.floor(999/3)
        fiveCount = math.floor(999/5)
        fifteenCount = math.floor(999/15)
        threeSum = 3*((0.5*(threeCount**2))+(0.5*threeCount))
        fiveSum = 5*((0.5*(fiveCount**2))+(0.5*fiveCount))
        fifteenSum = 15*((0.5*(fifteenCount**2))+(0.5*fifteenCount))
        answer = threeSum + fiveSum - fifteenSum
        return answer
    
    def euler2(self):
        previousNum = 1
        currentNum = 2
        answer = 0
        while currentNum < 4000000:
            if(currentNum % 2 == 0):
                answer = answer + currentNum
            newNum = currentNum + previousNum
            previousNum = currentNum
            currentNum = newNum
        return answer
    
    def euler3(self):
        limit = 600851475143
        factorLimit = int(math.floor(math.sqrt(limit)))
        biggestPrimeFactor = 1
        for i in range(1,factorLimit):
            if(limit%i == 0):
                checkPrime = i
                checkPrimeLimit = int(math.floor(math.sqrt(checkPrime)))
                checkPrimeFactor = 1
                for j in range(1,checkPrimeLimit):
                    if(checkPrime%j == 0):
                        checkPrimeFactor = j
                if(checkPrimeFactor == 1):
                    biggestPrimeFactor = i
        return biggestPrimeFactor
    
    def euler4(self):
        biggestPalandrome = 0
        biggestPalandromeX = 0
        biggestPalandromeY = 0
        stopLoop = 100
        for x in range(999,100,-1):
            if(x < stopLoop):
                break
            for y in range(999,x,-1):
                product = x * y
                reverseProduct = int(str(product)[::-1])
                if(product == reverseProduct and product > biggestPalandrome):
                    biggestPalandrome = product
                    biggestPalandromeX = x
                    biggestPalandromeY = y
                    stopLoop = int(math.floor(biggestPalandrome/999))
        return "answer is: " + str(biggestPalandrome) + " = " + str(biggestPalandromeX) + "x" + str(biggestPalandromeY)
    
    def checkPrime(self,inputNumber):
        checkPrime = inputNumber
        checkPrimeFactor = 1
        if(checkPrime<=0):
            return False
        for j in range(2,int(math.floor(math.sqrt(checkPrime)))+1):
            if(checkPrime%j == 0):
                checkPrimeFactor = j
                break
        if(checkPrimeFactor == 1 and inputNumber!=1):
            return True
        else:
            return False
    
    def euler5(self):
        factors = {}
        maximum = 20
        for num in range(1,maximum+1):
            for x in range(1,num+1):
                if(num%x == 0):
                    if(self.checkPrime(x)):
                        if(x not in factors):
                            factors[x] = 1
                        dividesCount = 1
                        for attempt in range(1,6):
                            if(num%(x**attempt) == 0):
                                dividesCount = attempt
                        if(factors[x] < dividesCount):
                            factors[x] = dividesCount
        answer = 1
        for prime, power in factors.items():
            answer = answer*(prime**power)
        return answer
    
    def euler6(self):
        answer = 0
        for x in range(1,101):
            answer = answer + x*(0.5*(101**2)-0.5*101) - x**2
        return answer
    
    def euler7(self):
        numPrimes = 0
        test = 1
        prime = 1
        while numPrimes < 10001:
            test = test + 1
            if(self.checkPrime(test)):
                numPrimes = numPrimes + 1
                prime = test
        return prime
    
    def euler8(self):
        string = open("store/euler/euler_8_string.txt","r").read()[:-1]
        biggestProduct = 0
        while(len(string)>=5):
            substring = string[0:5]
            product = int(substring[0])*int(substring[1])*int(substring[2])*int(substring[3])*int(substring[4])
            biggestProduct = max(product, biggestProduct)
            string = string[1:]
        return biggestProduct
    
    def euler9(self):
        answera = 0
        answerb = 0
        answerc = 0
        answer = 0
        for b in range(500,0,-1):
            for a in range(b-1,0,-1):
                c = math.sqrt(a**2+b**2)
                if(c-math.floor(c)<=0.001 and a+b+int(c)==1000):
                    answera = a
                    answerb = b
                    answerc = int(c)
                    answer = a*b*int(c)
        return "a = " + str(answera) + ", b = " + str(answerb) + ", c = " + str(answerc) + " and a*b*c = " + str(answer)
    
    def euler10(self):
        numbers = [0] * 2000000
        primeSum = 2
        for x in range(3,2000000,2):
            if(numbers[x]==0):
                primeSum = primeSum + x
                for y in range(x,2000000,x):
                    numbers[y] = 1
        return primeSum
    
    def euler11(self):
        rawBox = open("store/euler/euler_11_grid.txt").read()[:-1]
        arrBox = rawBox.split()
        biggestProduct = 0
        answerX = 0
        answerY = 0
        direction = ''
        #vertical checks
        for x in range(0,20):
            for y in range(0,17):
                product = int(arrBox[x+20*y])*int(arrBox[x+20*y+20])*int(arrBox[x+20*y+40])*int(arrBox[x+20*y+60])
                if(product>biggestProduct):
                    biggestProduct = product
                    answerX = x
                    answerY = y
                    direction = "vertical"
        #horizontal checks
        for x in range(0,17):
            for y in range(0,20):
                product = int(arrBox[x+20*y])*int(arrBox[x+20*y+1])*int(arrBox[x+20*y+2])*int(arrBox[x+20*y+3])
                if(product>biggestProduct):
                    biggestProduct = product
                    answerX = x
                    answerY = y
                    direction = "horizontal"
        #diagonal check \
        for x in range(0,17):
            for y in range(0,17):
                product = int(arrBox[x+20*y])*int(arrBox[x+20*y+21])*int(arrBox[x+20*y+42])*int(arrBox[x+20*y+63])
                if(product>biggestProduct):
                    biggestProduct = product
                    answerX = x
                    answerY = y
                    direction = "diagonal \\"
        #diagonal check /
        for x in range(3,20):
            for y in range(0,17):
                product = int(arrBox[x+20*y])*int(arrBox[x+20*y+19])*int(arrBox[x+20*y+38])*int(arrBox[x+20*y+57])
                if(product>biggestProduct):
                    biggestProduct = product
                    answerX = x
                    answerY = y
                    direction = "diagonal /"
        outputString = "biggest product is: " + str(biggestProduct)
        outputString += " the coords are: (" + str(answerX) + "," + str(answerY) + ") in the direction: " + direction
        return outputString
    
    def findNumberOfFactors(self,number):
        number = int(number)
        numFactors = 2
        for x in range(2,int(math.sqrt(number))+1):
            if(number%x == 0):
                numFactors = numFactors + 2
        return numFactors
    
    def euler12(self):
        number = 1
        numFactors = 0
        while numFactors<500:
            number = number + 1
            if(number%2 == 0):
                numFactors = self.findNumberOfFactors(number+1)*self.findNumberOfFactors(number/2)
            else:
                numFactors = self.findNumberOfFactors((number+1)/2)*self.findNumberOfFactors(number)
        triangle = ((number+1)*number)/2
        return triangle
    
    def euler13(self):
        arrNumbers = open("store/euler/euler_13_numbers.txt","r").read()[:-1]
        total = 0
        for number in arrNumbers:
            total = total + int(number)
        return str(total)[0:10]
    
    def euler14(self):
        lengths = [0] * 1000000
        maxChain = 0
        maxStart = 0
        for start in range(1,1000000):
            num = start
            length = 1
            while True:
                if(num==1):
                    lengths[start] = length
                    break
                if(num < 1000000 and lengths[num] != 0):
                    lengths[start] = length + lengths[num]
                    break
                if(num%2 == 0):
                    num = num//2
                    length = length + 1
                else:
                    num = (3*num)+1
                    length = length + 1
            if(maxChain < lengths[start]):
#                print "new longest chain, it starts at: " + str(start) + " and is " + str(lengths[start]) + " steps long. Exploited a " + str(jump) + " step jump! meaning I only had to do " + str(lengths[start]-jump) + " steps myself."
                maxChain = lengths[start]
                maxStart = start
        return maxStart
    
    def euler15(self):
        gridSize = 20
        x = gridSize
        routes = 1
        for y in range(x):
            routes = routes*(x+y+1)/(y+1)
        return routes
    
    def euler16(self):
        bigNumber = 2**1000
        bigNumber = str(bigNumber)
        total = 0
        for x in range(len(bigNumber)):
            total = total + int(bigNumber[x])
        return total
    
    def euler17(self):
        #Get Number function
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        functionClass = functionDispatcher.getFunctionByName("number")
        functionObject = functionDispatcher.getFunctionObject(functionClass)
        #Do processing
        total = 0
        for x in range(1,1001):
            total = total + len(functionObject.numberWord(str(x)).replace(' ','').replace('-',''))
        return total
        
    def euler18(self):
        arrTriangle = open("store/euler/euler_18_triangle.txt","r").read()[:-1].split("\n")
        for x in range(len(arrTriangle)):
            arrTriangle[x] = arrTriangle[x].split()
        for row in range(len(arrTriangle)-2,-1,-1):
            for col in range(len(arrTriangle[row])):
                if(int(arrTriangle[row+1][col]) > int(arrTriangle[row+1][col+1])):
                    arrTriangle[row][col] = int(arrTriangle[row][col]) + int(arrTriangle[row+1][col])
                else:
                    arrTriangle[row][col] = int(arrTriangle[row][col]) + int(arrTriangle[row+1][col+1])
        return arrTriangle[0][0]
    
    def euler19(self):
        day = 1+365
        year = 0
        total = 0
        while year < 101:
            year = year + 1
            for month in range(12):
                if(day%7==0):
                    total = total + 1
                if(month == 2):
                    if((year%4 == 0 and year%100 != 0) or year%400 == 0):
                        day = day + 29
                    else:
                        day = day + 28 
                elif(month in [9,11,4,6]):
                    day = day + 30
                else:
                    day = day + 31
        return total
    
    def euler20(self):
        number = math.factorial(100)
        number = str(number)
        total = 0
        for x in range(len(number)):
            total = total + int(number[x])
        return total
    
    def findFactors(self,number):
        number = int(number)
        factors = []
        for x in range(1,int(math.sqrt(number))+1):
            if(number%x == 0):
                factors.append(x)
                if(number/x!=x):
                    factors.append(number/x)
        return factors
    
    def euler21(self):
        amicable = []
        total = 0
        for x in range(10000):
            if(x not in amicable):
                factors = self.findFactors(x)
                factorTotal = 0
                for factor in factors:
                    factorTotal = factorTotal + factor
                otherNumber = factorTotal-x
                otherFactors = self.findFactors(otherNumber)
                otherFactorTotal = 0
                for otherFactor in otherFactors:
                    otherFactorTotal = otherFactorTotal + otherFactor
                if(otherFactorTotal-otherNumber==x and otherNumber!=x):
                    print("found a pair: " + str(x) + " and " + str(factorTotal-x))
                    amicable.append(x)
                    amicable.append(factorTotal-x)
                    total = total + x + otherNumber
        return total
    
    def euler22(self):
        rawNames = open("store/euler/euler_22_names.txt","r").read()[:-1]
        arrNames = sorted(rawNames.replace('"','').split(','))
        total = 0
        nameNum = 0
        for name in arrNames:
            nameNum = nameNum + 1
            value = 0
            for letter in range(len(name)):
                value = value + ord(name[letter])-64
            score = value * nameNum
            total = total + score
        return total
    
    def euler23(self):
        abundantNumbers = []
        sumOfTwo = [0] * 28150
        total = (28150/2)*(1+28150)-28150
        for x in range(28150):
            factors = self.findFactors(x)
            factorTotal = 0
            for factor in factors:
                factorTotal = factorTotal + factor
            factorTotal = factorTotal - x
            if(factorTotal>x):
                abundantNumbers.append(x)
                for otherNumber in abundantNumbers:
                    abSum = otherNumber+x
                    if(abSum<28150):
                        if(sumOfTwo[abSum] != 1):
                            sumOfTwo[abSum] = 1
                            total = total - (abSum)
                    else:
                        break
        return total
    
    def euler24(self):
        digits = [0,1,2,3,4,5,6,7,8,9]
        permutation = 1000000-1
        string = ''
        while len(digits)!=1:
            number = int(math.floor(permutation/math.factorial(len(digits)-1)))
            string = string + str(digits[number])
            del digits[number]
            permutation = permutation - int(math.factorial(len(digits))*number)
        string = string + str(digits[0])
        return string

    def euler25(self):
        length = 0
        a = 1
        b = 1
        num = 2
        while length<1000:
            num = num + 1
            c = a + b
            a = b
            b = c
            length = len(str(c))
        return num




    