import ircbot_chk
import mod_euler
import math

endl = "\r\n"
class mod_calc:

    def fnn_calc_after(self, calc, sub):
        pos = calc.find(str(sub))
        if len(calc) <= pos+len(sub):
            return ''
        post_calc = calc[pos+len(sub):]
        num = ''
        if(post_calc[0].isdigit() or post_calc[0]=='.' or post_calc[0]=='-'):
            num = num + post_calc[0]
            for nextchar in post_calc[1:]:
                if(nextchar.isdigit() or nextchar == '.'):
                    num = num + nextchar
                else:
                    break
        return num

    def fnn_calc_before(self, calc, sub):
        pos = calc.find(str(sub))
        if pos == 0:
            return ''
        pre_calc = calc[:pos]
        num = ''
        for nextchar in pre_calc[::-1]:
            if(nextchar.isdigit() or nextchar == '.'):
                num = nextchar + num
            else:
                break
        return num

    def fnn_calc_preflight(self, calc):
        ##preflight checks
        #strip brackets
        calc = calc.replace(' ','').lower()
        #make sure only legit characters are allowed
        if(not ircbot_chk.ircbot_chk.chk_msg_calc):
            return 'Error, Invalid characters in expression'
        #make sure openbrackets don't outnumber close
        elif(calc.count('(')>calc.count(')')):
            return 'Error, too many open brackets'
        else:
            return 'Looks good.'

    def fnn_calc_triggy(self,calc,runncalc):
        tempans = mod_calc.fnn_calc_process(self,runncalc)
        runncalc = '('+runncalc+')'
        before = calc.split(runncalc)[0]
        trigdict = [{'name':'acos','func':math.acos},{'name':'asin','func':math.asin},{'name':'atan','func':math.atan},{'name':'cos','func':math.cos},{'name':'sin','func':math.sin},{'name':'tan','func':math.tan},{'name':'sqrt','func':math.sqrt},{'name':'log','func':math.log},{'name':'acosh','func':math.acosh},{'name':'asinh','func':math.asinh},{'name':'atanh','func':math.atanh},{'name':'cosh','func':math.cosh},{'name':'sinh','func':math.sinh},{'name':'tanh','func':math.tanh},{'name':'gamma','func':math.gamma}]
        for trig in trigdict:
            if(before[-len(trig['name']):]==trig['name']):
                return [trig['name']+runncalc,trig['func'](float(tempans))]
        return [runncalc,tempans]

    def fnn_calc_process(self, calc):
        ##constant evaluation
        while calc.count('pi')!=0:
            tempans = math.pi
            if(mod_calc.fnn_calc_before(self,calc,'pi') != ''):
                tempans = '*' + str(tempans)
            if(mod_calc.fnn_calc_after(self,calc,'pi') != ''):
                tempans = str(tempans) + '*'
            calc = calc.replace('pi',str(tempans))
        while calc.count('e') != 0:
            tempans = math.e
            if(mod_calc.fnn_calc_before(self,calc,'e') != ''):
                tempans = '*' + str(tempans)
            if(mod_calc.fnn_calc_after(self,calc,'e') != ''):
                tempans = str(tempans) + '*'
            calc = calc.replace('e',str(tempans))
        #del tempans
        ##bracket processing
        while calc.count('(') != 0:
            tempcalc = calc[calc.find('(')+1:]
            bracket = 1;
            runncalc = ''
            for nextchar in tempcalc:
                if nextchar == '(':
                    bracket += 1 
                elif nextchar == ')':
                    bracket -= 1
                if bracket == 0:
                    #tempans = mod_calc.fnn_calc_process(self,runncalc)
                    #runncalc = '('+runncalc+')'
                    trigcheck = mod_calc.fnn_calc_triggy(self,calc,runncalc)
                    tempans = trigcheck[1]
                    runncalc = trigcheck[0]
                    if mod_calc.fnn_calc_before(self,calc,runncalc) != '':
                        tempans = '*' + str(tempans)
                    if mod_calc.fnn_calc_after(self,calc,runncalc) != '':
                        tempans = str(tempans) + '*'
                    calc = calc.replace(runncalc,str(tempans))
                    break
                runncalc = runncalc + nextchar
        calc = calc.replace(')','')
        #del tempcalc, bracket, runncalc, nextchat, tempans
        ##powers processing
        while calc.count('^') != 0:
            pre_calc = mod_calc.fnn_calc_before(self,calc,'^')
            post_calc = mod_calc.fnn_calc_after(self,calc,'^')
            calc = calc.replace(str(pre_calc) + '^' + str(post_calc),str(float(pre_calc) ** float(post_calc)))
            del pre_calc, post_calc
        ##powers processing2
        while calc.count('**') != 0:
            pre_calc = mod_calc.fnn_calc_before(self,calc,'**')
            post_calc = mod_calc.fnn_calc_after(self,calc,'**')
            calc = calc.replace(str(pre_calc) + '**' + str(post_calc),str(float(pre_calc) ** float(post_calc)))
            del pre_calc, post_calc
        ##modulo processing
        while calc.count('%') != 0:
            pre_calc = mod_calc.fnn_calc_before(self,calc,'%')
            post_calc = mod_calc.fnn_calc_after(self,calc,'%')
            if float(post_calc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(pre_calc) + '%' + str(post_calc),str(float(pre_calc) % float(post_calc)))
            del pre_calc, post_calc
        ##multiplication processing
        while calc.count('/') != 0:
            pre_calc = mod_calc.fnn_calc_before(self,calc,'/')
            post_calc = mod_calc.fnn_calc_after(self,calc,'/')
            if float(post_calc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(pre_calc) + '/' + str(post_calc),str(float(pre_calc) / float(post_calc)))
            del pre_calc, post_calc
        ##multiplication processing
        while calc.count('*') != 0:
            pre_calc = mod_calc.fnn_calc_before(self,calc,'*')
            post_calc = mod_calc.fnn_calc_after(self,calc,'*')
            calc = calc.replace(str(pre_calc) + '*' + str(post_calc),str(float(pre_calc) * float(post_calc)))
            del pre_calc, post_calc
        ##multiplication processing2
        while calc.count('x') != 0:
            pre_calc = mod_calc.fnn_calc_before(self,calc,'x')
            post_calc = mod_calc.fnn_calc_after(self,calc,'x')
            calc = calc.replace(str(pre_calc) + 'x' + str(post_calc),str(float(pre_calc) * float(post_calc)))
            del pre_calc, post_calc
        ##addition processing
        calc = calc.replace('-','+-')
        answer = 0
        calc = calc.replace('e+','e')
        for tempans in calc.split('+'):
            if tempans != '':
                answer = answer + float(tempans)
        answer = '{0:.10f}'.format(answer)
        if('.' in answer):
            while(answer[-1]=='0'):
                answer = answer[:-1]
        if answer[-1] == '.':
            answer = answer[:-1]
        return answer

    def fn_calc(self, args, client, destination):
        'Calculate function, calculates the answer to mathematical expressions using custom built python scripts. Format: calc <calculation>'
        calc = args
        answer = 0
        ##check for equals signs
        if(calc.count('=')>=1):
            calcparts = calc.split('=')
            ansparts = []
            number_ans = []
            num_calcs = 0
            for calcpart in calcparts:
                #run preflight checks, if it passes do the calculation, if it doesn't return the same text.
                if(mod_calc.fnn_calc_preflight(self,calcpart) == 'Error, Invalid characters in expression'):
                    ansparts.append(calcpart)
                elif(mod_calc.fnn_calc_preflight(self,calcpart) == 'Error, too many open brackets'):
                    ansparts.append('{Too many open brackets here}')
                else:
                    calcpart = calcpart.replace(' ','').lower()
                    anspart = mod_calc.fnn_calc_process(self,calcpart)
                    ansparts.append(anspart)
                    number_ans.append(anspart)
                    num_calcs = num_calcs + 1
            answer = '='.join(ansparts)
            if(num_calcs > 1):
                seems_legit = True
                lastnumber = number_ans[0]
                for number in number_ans[1:]:
                    if(number!=lastnumber):
                        seems_legit = False
                        break
                    lastnumber = number
                if(seems_legit is False):
                    answer = answer + endl + "Wait, that's not right..."
        else:
            calc = calc.replace(' ','').lower()
            if(mod_calc.fnn_calc_preflight(self,calc) == 'Looks good.'):
                answer = mod_calc.fnn_calc_process(self,calc)
            else:
                answer = mod_calc.fnn_calc_preflight(self,calc)
        return answer + "."

    def fn_average(self,args,client,destination):
        'finds the average of a list of numbers. Format: avg <number1> <number2> ... <number n-1> <number n>'
        numberlist = args.split()
        numbersum = sum(float(x) for x in numberlist)
        return "The average of " + ', '.join(numberlist) + " is: " + str(numbersum/float(len(numberlist))) + "."

    def fn_number(self,args,client,destination):
        'Returns the textual representation of a given number. Format: number <number>'
        if(args.count(' ')==0):
            number = args
            lang = "american"
        elif(args.split()[1].lower() == "british" or args.split()[1].lower() == "english"):
            number = args.split()[0]
            lang = "english"
        elif(args.split()[1].lower() == "european" or args.split()[1].lower() == "french"):
            number = args.split()[0]
            lang = "european"
        else:
            number = args.split()[0]
            lang = "american"
        if(ircbot_chk.ircbot_chk.chk_msg_numbers(self,number)):
            number = number
        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,number)):
            number = mod_calc.fn_calc(self,number,client,destination)
            if(str(number)[-1]=='.'):
                number = number[:-1]
        else:
            return "You must enter a valid number or calculation."
        return mod_euler.mod_euler.fnn_euler_numberword(self,number,lang) + "."

    def fn_highest_common_factor(self,args,client,destination):
        'Returns the highest common factor of two numbers. Format: highest_common_factor <number1> <number2>'
        if(len(args.split())!=2):
            return "You must provide two arguments."
        numberone = args.split()[0]
        numbertwo = args.split()[1]
        if(not ircbot_chk.ircbot_chk.chk_msg_numbers(self,numberone)):
            return "Both arguments must be integers."
        if(not ircbot_chk.ircbot_chk.chk_msg_numbers(self,numbertwo)):
            return "Both arguments must be integers."
        numberone_factors = mod_euler.mod_euler.fnn_euler_primefactors(self,int(numberone))
        numbertwo_factors = mod_euler.mod_euler.fnn_euler_primefactors(self,int(numbertwo))
        common_factors = mod_euler.mod_euler.fnn_intersection(self,numberone_factors,numbertwo_factors)
        hcf = mod_euler.mod_euler.fnn_product(self,common_factors)
        return "The highest common factor of " + numberone + " and " + numbertwo + " is " + str(hcf) + "."

    def fn_simplify_fraction(self,args,client,destination):
        'Returns a fraction in its simplest form. simplify_fraction <numerator>/<denominator>'
        #preflight checks please
        numerator = args.split('/')[0]
        denominator = args.split('/')[1]
        if(not ircbot_chk.ircbot_chk.chk_msg_numbers(self,numerator)):
            return "Numerator must be an integer."
        if(not ircbot_chk.ircbot_chk.chk_msg_numbers(self,denominator)):
            return "Denominator must be an integer."
        numerator_factors = mod_euler.mod_euler.fnn_euler_primefactors(self,int(numerator))
        denominator_factors = mod_euler.mod_euler.fnn_euler_primefactors(self,int(denominator))
        numerator_factors_new = mod_euler.mod_euler.fnn_listminus(self,numerator_factors,mod_euler.mod_euler.fnn_intersection(self,denominator_factors,numerator_factors))
        denominator_factors_new = mod_euler.mod_euler.fnn_listminus(self,denominator_factors,mod_euler.mod_euler.fnn_intersection(self,denominator_factors,numerator_factors))
        numerator_new = mod_euler.mod_euler.fnn_product(self,numerator_factors_new)
        denominator_new = mod_euler.mod_euler.fnn_product(self,denominator_factors_new)
        return numerator + "/" + denominator + " = " + str(numerator_new) + "/" + str(denominator_new) + "."
