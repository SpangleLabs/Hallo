import math
import collections

import ircbot_chk
import mod_calc

class mod_euler:
    def fn_euler(self, args, client, destination):
        'Project Euler functions. Format: "euler list" to list project euler solutions. "euler <number>" for the solution to project euler problem of the given number.'
        if(args.replace(' ','').isdigit()):
            #try and do that euler function command
            if(hasattr(mod_euler,'fnn_euler_' + args) and isinstance(getattr(mod_euler,'fnn_euler_' + args), collections.Callable)):
                eulerfunc = getattr(mod_euler,'fnn_euler_' + args)
                if(hasattr(eulerfunc, '__call__')):
                    try:
                        answer = "Euler project problem " + args + "? I think the answer is: " + str(eulerfunc(self)) + "."
                    except Exception as e:
                        answer = "hmm, seems that one doesn't work... darnit."
                        print("EULER ERROR: " + str(e))
                else:
                    answer = "That doesn't seem to work."
            else:
                answer = "I don't think I've solved that one yet."
        elif(args.replace(' ','').lower() == 'list'):
            #list all available project Euler answers
            problem_funcs = []
            for fn in dir(mod_euler):
                if(fn[:10] == 'fnn_euler_' and fn[10:].isdigit()):
                    problem_funcs.append(fn[10:])
            answer = "Currently I can do Project Euler problems " + ', '.join(sorted(problem_funcs,key=int)[:-1]) + " and " + sorted(problem_funcs,key=int)[-1] + '.'
        else:
            count = sum(1 for fn in dir(mod_euler) if fn[:10] == 'fnn_euler_' and fn[10:].isdigit())
            answer = "I'm learning to complete the project Euler programming problems. I've not done many so far, I've only done " + str(count) + " of the 434 problems. But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, say 'Hallo Euler {num}' for the answer to challenge number {num}."
        return answer

    def fnn_euler_isprime(self,args):
        checkprime = args
        checkprimefactor = 1
        if(checkprime<=0):
            return False
        for j in range(2,int(math.floor(math.sqrt(checkprime)))+1):
            if(checkprime%j == 0):
                checkprimefactor = j
                break
        if(checkprimefactor == 1 and args!=1):
            return True
        else:
            return False

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
                factors.extend(mod_euler.fnn_euler_primefactors(self,args//x))
                notprime = True
                break
        if(not notprime):
            return [args]
        else:
            return factors

    def fn_prime_factors(self,args,client,destination):
        'Returns the prime factors of a given number. Format: prime_factors <number>'
        if(ircbot_chk.ircbot_chk.chk_msg_numbers(self,args)):
            args = int(args)
        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,args)):
            args = mod_calc.mod_calc.fn_calc(self,args,client,destination)
            if(str(args)[-1]=='.'):
                args = args[:-1]
            args = int(args)
        else:
            return "This is not a valid number or calculation."
        prime_factors = mod_euler.fnn_euler_primefactors(self,args)
        return "The prime factors of " + str(args) + " are: " + 'x'.join(str(x) for x in prime_factors) + "."

    def fnn_euler_21(self):
        amicable = []
        total = 0
        for x in range(10000):
            if(x not in amicable):
                factors = mod_euler.fnn_euler_factorise(self,x)
                factortotal = 0
                for factor in factors:
                    factortotal = factortotal + factor
                othernumber = factortotal-x
                otherfactors = mod_euler.fnn_euler_factorise(self,othernumber)
                otherfactortotal = 0
                for otherfactor in otherfactors:
                    otherfactortotal = otherfactortotal + otherfactor
                if(otherfactortotal-othernumber==x and othernumber!=x):
                    print("found a pair: " + str(x) + " and " + str(factortotal-x))
                    amicable.append(x)
                    amicable.append(factortotal-x)
                    total = total + x + othernumber
        return total

    def fnn_euler_22(self):
        raw_names = mod_euler.fnn_euler_readfiletostring(self,"euler/euler_22_names.txt")
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
            factors = mod_euler.fnn_euler_factorise(self,x)
            factortotal = 0
            for factor in factors:
                factortotal = factortotal + factor
            factortotal = factortotal - x
            if(factortotal>x):
                abundantnumbers.append(x)
                for othernumber in abundantnumbers:
                    ab_sum = othernumber+x
                    if(ab_sum<28150):
                        if(sumoftwo[ab_sum] != 1):
                            sumoftwo[ab_sum] = 1
                            total = total - (ab_sum)
                    else:
                        break
