#from ircbot import ircbot
import math

class euler:
    def fn_euler(self, args, client, destination):
        'Project Euler functions'
        if(args.replace(' ','').isdigit()):
            #try and do that euler function command
            try: eulerfunc = getattr(self, 'fnn_euler_' + args)
            except: answer = "I don't think I've solved that one yet."
            else:
                if(hasattr(eulerfunc, '__call__')):
                    try:
                        answer = "Euler project problem " + args + "? I think the answer is: " + str(eulerfunc())
                    except Exception, e:
                        answer = "hmm, seems that one doesn't work... darnit."
                        print "EULER ERROR: " + str(e)
                else:
                    answer = "That doesn't seem to work"
        elif(args.replace(' ','').lower() == 'list'):
            #list all available project Euler answers
            problem_funcs = []
            for fn in dir(self):
                if(fn[:10] == 'fnn_euler_' and fn[10:].isdigit()):
                    problem_funcs.append(fn[10:])
            answer = "Currently I can do Project Euler problems " + ', '.join(sorted(problem_funcs,key=int)[:-1]) + " and " + sorted(problem_funcs,key=int)[-1]
        else:
            count = sum(1 for fn in dir(self) if fn[:10] == 'fnn_euler_' and fn[10:].isdigit())
            answer = "I'm learning to complete the project Euler programming problems. I've not done many so far, I've only done " + str(count) + " of the 434 problems. But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, say 'Hallo Euler {num}' for the answer to challenge number {num}"
        return answer

    def fnn_euler_1(self):
        threes = math.floor(999/3)
        fives = math.floor(999/5)
        fifteens = math.floor(999/15)
        threesum = 3*((0.5*(threes**2))+(0.5*threes))
        fivesum = 5*((0.5*(fives**2))+(0.5*fives))
        fifteensum = 15*((0.5*(fifteens**2))+(0.5*fifteens))
        answer = threesum + fivesum - fifteensum
        return answer

    def fnn_euler_2(self):
        previous_num = 1
        current_num = 2
        answer = 0
        while current_num < 4000000:
            if(current_num % 2 == 0):
                answer = answer + current_num
            new_num = current_num + previous_num
            previous_num = current_num
            current_num = new_num
        return answer

    def fnn_euler_3(self):
        limit = 600851475143
        factorlimit = int(math.floor(math.sqrt(limit)))
        biggestprimefactor = 1
        for i in range(1,factorlimit):
            if(limit%i == 0):
                checkprime = i
                checkprimelimit = int(math.floor(math.sqrt(checkprime)))
                checkprimefactor = 1
                for j in range(1,checkprimelimit):
                    if(checkprime%j == 0):
                        checkprimefactor = j
                if(checkprimefactor == 1):
                    biggestprimefactor = i
        return biggestprimefactor

    def fnn_euler_4(self):
        biggestpalandrome = 0
        biggestpalandromex = 0
        biggestpalandromey = 0
        stoploop = 100
        for x in range(999,100,-1):
            if(x < stoploop):
                break
            for y in range(999,x,-1):
                product = x * y
                reverseproduct = int(str(product)[::-1])
                if(product == reverseproduct and product > biggestpalandrome):
                    biggestpalandrome = product
                    biggestpalandromex = x
                    biggestpalandromey = y
                    stoploop = int(math.floor(biggestpalandrome/999))
        return "answer is: " + str(biggestpalandrome) + " = " + str(biggestpalandromex) + "x" + str(biggestpalandromey)

    def fnn_euler_isprime(self,args):
        checkprime = args
        checkprimefactor = 1
        if(checkprime<=0):
            return False
        for j in range(2,int(math.floor(math.sqrt(checkprime)))+1):
            if(checkprime%j == 0):
                checkprimefactor = j
                break
        if(checkprimefactor == 1):
            return True
        else:
            return False

    def fnn_euler_5(self):
        factors = {}
        maximum = 20
        for num in range(1,maximum+1):
            for x in range(1,num+1):
                if(num%x == 0):
                    if(self.fnn_euler_isprime(x)):
                        if(x not in factors):
                            factors[x] = 1
                        dividescount = 1
                        for attempt in range(1,6):
                            if(num%(x**attempt) == 0):
                                dividescount = attempt
                        if(factors[x] < dividescount):
                            factors[x] = dividescount
        answer = 1
        for prime, power in factors.iteritems():
            answer = answer*(prime**power)
        return answer

    def fnn_euler_6(self):
        answer = 0
        for x in range(1,101):
            answer = answer + x*(0.5*(101**2)-0.5*101) - x**2
        return answer

    def fnn_euler_7(self):
        num_primes = 0
        test = 1
        prime = 1
        while num_primes < 10001:
            test = test + 1
            if(self.fnn_euler_isprime(test)):
                num_primes = num_primes + 1
                prime = test
        return prime

    def fnn_euler_readfiletostring(self,filename):
        f = open(filename,"r")
        return f.read()[:-1]

    def fnn_euler_readfiletolist(self,filename):
        f = open(filename,"r")
        filearray = []
        num_line = 0
        raw_line = f.readline()
        while raw_line != '':
            filearray.append(raw_line.replace("\n",''))
            num_line = num_line + 1
            raw_line = f.readline()
        return filearray

    def fnn_euler_8(self):
        string = self.fnn_euler_readfiletostring("euler_8_string.txt")
        biggestproduct = 0
        while(len(string)>=5):
            substring = string[0:5]
            product = int(substring[0])*int(substring[1])*int(substring[2])*int(substring[3])*int(substring[4])
            biggestproduct = max(product, biggestproduct)
            string = string[1:]
        return biggestproduct

    def fnn_euler_9(self):
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

    def fnn_euler_10(self):
        numbers = [0] * 2000000
        primesum = 2
        for x in range(3,2000000,2):
            if(numbers[x]==0):
                primesum = primesum + x
                for y in range(x,2000000,x):
                    numbers[y] = 1
        return primesum

    def fnn_euler_11(self):
        raw_box = self.fnn_euler_readfiletostring("euler_11_grid.txt")
        arr_box = raw_box.split()
        biggestproduct = 0
        answerx = 0
        answery = 0
        dir = ''
        #vertical checks
        for x in range(0,20):
            for y in range(0,17):
                product = int(arr_box[x+20*y])*int(arr_box[x+20*y+20])*int(arr_box[x+20*y+40])*int(arr_box[x+20*y+60])
                if(product>biggestproduct):
                    biggestproduct = product
                    answerx = x
                    answery = y
                    dir = "vertical"
        #horizontal checks
        for x in range(0,17):
            for y in range(0,20):
                product = int(arr_box[x+20*y])*int(arr_box[x+20*y+1])*int(arr_box[x+20*y+2])*int(arr_box[x+20*y+3])
                if(product>biggestproduct):
                    biggestproduct = product
                    answerx = x
                    answery = y
                    dir = "horizontal"
        #diagonal check \
        for x in range(0,17):
            for y in range(0,17):
                product = int(arr_box[x+20*y])*int(arr_box[x+20*y+21])*int(arr_box[x+20*y+42])*int(arr_box[x+20*y+63])
                if(product>biggestproduct):
                    biggestproduct = product
                    answerx = x
                    answery = y
                    dir = "diagonal \\"
        #diagonal check /
        for x in range(3,20):
            for y in range(0,17):
                product = int(arr_box[x+20*y])*int(arr_box[x+20*y+19])*int(arr_box[x+20*y+38])*int(arr_box[x+20*y+57])
                if(product>biggestproduct):
                    biggestproduct = product
                    answerx = x
                    answery = y
                    dir = "diagonal /"
        return "biggest product is: " + str(biggestproduct) + " the coords are: (" + str(answerx) + "," + str(answery) + ") in the direction: " + dir

    def fnn_euler_factorise(self,args):
        args = int(args)
        factors = []
        for x in range(1,int(math.sqrt(args))+1):
            if(args%x == 0):
                factors.append(x)
                if(args/x!=x):
                    factors.append(args/x)
        return factors

    def fnn_euler_numfactors(self,args):
        args = int(args)
        num_factors = 2
        for x in range(2,int(math.sqrt(args))+1):
            if(args%x == 0):
                num_factors = num_factors + 2
        return num_factors

    def fnn_euler_primefactors(self,args):
        args = int(args)
        factors = []
        notprime = False
        for x in range(2,int(math.sqrt(args))+1):
            if(args%x == 0):
                factors.append(x)
                factors.extend(self.fnn_euler_primefactors(args/x))
                notprime = True
                break
        if(not notprime):
            return [args]
        else:
            return factors

    def fn_primefactors(self,args,client,destination):
        args = int(args)
        prime_factors = self.fnn_euler_primefactors(args)
        return "The prime factors of " + str(args) + " are: " + 'x'.join(str(x) for x in prime_factors)

    def fnn_euler_12(self):
        number = 1
        numfactors = 0
        while numfactors<500:
            number = number + 1
            if(number%2 == 0):
                numfactors = self.fnn_euler_numfactors(number+1)*self.fnn_euler_numfactors(number/2)
            else:
                numfactors = self.fnn_euler_numfactors((number+1)/2)*self.fnn_euler_numfactors(number)
        triangle = ((number+1)*number)/2
        return triangle

    def fnn_euler_13(self):
        arr_numbers = self.fnn_euler_readfiletolist("euler_13_numbers.txt")
        total = 0
        for number in arr_numbers:
            total = total + int(number)
        return str(total)[0:10]

    def fnn_euler_collatz(self,seq):
        num = int(seq[-1])
        if(num==1):
            return seq
        elif(num%2 == 0):
            seq.append(num/2)
            return self.fnn_euler_collatz(seq)
        else:
            seq.append(3*num+1)
            return self.fnn_euler_collatz(seq)

    def fn_hailstone(self,args,client,destination):
        'Returns the hailstone sequence for a given number'
        if(args == "" or not args.isdigit()):
            return "The hailstone function has to be given with a number (to generate the collatz sequence of)"
        else:
            args = int(args)
            sequence = self.fnn_euler_collatz([args])
            return "Hailstone (Collatz) sequence for " + str(args) + ": " + '->'.join(str(x) for x in sequence) + " (" + str(len(sequence)) + " steps)"

    def fnn_euler_14(self):
        lengths = [0] * 1000000
        maxchain = 0
        maxstart = 0
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
                    num = num/2
                    length = length + 1
                else:
                    num = (3*num)+1
                    length = length + 1
            if(maxchain < lengths[start]):
               # print "new longest chain, it starts at: " + str(start) + " and is " + str(lengths[start]) + " steps long. Exploited a " + str(jump) + " step jump! meaning I only had to do " + str(lengths[start]-jump) + " steps myself."
                maxchain = lengths[start]
                maxstart = start
        return maxstart

    def fnn_euler_15(self):
        gridsize = 20
        x = gridsize
        routes = 1
        for y in range(x):
            routes = routes*(x+y+1)/(y+1)
        return routes

    def fnn_euler_16(self):
        bignumber = 2**1000
        bignumber = str(bignumber)
        total = 0
        for x in range(len(bignumber)):
            total = total + int(bignumber[x])
        return total


    def fnn_euler_numberword(self,number,type="american"):
        digits = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
        tens = ['zero','ten','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
        segs = ['','thousand','million','billion','trillion','quadrillion','quintillion','sextillion','septillion','octillion','nonillion','decillion','undecillion','duodecillion','tredecillion']
        europeansegs = ['','thousand','million','milliard','billion','billiard','trillion','trilliard','quadrillion','quadrilliard','quintillion','quintilliard','sextillion','sextilliard','septillion']
        englishsegs = ['','thousand','million','thousand million','billion','thousand billion','trillion','thousand trillion','quadrillion','thousand quadrillion','quintillion','thousand quintillion','sextillion','thousand sextillion','septillion']
        if(number.count('.')>1):
            return "There's too many decimal points in that."
        elif(number.count('.')==1):
            expnumber = number.split('.')
            numberdecimal = expnumber[1]
            number = expnumber[0]
            decimal = " point"
            for num in numberdecimal:
                decimal = decimal + " " + digits[int(num)]
        else:
            decimal = ""
        number = str(number)
        if(number[0]=="-"):
            number = number[1:]
            string = 'negative '
        else:
            string = ''
#check the number is just digits here
        segments = int(math.ceil(float(len(number))/3)+0.01)
        number = number.rjust(3*segments,'0')
        if(number == "000"):
            string = "zero"
        for seg in range(segments):
            start = seg*3
            end = start+3
            segment = number[start:end]
            #string = string + "(" + segment + ")"
            if(segment[0]!="0"):
                string = string + digits[int(segment[0])] + " hundred "
                if(int(segment[1:]) != 0):
                    string = string + "and "
            elif(seg!=0 and int(segment[1:])!=0):
                string = string + "and "
            if(int(segment[1:]) == 0):
                pass
            elif(int(segment[1:]) < 20):
                string = string + digits[int(segment[1:])]
            else:
                string = string + tens[int(segment[1])]
                if(segment[2]!="0"):
                    string = string + "-" + digits[int(segment[2])]
            if(seg!=(segments-1) and segment != "000"):
                if(type.lower() == "american"):
                    string = string + " " + segs[segments-seg-1]
                elif(type.lower() == "english"):
                    string = string + " " + englishsegs[segments-seg-1]
                elif(type.lower() == "european"):
                    string = string + " " + europeansegs[segments-seg-1]
                else:
                    string = string + " " + segs[segments-seg-1]
            if(seg!=(segments-1) and int(number[end:end+3])!=0):
                string = string + ', '
        string = string + decimal
        return string


    def fn_number(self,args,client,destination):
        if(args.count(' ')==0):
            return self.fnn_euler_numberword(args)
        elif(args.split()[1].lower() == "british" or args.split()[1].lower() == "english"):
            return self.fnn_euler_numberword(args.split()[0],"english")
        elif(args.split()[1].lower() == "european" or args.split()[1].lower() == "french"):
            return self.fnn_euler_numberword(args.split()[0],"european")
        else:
            return self.fnn_euler_numberword(args.split()[0])

    def fnn_euler_17(self):
        total = 0
        for x in range(1,1001):
            total = total + len(self.fnn_euler_numberword(x).replace(' ','').replace('-',''))
        return total

    def fnn_euler_18(self):
        arr_triangle = self.fnn_euler_readfiletolist("euler_18_triangle.txt")
        for x in range(len(arr_triangle)):
            arr_triangle[x] = arr_triangle[x].split()
        for row in range(len(arr_triangle)-2,-1,-1):
            for col in range(len(arr_triangle[row])):
                if(int(arr_triangle[row+1][col]) > int(arr_triangle[row+1][col+1])):
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col])
                else:
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col+1])
        return arr_triangle[0][0]

    def fnn_euler_19(self):
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

    def fnn_euler_20(self):
        number = math.factorial(100)
        number = str(number)
        total = 0
        for x in range(len(number)):
            total = total + int(number[x])
        return total

    def fnn_euler_21(self):
        amicable = []
        total = 0
        for x in range(10000):
            if(x not in amicable):
                factors = self.fnn_euler_factorise(x)
                factortotal = 0
                for factor in factors:
                    factortotal = factortotal + factor
                othernumber = factortotal-x
                otherfactors = self.fnn_euler_factorise(othernumber)
                otherfactortotal = 0
                for otherfactor in otherfactors:
                    otherfactortotal = otherfactortotal + otherfactor
                if(otherfactortotal-othernumber==x and othernumber!=x):
                    print "found a pair: " + str(x) + " and " + str(factortotal-x)
                    amicable.append(x)
                    amicable.append(factortotal-x)
                    total = total + x + othernumber
        return total

    def fnn_euler_22(self):
        raw_names = self.fnn_euler_readfiletostring("euler_22_names.txt")
        arr_names = sorted(raw_names.replace('"','').split(','))
        total = 0
        name_num = 0
        for name in arr_names:
            name_num = name_num + 1
            value = 0
            for letter in range(len(name)):
                value = value + ord(name[letter])-64
            score = value * name_num
            total = total + score
        return total

    def fnn_euler_23(self):
        abundantnumbers = []
        sumoftwo = [0] * 28150
        total = (28150/2)*(1+28150)-28150
        for x in range(28150):
            factors = self.fnn_euler_factorise(x)
            factortotal = 0
            for factor in factors:
                factortotal = factortotal + factor
            factortotal = factortotal - x
            if(factortotal>x):
                abundantnumbers.append(x)
                for othernumber in abundantnumbers:
                    sum = othernumber+x
                    if(sum<28150):
                        if(sumoftwo[sum] != 1):
                            sumoftwo[sum] = 1
                            total = total - (sum)
                    else:
                        break
       # total = 0
       # for y in range(len(sumoftwo)):
       #     if(sumoftwo[y]==0):
       #         total = total + y
       # return len(abundantnumbers)
        return total

    def fnn_euler_24(self):
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

    def fnn_euler_25(self):
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

    def fnn_euler_readdecimal(self,fraction):
        fraction = str(fraction)
        if(fraction.count('/')!=1):
            return "This function returns the decimal representation of a fraction, in the form x/y, please provide input in this form"
        else:
            fraction = fraction.split('/')
            fraction[0] = int(fraction[0])
            fraction[1] = int(fraction[1])
            string = str(int(fraction[0]/fraction[1])) + '.'
            decimals = 100
            bignumber = int((fraction[0]*(10**decimals))/fraction[1])
            bignumber = str(bignumber).rjust(decimals,'0')
            string = string + bignumber
            return string

    def fn_readdecimal(self,args,client,destination):
        return self.fnn_euler_readdecimal(args)

    def fnn_euler_removelistitems(self,list,remove):
        newlist = []
        for item in list:
            if(item != remove):
                newlist.append(item)
        return newlist

    def fnn_euler_26(self):
        maxnines = 0
        maxd = 0
        for d in range(1,1000):
            factors = self.fnn_euler_primefactors(d)
            factors = self.fnn_euler_removelistitems(factors,2)
            factors = self.fnn_euler_removelistitems(factors,5)
            product = 1
            for factor in factors:
                product = product*factor
       #     print "d = " + str(d) + ", product = " + str(product)
            nines = 0
            while True:
                nines = (nines * 10) + 9
                if(nines%product==0):
                    if(nines>maxnines):
                        maxnines = nines
                        maxd = d
       #                 print "New record: " + str(d) + " requires " + str(len(str(nines))) + " nines."
                    break
        return maxd

    def fnn_euler_27(self):
        maxlength = 0
        maxproduct = 1
        for b in range(1,1000):
            if(self.fnn_euler_isprime(b)):
                for a in range(1,1000):
                    length = 0
                    n = 0
                    while True:
                        length = length + 1
                        n = n + 1
                        answer = (n**2) + (a*n) + b
                        if not self.fnn_euler_isprime(answer):
                            break
                    if(length>maxlength):
                        maxlength = length
                        maxproduct = a * b
       #                 print "new record: a = " + str(a) + ", b = " + str(b) + ", length = " + str(length)
                    length = 0
                    n = 0
                    if(a<b):
                        while True:
                            length = length + 1
                            n = n + 1
                            answer = (n**2) - (a*n) + b
                            if not self.fnn_euler_isprime(answer):
                                break
                        if(length>maxlength):
                            maxlength = length
                            maxproduct = -(a * b)
       #                     print "new record: a = -" + str(a) + ", b = " + str(b) + ", length = " + str(length)
        return maxproduct

    def fnn_euler_28(self):
        total = 1
        n = 1
        for x in range(1,501):
            gap = x*2
            total = total + 4*n + 10*gap
            n = n + gap*4
        return total

    def fnn_euler_29(self):
        answers = []
        for a in range(2,101):
            afactors = self.fnn_euler_primefactors(a)
       #     answer = a
            for b in range(2,101):
       #         answer = answer * a
                answer = sorted(b * afactors)
                if(answer not in answers):
                    answers.append(answer)
        return len(answers)

    def fnn_euler_30(self):
     #   number = 10
     #   while True:
        digits = [0,1,2,3,4,5,6,7,8,9]
        powerdigits = []
        for digit in range(10):
            powerdigits.append(digit**5)
        total = 0
        for number in range(10,200000):
            strnumber = str(number)
            lennumber = len(strnumber)
            numbertotal = 0
            for x in range(lennumber):
                numbertotal = numbertotal + powerdigits[int(strnumber[x])]
            if(numbertotal==number):
                total = total + number
        return total

    def fnn_euler_change(self,coins,coinnum,amount):
        coinamount = amount/coins[coinnum]
        change = []
        if(amount==0):
            return None
        elif(coinnum==len(coins)-1):
            change.append([coins[coinnum]]*(amount/coins[coinnum]))
        else:
            for x in range(coinamount,-1,-1):
                remaining = amount - x*coins[coinnum]
                if(remaining==0):
                    change.append(x*[coins[coinnum]])
                else:
                    changeadd = self.fnn_euler_change(coins,coinnum+1,remaining)
                    for changeoption in changeadd:
                        change.append(x*[coins[coinnum]]+changeoption)
        return change

    def fnn_euler_changecount(self,coins,coinnum,amount):
        coinamount = amount/coins[coinnum]
        change = 0
        if(amount==0):
            return 0
        elif(coinnum==len(coins)-1):
            change = 1
        else:
            for x in range(coinamount,-1,-1):
                remaining = amount - x*coins[coinnum]
                if(remaining==0):
                    change = change + 1
                else:
                    changeadd = self.fnn_euler_change(coins,coinnum+1,remaining)
                    change = change + changeadd
        return change

    def fn_changeoptions(self,args,client,destination):
        args = int(args)
        coins = [200,100,50,20,10,5,2,1]
        options = self.fnn_euler_change(coins,0,args)
        reply = 'Possible ways to give that change: '
        for option in options:
            reply = reply + '[' + ','.join(str(x) for x in option) + '],'
        return reply

    def fnn_euler_31(self):
        coins = [200,100,50,20,10,5,2,1]
        options = self.fnn_euler_change(coins,0,200)
        numoptions = len(options)
     #   numoptions = self.fnn_euler_changecount(coins,0,200)
        return numoptions

    def fnn_euler_32(self):
        digits = [1,2,3,4,5,6,7,8,9]
        products = []
        for a in range(9):
            adigit = digits[a]
            adigits = digits
            del adigits[a]
            for b in range(8):
                bdigit = adigits[b]
                bdigits = adigits
                del bdigits[b]
                for c in range(7):
                    cdigit = bdigits[c]
                    cdigits = bdigits
                    del cdigits[c]
                    for d in range(6):
                        ddigit = cdigits[d]
                        ddigits = cdigits
                        del ddigits[d]
                        for e in range(5):
                            edigit = ddigits[e]
                            edigits = ddigits
                            del edigits[e]
                            product = (adigit*10+bdigit)*(cdigit*100+ddigit*10+edigit)
                            fail = False
                            for f in range(4):
                                if(edigits[f] not in list(str(product))):
                                    fail = True
                            if(not fail):
                                products.append(product)
        return sum(products)


    def fnn_euler_67(self):
        #this is the same as  problem 18, but bigger file.
        arr_triangle = self.fnn_euler_readfiletolist("euler_67_triangle.txt")
        for x in range(len(arr_triangle)):
            arr_triangle[x] = arr_triangle[x].split()
        for row in range(len(arr_triangle)-2,-1,-1):
            for col in range(len(arr_triangle[row])):
                if(int(arr_triangle[row+1][col]) > int(arr_triangle[row+1][col+1])):
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col])
                else:
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col+1])
        return arr_triangle[0][0]










