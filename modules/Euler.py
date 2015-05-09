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
        
    def checkPalindrome(self,inputString):
        if(inputString==inputString[::-1]):
            return True
        else:
            return False
        
    def checkListInList(self,listSmall,listBig):
        listTest = list(listBig)
        for x in listSmall:
            if(x in listTest):
                listTest.remove(x)
            else:
                return False
        return True
    
    def findNumberOfFactors(self,number):
        number = int(number)
        numFactors = 2
        for x in range(2,int(math.sqrt(number))+1):
            if(number%x == 0):
                numFactors = numFactors + 2
        return numFactors
    
    def findFactors(self,number):
        number = int(number)
        factors = []
        for x in range(1,int(math.sqrt(number))+1):
            if(number%x == 0):
                factors.append(x)
                if(number/x!=x):
                    factors.append(number/x)
        return factors
    
    def removeListItems(self,inputList,removeItem):
        newList = []
        for item in inputList:
            if(item != removeItem):
                newList.append(item)
        return newList
    
    def listMinus(self,listOne,listTwo):
        listMinus = list(listOne)
        for x in listTwo:
            if(x in listMinus):
                listMinus.remove(x)
        return listMinus
    
    def listIntersection(self,listOne,listTwo):
        intersection = []
        tempList = list(listTwo)
        for x in listOne:
            if(x in tempList):
                intersection.append(x)
                tempList.remove(x)
        return intersection
    
    def listProduct(self,inputList):
        product = 1
        for number in inputList:
            product = product*number
        return product
    
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
    
    def euler26(self):
        #Get PrimeFactors function
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        functionClass = functionDispatcher.getFunctionByName("prime factors")
        functionObject = functionDispatcher.getFunctionObject(functionClass)
        #Do processing
        maxnines = 0
        maxd = 0
        for d in range(1,1000):
            factors = functionObject.findPrimeFactors(d)
            factors = self.removeListItems(factors,2)
            factors = self.removeListItems(factors,5)
            product = 1
            for factor in factors:
                product = product*factor
#            print "d = " + str(d) + ", product = " + str(product)
            nines = 0
            while True:
                nines = (nines * 10) + 9
                if(nines%product==0):
                    if(nines>maxnines):
                        maxnines = nines
                        maxd = d
#                        print "New record: " + str(d) + " requires " + str(len(str(nines))) + " nines."
                    break
        return maxd
    
    def euler27(self):
        maxLength = 0
        maxProduct = 1
        for b in range(1,1000):
            if(self.checkPrime(b)):
                for a in range(1,1000):
                    length = 0
                    n = 0
                    while True:
                        length = length + 1
                        n = n + 1
                        answer = (n**2) + (a*n) + b
                        if not self.checkPrime(answer):
                            break
                    if(length>maxLength):
                        maxLength = length
                        maxProduct = a * b
#                        print "new record: a = " + str(a) + ", b = " + str(b) + ", length = " + str(length)
                    length = 0
                    n = 0
                    if(a<b):
                        while True:
                            length = length + 1
                            n = n + 1
                            answer = (n**2) - (a*n) + b
                            if not self.checkPrime(answer):
                                break
                        if(length>maxLength):
                            maxLength = length
                            maxProduct = -(a * b)
#                            print "new record: a = -" + str(a) + ", b = " + str(b) + ", length = " + str(length)
        return maxProduct
    
    def euler28(self):
        total = 1
        n = 1
        for x in range(1,501):
            gap = x*2
            total = total + 4*n + 10*gap
            n = n + gap*4
        return total
    
    def euler29(self):
        #Get PrimeFactors function
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        functionClass = functionDispatcher.getFunctionByName("prime factors")
        functionObject = functionDispatcher.getFunctionObject(functionClass)
        #Do processing
        answers = []
        for a in range(2,101):
            afactors = functionObject.findPrimeFactors(a)
#            answer = a
            for b in range(2,101):
#                answer = answer * a
                answer = sorted(b * afactors)
                if(answer not in answers):
                    answers.append(answer)
        return len(answers)
    
    def euler30(self):