#        total = 0
#        for y in range(len(sumoftwo)):
#            if(sumoftwo[y]==0):
#                total = total + y
#        return len(abundantnumbers)
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

    def fnn_euler_removelistitems(self,list_in,remove):
        newlist = []
        for item in list_in:
            if(item != remove):
                newlist.append(item)
        return newlist

    def fnn_euler_26(self):
        maxnines = 0
        maxd = 0
        for d in range(1,1000):
            factors = mod_euler.fnn_euler_primefactors(self,d)
            factors = mod_euler.fnn_euler_removelistitems(self,factors,2)
            factors = mod_euler.fnn_euler_removelistitems(self,factors,5)
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

    def fnn_euler_27(self):
        maxlength = 0
        maxproduct = 1
        for b in range(1,1000):
            if(mod_euler.fnn_euler_isprime(self,b)):
                for a in range(1,1000):
                    length = 0
                    n = 0
                    while True:
                        length = length + 1
                        n = n + 1
                        answer = (n**2) + (a*n) + b
                        if not mod_euler.fnn_euler_isprime(self,answer):
                            break
                    if(length>maxlength):
                        maxlength = length
                        maxproduct = a * b
#                        print "new record: a = " + str(a) + ", b = " + str(b) + ", length = " + str(length)
                    length = 0
                    n = 0
                    if(a<b):
                        while True:
                            length = length + 1
                            n = n + 1
                            answer = (n**2) - (a*n) + b
                            if not mod_euler.fnn_euler_isprime(self,answer):
                                break
                        if(length>maxlength):
                            maxlength = length
                            maxproduct = -(a * b)
#                            print "new record: a = -" + str(a) + ", b = " + str(b) + ", length = " + str(length)
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
            afactors = mod_euler.fnn_euler_primefactors(self,a)
#            answer = a
            for b in range(2,101):
#                answer = answer * a
                answer = sorted(b * afactors)
                if(answer not in answers):
                    answers.append(answer)
        return len(answers)

    def fnn_euler_30(self):
#        number = 10
#        while True:
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
        coinamount = amount//coins[coinnum]
        change = []
        if(amount==0):
            return None
        elif(coinnum==len(coins)-1):
            change.append([coins[coinnum]]*(amount//coins[coinnum]))
        else:
            for x in range(coinamount,-1,-1):
                remaining = amount - x*coins[coinnum]
                if(remaining==0):
                    change.append(x*[coins[coinnum]])
                else:
                    changeadd = mod_euler.fnn_euler_change(self,coins,coinnum+1,remaining)
                    for changeoption in changeadd:
                        change.append(x*[coins[coinnum]]+changeoption)
        return change

    def fnn_euler_changecount(self,coins,coinnum,amount):
        coinamount = amount//coins[coinnum]
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
                    changeadd = mod_euler.fnn_euler_change(self,coins,coinnum+1,remaining)
                    change = change + changeadd
        return change

    def fn_change_options(self,args,client,destination):
        'Returns the number of ways to give change for a given amount (in pence, using british coins.) Format: change_options <number>'
        args = int(args)
        coins = [200,100,50,20,10,5,2,1]
        options = mod_euler.fnn_euler_change(self,coins,0,args)
        reply = 'Possible ways to give that change: '
        for option in options:
            reply = reply + '[' + ','.join(str(x) for x in option) + '],'
        return reply + "."

    def fnn_euler_31(self):
        coins = [200,100,50,20,10,5,2,1]
        options = mod_euler.fnn_euler_change(self,coins,0,200)
        numoptions = len(options)
#        numoptions = euler.fnn_euler_changecount(self,coins,0,200)
        return numoptions

    def fnn_euler_32(self):
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
                            productone = (adigit*10+bdigit)*(cdigit*100+ddigit*10+edigit)
                            producttwo = adigit*(bdigit*1000+cdigit*100+ddigit*10+edigit)
                            failone = False
                            failtwo = False
                            for f in range(4):
                                if(str(edigits[f]) not in list(str(productone)) or productone>9999):
                                    failone = True
                            for g in range(4):
                                if(str(edigits[g]) not in list(str(producttwo)) or producttwo<1000 or producttwo>9999):
                                    failtwo = True
                            if(not failone):
                                print(str(adigit)+str(bdigit)+"*"+str(cdigit)+str(ddigit)+str(edigit)+"="+str(productone))
                                products.append(productone)
                            if(not failtwo):
                                print(str(adigit)+"*"+str(bdigit)+str(cdigit)+str(ddigit)+str(edigit)+"="+str(producttwo))
                                products.append(producttwo)
        products = list(set(products))
        return sum(products)

    def fnn_product(self,list_in):
        product = 1
        for number in list_in:
            product = product*number
        return product

    def fnn_intersection(self,listone,listtwo):
        intersection = []
        templist = list(listtwo)
        for x in listone:
            if(x in templist):
                intersection.append(x)
                templist.remove(x)
        return intersection

    def fnn_listminus(self,listone,listtwo):
        listminus = list(listone)
        for x in listtwo:
            if(x in listminus):
                listminus.remove(x)
        return listminus

    def fnn_listinlist(self,listsmall,listbig):
        listtest = list(listbig)
        for x in listsmall:
            if(x in listtest):
                listtest.remove(x)
            else:
                return False
        return True

    def fnn_euler_33(self):
        epsilon = 0.0000001
        total_numerator_factors = []
        total_denominator_factors = []
        for denominator in range(11,100):
            for numerator in range(10,denominator):
                if(str(numerator)[0] in str(denominator)):
                    if(str(denominator)[0]==str(denominator)[1]):
                        denominator_new = int(str(denominator)[1])
                    else:
                        denominator_new = int(str(denominator).replace(str(numerator)[0],''))
                    numerator_new = int(str(numerator)[1])
                    numerator_factors_new = mod_euler.fnn_euler_primefactors(self,numerator_new)
                    denominator_factors_new = mod_euler.fnn_euler_primefactors(self,denominator_new)
                    if(denominator_new!=0):
                        if((numerator/denominator-numerator_new/denominator_new)**2<epsilon):
                            print("found one." + str(numerator) + "/" + str(denominator))
                            total_numerator_factors = total_numerator_factors + numerator_factors_new
                            total_denominator_factors = total_denominator_factors + denominator_factors_new
                elif(str(numerator)[1] in str(denominator) and str(numerator)[1] != "0"):
                    if(str(denominator)[0]==str(denominator)[1]):
                        denominator_new = int(str(denominator)[1])
                    else:
                        denominator_new = int(str(denominator).replace(str(numerator)[1],''))
                    numerator_new = int(str(numerator)[0])
                    numerator_factors_new = mod_euler.fnn_euler_primefactors(self,numerator_new)
                    denominator_factors_new = mod_euler.fnn_euler_primefactors(self,denominator_new)
                    if(denominator_new!=0):
                        if((numerator/denominator-numerator_new/denominator_new)**2<epsilon):
                            print("found one." + str(numerator) + "/" + str(denominator))
                            total_numerator_factors = total_numerator_factors + numerator_factors_new
                            total_denominator_factors = total_denominator_factors + denominator_factors_new
        total_denominator_factors_new = mod_euler.fnn_listminus(self,total_denominator_factors,mod_euler.fnn_intersection(self,total_denominator_factors,total_numerator_factors))
        total_denominator_new = mod_euler.fnn_product(self,total_denominator_factors_new)
        return total_denominator_new
 
    def fnn_euler_34(self):
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

    def fnn_euler_35(self):
        number = 0
        for x in range(10**6):
            prime = True
            strx = str(x)
            for digit in range(len(strx)):
                rotatex = strx[digit:] + strx[:digit]
                prime = prime and mod_euler.fnn_euler_isprime(self,int(rotatex))
            if(prime):
                number += 1
                print(x)
        return number

    def fnn_ispalindrome(self,args):
        if(args==args[::-1]):
            return True
        else:
            return False

    def fnn_euler_36(self):
        total = 0
        for a in range(10**6):
            if(mod_euler.fnn_ispalindrome(self,str(a))):
                binary = bin(a)[2:]
                if(mod_euler.fnn_ispalindrome(self,binary)):
                    total += a
        return total

    def fnn_euler_37(self):
        total = 0
        num_found = 0
        number = 10
        while num_found<11 and number<10**7:
            strnumber = str(number)
            truncatable = True
            for x in range(len(strnumber)):
                truncatable = truncatable and mod_euler.fnn_euler_isprime(self,int(strnumber[x:]))
                truncatable = truncatable and mod_euler.fnn_euler_isprime(self,int(strnumber[:len(strnumber)-x]))
            if(truncatable):
                print('found one. ' + strnumber)
                num_found += 1
                total += number
            number += 1
        return total

    def fnn_euler_38(self):
        max_constr = 0
        for x in range(10**5):
            constr = ''
            n = 1
            while len(constr)<9:
                constr = constr + str(x*n)
                n += 1
            if(len(constr)==9 and int(constr)>max_constr):
                if(mod_euler.fnn_listinlist(self,[str(x) for x in list(range(1,10))],list(constr))):
                    print('new max: ' + constr)
                    max_constr = int(constr)
        return max_constr

    def fnn_euler_39(self):
        epsilon = 0.00000001
        max_p = 0
        max_p_count = 0
        for p in range(1,1001):
            p_count = 0
            p_list = []
            for a in range(1,int(p/2)):
                b = (p*p-2*p*a)/(2*(a-p))
                c = (a*a+b*b)**0.5
                if(b%1<epsilon and c%1<epsilon):
                    p_count += 1
                    p_list.append([int(a),int(b),int(c)])
            if(p_count>max_p_count):
                max_p = p
                max_p_count = p_count
        return "Maximum triangles for given perimeter is " + str(max_p_count) + " for the perimeter of " + str(max_p) + "."

    def fnn_euler_40(self):
        stringlength = 0
        product = 1
        for number in range(1,10**6):
            addlength = len(str(number))
            if(stringlength<1<=stringlength+addlength):
                print('digit is ' + str(number)[1-stringlength-1])
                product = product*int(str(number)[1-stringlength-1])
            if(stringlength<10<=stringlength+addlength):
                print('digit is ' + str(number)[10-stringlength-1])
                product = product*int(str(number)[10-stringlength-1])
            if(stringlength<100<=stringlength+addlength):
                print('digit is ' + str(number)[100-stringlength-1])
                product = product*int(str(number)[100-stringlength-1])
            if(stringlength<1000<=stringlength+addlength):
                print('digit is ' + str(number)[1000-stringlength-1])
                product = product*int(str(number)[1000-stringlength-1])
            if(stringlength<10000<=stringlength+addlength):
                print('digit is ' + str(number)[10000-stringlength-1])
                product = product*int(str(number)[10000-stringlength-1])
            if(stringlength<100000<=stringlength+addlength):
                print('digit is ' + str(number)[100000-stringlength-1])
                product = product*int(str(number)[100000-stringlength-1])
            if(stringlength<1000000<=stringlength+addlength):
                print('digit is ' + str(number)[1000000-stringlength-1])
                product = product*int(str(number)[1000000-stringlength-1])
            stringlength += addlength
        return product

    def fnn_euler_41(self):
        max_pandigitalprime = 1
        for x in range(2,8*10**6):
            digits = len(str(x))
            if(x%2!=0 and x%3!=0 and x%5!=0):
                if(mod_euler.fnn_listinlist(self,[str(x) for x in range(1,digits+1)],list(str(x)))):
                    if(mod_euler.fnn_euler_isprime(self,x)):
                        print('this is one. ' + str(x))
                        max_pandigitalprime = x
        return max_pandigitalprime

    def fnn_euler_wordvalue(self,word):
        value = 0
        word = word.upper()
        for char in word:
            value += ord(char)-64
        return value
        
    def fnn_euler_42(self):
        filestring = mod_euler.fnn_euler_readfiletostring(self,'euler/euler_42_words.txt')
        words = [word.replace('"','') for word in filestring.split(',')]
        longestword = max(words,key=len)
        triangles = []
        count = 0
        x = 1
        while (0.5*x*(x+1)) < 26*len(longestword):
            triangles.append(0.5*x*(x+1))
            x += 1
        for word in words:
            if(mod_euler.fnn_euler_wordvalue(self,word) in triangles):
                print('found a triangle word: ' + word)
                count += 1
        return count
        

    def fnn_euler_pandigitals(self):
        pandigitals = []
        digits = list(range(10))
        for a in range(9):
            adigit = digits[a+1]
            adigits = list(digits)
            del adigits[a+1]
            for b in range(9):
                bdigit = adigits[b]
                bdigits = list(adigits)
                del bdigits[b]
                for c in range(8):
                    cdigit = bdigits[c]
                    cdigits = list(bdigits)
                    del cdigits[c]
                    for d in range(7):
                        ddigit = cdigits[d]
                        ddigits = list(cdigits)
                        del ddigits[d]
                        for e in range(6):
                            edigit = ddigits[e]
                            edigits = list(ddigits)
                            del edigits[e]
                            for f in range(5):
                                fdigit = edigits[f]
                                fdigits = list(edigits)
                                del fdigits[f]
                                for g in range(4):
                                    gdigit = fdigits[g]
                                    gdigits = list(fdigits)
                                    del gdigits[g]
                                    for h in range(3):
                                        hdigit = gdigits[h]
                                        hdigits = list(gdigits)
                                        del hdigits[h]
                                        for i in range(2):
                                            idigit = hdigits[i]
                                            idigits = list(hdigits)
                                            del idigits[i]
                                            jdigit = idigits[0]
                                            pandigitals.append(1000000000*adigit+100000000*bdigit+10000000*cdigit+1000000*ddigit+100000*edigit+10000*fdigit+1000*gdigit+100*hdigit+10*idigit+jdigit)
        return pandigitals

    def fnn_euler_43(self):
        pandigitals = mod_euler.fnn_euler_pandigitals(self)
        pandigital_sum = 0
        for pandigital in pandigitals:
            if(int(str(pandigital)[1:4])%2==0 and int(str(pandigital)[2:5])%3==0 and int(str(pandigital)[3:6])%5==0 and int(str(pandigital)[4:7])%7==0 and int(str(pandigital)[5:8])%11==0):
                if(int(str(pandigital)[6:9])%13==0 and int(str(pandigital)[7:10])%17==0):
                    print('found one: ' + str(pandigital))
                    pandigital_sum += pandigital
        return pandigital_sum

    def fnn_euler_44(self):
        epsilon = 0.000001
        pentagonals = [0,1]
        smallest_diff = 10**9
        for x in range(2,3000):
            pentagonals.append(int(x*(3*x-1)/2))
            for y in range(1,x):
                pentagonal_sum = pentagonals[x] + pentagonals[y]
                diff = pentagonals[x] - pentagonals[y]
                sumpent = (1+(1+24*pentagonal_sum)**0.5)/6
                diffpent = (1+(1+24*diff)**0.5)/6
                if(sumpent%1<epsilon and diffpent%1<epsilon):
                    print('found one.')
                    if(diff<smallest_diff):
                        smallest_diff = diff
        return smallest_diff

    def fnn_euler_45(self):
        epsilon = 0.0000001
        tripenthex = 0
        for x in range(40756,10**9):
            xtri = (-1+(1+8*x)**0.5)/2
            if(xtri%1<epsilon):
                xpent = (1+(1+24*x)**0.5)/6
                if(xpent%1<epsilon):
                    xhex = (1+(1+8*x)**0.5)/4
                    if(xhex%1<epsilon):
                        print('found it.')
                        tripenthex = x
                        break
        return tripenthex



    def fnn_euler_67(self):
        #this is the same as  problem 18, but bigger file.
        arr_triangle = mod_euler.fnn_euler_readfiletolist(self,"euler/euler_67_triangle.txt")
        for x in range(len(arr_triangle)):
            arr_triangle[x] = arr_triangle[x].split()
        for row in range(len(arr_triangle)-2,-1,-1):
            for col in range(len(arr_triangle[row])):
                if(int(arr_triangle[row+1][col]) > int(arr_triangle[row+1][col+1])):
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col])
                else:
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col+1])
        return arr_triangle[0][0]