#        number = 10
#        while True:
        powerDigits = []
        for digit in range(10):
            powerDigits.append(digit**5)
        total = 0
        for number in range(10,200000):
            strNumber = str(number)
            lenNumber = len(strNumber)
            numberTotal = 0
            for x in range(lenNumber):
                numberTotal = numberTotal + powerDigits[int(strNumber[x])]
            if(numberTotal==number):
                total = total + number
        return total
    
    def euler31(self):
        #Get ChangeOptions function
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        functionClass = functionDispatcher.getFunctionByName("change options")
        functionObject = functionDispatcher.getFunctionObject(functionClass)
        #Do processing
        coins = [200,100,50,20,10,5,2,1]
        options = functionObject.changeOptions(coins,0,200)
        numoptions = len(options)
#        numoptions = euler.fnn_euler_changecount(self,coins,0,200)
        return numoptions
    
    def euler32(self):
        digits = [1,2,3,4,5,6,7,8,9]
        products = []
        for a in range(9):
            adigit = digits[a]
            adigits = list(digits)
            adigits.remove(adigit)
            for b in range(8):
                bdigit = adigits[b]
                bdigits = list(adigits)
                bdigits.remove(bdigit)
                for c in range(7):
                    cdigit = bdigits[c]
                    cdigits = list(bdigits)
                    cdigits.remove(cdigit)
                    for d in range(6):
                        ddigit = cdigits[d]
                        ddigits = list(cdigits)
                        ddigits.remove(ddigit)
                        for e in range(5):
                            edigit = ddigits[e]
                            edigits = list(ddigits)
                            edigits.remove(edigit)
                            productOne = (adigit*10+bdigit)*(cdigit*100+ddigit*10+edigit)
                            productTwo = adigit*(bdigit*1000+cdigit*100+ddigit*10+edigit)
                            failOne = False
                            failTwo = False
                            for f in range(4):
                                if(str(edigits[f]) not in list(str(productOne)) or productOne>9999):
                                    failOne = True
                            for g in range(4):
                                if(str(edigits[g]) not in list(str(productTwo)) or productTwo<1000 or productTwo>9999):
                                    failTwo = True
                            if(not failOne):
                                print(str(adigit)+str(bdigit)+"*"+str(cdigit)+str(ddigit)+str(edigit)+"="+str(productOne))
                                products.append(productOne)
                            if(not failTwo):
                                print(str(adigit)+"*"+str(bdigit)+str(cdigit)+str(ddigit)+str(edigit)+"="+str(productTwo))
                                products.append(productTwo)
        products = list(set(products))
        return sum(products)

    def euler33(self):
        #Get PrimeFactors function
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        functionClass = functionDispatcher.getFunctionByName("prime factors")
        functionObject = functionDispatcher.getFunctionObject(functionClass)
        #Do processing
        epsilon = 0.0000001
        totalNumeratorFactors = []
        totalDenominatorFactors = []
        for denominator in range(11,100):
            for numerator in range(10,denominator):
                if(str(numerator)[0] in str(denominator)):
                    if(str(denominator)[0]==str(denominator)[1]):
                        denominatorNew = int(str(denominator)[1])
                    else:
                        denominatorNew = int(str(denominator).replace(str(numerator)[0],''))
                    numeratorNew = int(str(numerator)[1])
                    numeratorFactorsNew = functionObject.findPrimeFactors(numeratorNew)
                    denominatorFactorsNew = functionObject.findPrimeFactors(denominatorNew)
                    if(denominatorNew!=0):
                        if((numerator/denominator-numeratorNew/denominatorNew)**2<epsilon):
                            print("found one." + str(numerator) + "/" + str(denominator))
                            totalNumeratorFactors = totalNumeratorFactors + numeratorFactorsNew
                            totalDenominatorFactors = totalDenominatorFactors + denominatorFactorsNew
                elif(str(numerator)[1] in str(denominator) and str(numerator)[1] != "0"):
                    if(str(denominator)[0]==str(denominator)[1]):
                        denominatorNew = int(str(denominator)[1])
                    else:
                        denominatorNew = int(str(denominator).replace(str(numerator)[1],''))
                    numeratorNew = int(str(numerator)[0])
                    numeratorFactorsNew = functionObject.findPrimeFactors(numeratorNew)
                    denominatorFactorsNew = functionObject.findPrimeFactors(denominatorNew)
                    if(denominatorNew!=0):
                        if((numerator/denominator-numeratorNew/denominatorNew)**2<epsilon):
                            print("found one." + str(numerator) + "/" + str(denominator))
                            totalNumeratorFactors = totalNumeratorFactors + numeratorFactorsNew
                            totalDenominatorFactors = totalDenominatorFactors + denominatorFactorsNew
        totalDenominatorFactorsNew = self.listMinus(totalDenominatorFactors,self.listIntersection(totalDenominatorFactors,totalNumeratorFactors))
        totalDenominatorNew = self.listProduct(totalDenominatorFactorsNew)
        return totalDenominatorNew

    def euler34(self):
        totalsum = 0
        factorials = [math.factorial(x) for x in range(10)]
        for x in range(3,10**6):
            strx = str(x)
            total = 0
            for number in strx:
                total = total + factorials[int(number)]
            if(total==x):
                totalsum += x
        return totalsum
    
    def euler35(self):
        number = 0
        for x in range(10**6):
            prime = True
            strx = str(x)
            for digit in range(len(strx)):
                rotatex = strx[digit:] + strx[:digit]
                prime = prime and self.checkPrime(int(rotatex))
            if(prime):
                number += 1
                print(x)
        return number
    
    def euler36(self):
        total = 0
        for a in range(10**6):
            if(self.checkPalindrome(str(a))):
                binary = bin(a)[2:]
                if(self.checkPalindrome(binary)):
                    total += a
        return total
    
    def euler37(self):
        total = 0
        num_found = 0
        number = 10
        while num_found<11 and number<10**7:
            strnumber = str(number)
            truncatable = True
            for x in range(len(strnumber)):
                truncatable = truncatable and self.checkPrime(int(strnumber[x:]))
                truncatable = truncatable and self.checkPrime(int(strnumber[:len(strnumber)-x]))
            if(truncatable):
                print('found one. ' + strnumber)
                num_found += 1
                total += number
            number += 1
        return total
    
    def euler38(self):
        maxConstr = 0
        for x in range(10**5):
            constr = ''
            n = 1
            while len(constr)<9:
                constr = constr + str(x*n)
                n += 1
            if(len(constr)==9 and int(constr)>maxConstr):
                if(self.checkListInList([str(x) for x in list(range(1,10))],list(constr))):
                    print('new max: ' + constr)
                    maxConstr = int(constr)
        return maxConstr

    def euler39(self):
        epsilon = 0.00000001
        maxP = 0
        maxPCount = 0
        for p in range(1,1001):
            pCount = 0
            pList = []
            for a in range(1,int(p/2)):
                b = (p*p-2*p*a)/(2*(a-p))
                c = (a*a+b*b)**0.5
                if(b%1<epsilon and c%1<epsilon):
                    pCount += 1
                    pList.append([int(a),int(b),int(c)])
            if(pCount>maxPCount):
                maxP = p
                maxPCount = pCount
        return "Maximum triangles for given perimeter is " + str(maxPCount) + " for the perimeter of " + str(maxP) + "."

    def euler40(self):
        stringLength = 0
        product = 1
        for number in range(1,10**6):
            addLength = len(str(number))
            if(stringLength<1<=stringLength+addLength):
                print('digit is ' + str(number)[1-stringLength-1])
                product = product*int(str(number)[1-stringLength-1])
            if(stringLength<10<=stringLength+addLength):
                print('digit is ' + str(number)[10-stringLength-1])
                product = product*int(str(number)[10-stringLength-1])
            if(stringLength<100<=stringLength+addLength):
                print('digit is ' + str(number)[100-stringLength-1])
                product = product*int(str(number)[100-stringLength-1])
            if(stringLength<1000<=stringLength+addLength):
                print('digit is ' + str(number)[1000-stringLength-1])
                product = product*int(str(number)[1000-stringLength-1])
            if(stringLength<10000<=stringLength+addLength):
                print('digit is ' + str(number)[10000-stringLength-1])
                product = product*int(str(number)[10000-stringLength-1])
            if(stringLength<100000<=stringLength+addLength):
                print('digit is ' + str(number)[100000-stringLength-1])
                product = product*int(str(number)[100000-stringLength-1])
            if(stringLength<1000000<=stringLength+addLength):
                print('digit is ' + str(number)[1000000-stringLength-1])
                product = product*int(str(number)[1000000-stringLength-1])
            stringLength += addLength
        return product














    