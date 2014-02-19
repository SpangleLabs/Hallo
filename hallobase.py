#from euler import eulerclass
#import euler
#from ircbot import ircbot
#import shelve
import random
#import bsddb3 as bsddb
import base64
import urllib.request, urllib.error, urllib.parse
import time
import re
import math
##from PIL import Image
import io
import pickle
import euler
import threading
import json
import difflib
##import psutil

import ircbot_chk


endl = '\r\n'
class hallobase():
    
    def fn_op(self, args, client, destination):
        'Op member in given channel, or current channel if no channel given. Or command user if no member given. Format: op <name> <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.split()
                args[1] = ''.join(args[1:])
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    nick = args[1]
                elif(args[1] in self.comf['server'][destination[0]]['channel']):
                    channel = args[1]
                    nick = args[0]
                else:
                    return 'Multiple arguments given, but neither are a valid channel.'
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' +o ' + nick + endl).encode('utf-8'))
                return 'Op status given to ' + nick + ' in ' + channel + '.'
            elif(args.replace(' ','')!=''):
                if(args[0]=='#'):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +o ' + client + endl).encode('utf-8'))
                    return 'Op status given to you in ' + args + '.'
                else:
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +o ' + args + endl).encode('utf-8'))
                    return 'Op status given to ' + args + '.'
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +o ' + client + endl).encode('utf-8'))
                return 'Op status given.'
        else:
            return 'Insufficient privileges to add op status.'
    
    def fn_deop(self, args, client, destination):
        'Deop member in given channel, or current channel if no channel given. Or command user if no member given. Format: deop <name> <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.split()
                args[1] = ''.join(args[1:])
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    nick = args[1]
                elif(args[1] in self.comf['server'][destination[0]]['channel']):
                    channel = args[1]
                    nick = args[0]
                else:
                    return 'Multiple arguments given, but neither are a valid channel.'
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -o ' + nick + endl).encode('utf-8'))
                return 'Op status taken from ' + nick + ' in ' + channel + '.'
            elif(args.replace(' ','')!=''):
                if(args[0]=='#'):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' -o ' + client + endl).encode('utf-8'))
                    return 'Op status taken from you in ' + args + '.'
                else:
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -o ' + args + endl).encode('utf-8'))
                    return 'Op status taken from ' + args + '.'
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -o ' + client + endl).encode('utf-8'))
                return 'Op status taken.'
        else:
            return 'Insufficient privileges to take op status.'

    def fn_voice(self,args,client,destination):
        'Voice member in given channel, or current channel if no channel given, or command user if no member given. Format: voice <name> <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.split()
                args[1] = ''.join(args[1:])
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    nick = args[1]
                elif(args[1] in self.comf['server'][destination[0]]['channel']):
                    channel = args[1]
                    nick = args[0]
                else:
                    return 'Multiple arguments given, but neither are a valid channel.'
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' +v ' + nick + endl).encode('utf-8'))
                return 'Voice status given to ' + nick + ' in ' + channel + '.'
            elif(args.replace(' ','')!=''):
                if(args[0]=='#'):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +v ' + client + endl).encode('utf-8'))
                    return 'Voice status given to you in ' + args + '.'
                else:
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v ' + args + endl).encode('utf-8'))
                    return 'Voice status given to ' + args + '.'
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v ' + client + endl).encode('utf-8'))
                return 'Voice status given.'
        else:
            return 'Insufficient privileges to add voice status.'

    def fn_devoice(self,args,client,destination):
        'Voice member in given channel, or current channel if no channel given, or command user if no member given. Format: voice <name> <channel>'
        if(len(args.split())>=2):
            args = args.split()
            args[1] = ''.join(args[1:])
            if(args[0] in self.conf['server'][destination[0]]['channel']):
                channel = args[0]
                nick = args[1]
            elif(args[1] in self.comf['server'][destination[0]]['channel']):
                channel = args[1]
                nick = args[0]
            else:
                return 'Multiple arguments given, but neither are a valid channel.'
            if(nick.lower() == client.lower()):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -v ' + nick + endl).encode('utf-8'))
                return 'Voice status remove from ' + nick + ' in ' + channel + '.'
            else:
                if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -v ' + nick + endl).encode('utf-8'))
                    return 'Voice status removed from ' + nick + ' in ' + channel + '.'
                else:
                    return 'Insufficient privileges to remove voice status.'
        elif(args.replace(' ','')!=''):
            if(args[0]=='#'):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' -v ' + client + endl).encode('utf-8'))
                return 'Voice status taken from you in ' + args + '.'
            else:
                if(args.lower() == client.lower()):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + args + endl).encode('utf-8'))
                    return 'Voice status taken from ' + args + '.'
                else:
                    if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + args + endl).encode('utf-8'))
                        return 'Voice status taken from ' + args + '.'
                    else:
                        return 'Insufficient privileges to remove voice status.'
        else:
            self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + client + endl).encode('utf-8'))
            return 'Voice status taken.'

    def fn_roll(self, args, client, destination):
        'Roll X-Y returns a random number between X and Y. Format: "roll <min>-<max>" or "roll <num>d<sides>"'
        if(args.count('-')==1):
            num = args.split('-')
            try:
                ranges = int(num[0])
            except:
                return "Invalid start of range."
            try:
                rangee = int(num[1])
            except:
                return "Invalid end of range."
            if(ranges<rangee):
                rand = random.randint(ranges,rangee)
                return 'I roll ' + str(rand) + '!!!'
            else:
                return 'Smaller number goes first, I bet it was ari or Ripp_ who tried putting them in the other way.'
        elif(args.lower().count('d')==1):
            num = args.lower().split('d')
            try:
                sides = int(num[1])
            except:
                return "Invalid number of sides."
            try:
                dice = int(num[0])
            except:
                return "Invalid number of dice."
            if(dice>100):
                return "Too many dice. Was it beets again messing with that?"
            if(sides>1000000):
                return "At this point, the dice would approximate a sphere."
            if(sides>0 and dice>0):
                if(dice > 1):
                    string = "I roll "
                    total = 0
                    roll = random.randint(1,sides)
                    total = total + roll
                    string = string + str(roll)
                    for x in range(dice-1):
                        roll = random.randint(1,sides)
                        total = total + roll
                        string = string + ", " + str(roll)
                    string = string + ". The total is " + str(total) + "."
                    return string
                elif(dice == 1):
                    return "I roll " + str(random.randint(1,sides)) + '!!!'
                else:
                    return "Integer number of dice, greater than 0, less than or equal to 1, but not equal to 1. How did you do this?"
            else:
                return "You need to roll more than zero dice with more than zero sides. (Was it ari again who did that? or zephyr?)"
        else:
            return "Please give input in the form of X-Y or XdY."

    def fn_choose(self, args, client, destination):
        'Choose X, Y or Z or ... Returns one of the options separated by "or" or a comma. Format: choose <first_option>, <second_option> ... <n-1th option> or <nth option>'
        choices = re.compile(', | or ',re.IGNORECASE).split(args)
        numchoices = len(choices)
        if(numchoices==1):
           return 'Please present me with more than 1 thing to choose from!'
        else:
           rand = random.randint(0,numchoices-1)
           choice = choices[rand]
           return 'I choose "' + choice + '".'

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
        legit_chars = ['0','1','2','3','4','5','6','7','8','9','.','(',')','^','*','x','/','+','-','pi','e']
        stripped = calc
        for legit_char in legit_chars:
            stripped = stripped.replace(legit_char,'')
        if(stripped != ''):
            return 'Error, Invalid characters in expression'
       #make sure openbrackets don't outnumber close
        elif(calc.count('(')>calc.count(')')):
            return 'Error, too many open brackets'
        else:
            return 'Looks good.'

    def fnn_calc_process(self, calc):
      ##constant evaluation
        while calc.count('pi')!=0:
            tempans = math.pi
            if(hallobase.fnn_calc_before(self,calc,'pi') != ''):
                tempans = '*' + str(tempans)
            if(hallobase.fnn_calc_after(self,calc,'pi') != ''):
                tempans = str(tempans) + '*'
            calc = calc.replace('pi',str(tempans))
        while calc.count('e') != 0:
            tempans = math.e
            if(hallobase.fnn_calc_before(self,calc,'e') != ''):
                tempans = '*' + str(tempans)
            if(hallobase.fnn_calc_after(self,calc,'e') != ''):
                tempans = str(tempans) + '*'
            calc = calc.replace('e',str(tempans))
#        del tempans
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
                    tempans = hallobase.fnn_calc_process(self,runncalc)
                    if hallobase.fnn_calc_before(self,calc,'(' + runncalc + ')') != '':
                        tempans = '*' + str(tempans)
                    if hallobase.fnn_calc_after(self,calc,'(' + runncalc + ')') != '':
                        tempans = str(tempans) + '*'
                    calc = calc.replace('(' + runncalc + ')',str(tempans))
                    break
                runncalc = runncalc + nextchar
#        del tempcalc, bracket, runncalc, nextchat, tempans
      ##powers processing
        while calc.count('^') != 0:
            pre_calc = hallobase.fnn_calc_before(self,calc,'^')
            post_calc = hallobase.fnn_calc_after(self,calc,'^')
            calc = calc.replace(str(pre_calc) + '^' + str(post_calc),str(float(pre_calc) ** float(post_calc)))
            del pre_calc, post_calc
      ##powers processing2
        while calc.count('**') != 0:
            pre_calc = hallobase.fnn_calc_before(self,calc,'**')
            post_calc = hallobase.fnn_calc_after(self,calc,'**')
            calc = calc.replace(str(pre_calc) + '**' + str(post_calc),str(float(pre_calc) ** float(post_calc)))
            del pre_calc, post_calc
      ##division processing
        while calc.count('/') != 0:
            pre_calc = hallobase.fnn_calc_before(self,calc,'/')
            post_calc = hallobase.fnn_calc_after(self,calc,'/')
            if float(post_calc) == 0:
                return 'error, no division by zero, sorry.'
            calc = calc.replace(str(pre_calc) + '/' + str(post_calc),str(float(pre_calc) / float(post_calc)))
            del pre_calc, post_calc
      ##multiplication processing
        while calc.count('*') != 0:
            pre_calc = hallobase.fnn_calc_before(self,calc,'*')
            post_calc = hallobase.fnn_calc_after(self,calc,'*')
            calc = calc.replace(str(pre_calc) + '*' + str(post_calc),str(float(pre_calc) * float(post_calc)))
            del pre_calc, post_calc
      ##multiplication processing2
        while calc.count('x') != 0:
            pre_calc = hallobase.fnn_calc_before(self,calc,'x')
            post_calc = hallobase.fnn_calc_after(self,calc,'x')
            calc = calc.replace(str(pre_calc) + 'x' + str(post_calc),str(float(pre_calc) * float(post_calc)))
            del pre_calc, post_calc
      ##addition processing
        calc = calc.replace('-','+-')
        answer = 0
        calc = calc.replace('e+','e')
        for tempans in calc.split('+'):
            if tempans != '':
                answer = answer + float(tempans)
        answer = str(answer)
        if answer[-2:] == '.0':
            answer = answer[:-2]
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
                if(hallobase.fnn_calc_preflight(self,calcpart) == 'Error, Invalid characters in expression'):
                    ansparts.append(calcpart)
                elif(hallobase.fnn_calc_preflight(self,calcpart) == 'Error, too many open brackets'):
                    ansparts.append('{Too many open brackets here}')
                else:
                    calcpart = calcpart.replace(' ','').lower()
                    anspart = hallobase.fnn_calc_process(self,calcpart)
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
            if(hallobase.fnn_calc_preflight(self,calc) == 'Looks good.'):
                answer = hallobase.fnn_calc_process(self,calc)
            else:
                answer = hallobase.fnn_calc_preflight(self,calc)
        return answer + "."

    def fn_boop(self,args,client,destination):
        'Boops people. Format: boop <name>'
        if(args==''):
            return "This function boops people, as such you need to specify a person for me to boop, in the form 'Hallo boop <name>' but without the <> brackets."
        args = args.split()
        if(len(args)>=2):
            if(args[0][0]=='#'):
                online = ''.join(ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],[args[1]]))
                if(online==' ' or online==''):
                    return 'No one called "' + args + '" is online.'
                else:
                    self.base_say('\x01ACTION boops ' + args[1] + '.\x01',[destination[0],args[0]])
                    return 'done.'
            elif(args[1][0]=='#'):
                online = ''.join(ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],[args[0]]))
                if(online==' ' or online==''):
                    return 'No one called "' + args + '" is online.'
                else:
                    self.base_say('\x01ACTION boops ' + args[0] + '.\x01',[destination[0],args[1]])
                    return 'done.'
            else:
                return "Please specify a channel."
        elif(destination[1][0]=='#'):
            online = ''.join(ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],args))
            if(online==' ' or online==''):
                return 'No one called "' + args[0] + '" is online.'
            else:
                return '\x01ACTION boops ' + args[0] + '.\x01'
        else:
            online = ''.join(ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],args))
            if(online==' ' or online==''):
                return 'No one called "' + args[0] + '" is online.'
            else:
                self.base_say('\x01ACTION boops ' + args[0] + '.\x01',[destination[0],args[0]])
                return 'done.'
                
    def fn_eightball(self,args,client,destination):
        'Magic 8 ball. Format: eightball'
        responses = ['It is certain','It is decidedly so','Without a doubt','Yes definitely','You may rely on it','As I see it yes','Most likely','Outlook good','Yes','Signs point to yes','Reply hazy try again','Ask again later','Better not tell you now','Cannot predict now','Concentrate and ask again',"Don't count on it",'My reply is no','My sources say no','Outlook not so good','Very doubtful']
        rand = random.randint(0,len(responses)-1)
        return responses[rand] + "."

    def fn_chosen_one(self,args,client,destination):
        'Specifies who the chosen one is. Format: chosen_one'
        names = ircbot_chk.ircbot_chk.chk_names(self,destination[0],destination[1])
        tempnameslist = names
        nameslist = []
        for name in tempnameslist:
            if('_S' != name and self.conf['server'][destination[0]]['nick'] not in name):
                nameslist.append(name.replace('+','').replace('%','').replace('@','').replace('~','').replace('&',''))
        rand = random.randint(0,len(nameslist)-1)
        return 'It should be obvious by now that ' + nameslist[rand] + ' is the chosen one.'

    def fn_channels(self,args,client,destination):
        'Hallo will tell you which channels he is in, ops only. Format: "channels" for channels on current server, "channels all" for all channels on all servers.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(args.lower()=='all'):
                return "On all servers, I am on these channels: " + ', '.join(server + "-" + channel for server in self.conf['server'] for channel in self.conf['server'][server]['channel'] if self.conf['server'][server]['channel'][channel]['in_channel']) + "."
            else:
                return "On this server, I'm in these channels: " + ', '.join(channel for channel in self.conf['server'][destination[0]]['channel'] if self.conf['server'][destination[0]]['channel'][channel]['in_channel']) + "."
        else:
            return "Sorry, this function is for gods only."

    def fn_am_i_registered(self,args,client,destination):
        'Hallo checks if you are registered, tells you result. Format: am_i_registered'
        if(ircbot_chk.ircbot_chk.chk_userregistered(self,destination[0],client)):
            return "Yup, you are registered."
        else:
            return "It doesn't seem you are registered with nickserv right now."

    def fn_active_threads(self,args,client,destination):
        'Returns current number of active threads.. should probably be gods only, but it is not. Format: active_thread'
        return "I think I have " + str(threading.active_count()) + " active threads right now."

    def fn_in_space(self,args,client,destination):
        'Returns the number of people in space right now, and their names. Format: in_space'
        pagerequest = urllib.request.Request('http://www.howmanypeopleareinspacerightnow.com/space.json')
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageopener = urllib.request.build_opener()
        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read()
        space = json.loads(code.decode('utf-8'))
        return "There are " + str(space['number']) + " people in space right now. Their names are: " + ', '.join(x['name'] for x in space['people']) + "."

    def fn_mute(self,args,client,destination):
        'Mutes a given channel or current channel. Format: mute <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.replace(' ','')
            if(args==''):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +m ' + endl).encode('utf-8'))
                return "Muted the channel."
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +m ' + endl).encode('utf-8'))
                return "Muted " + args + "."
        else:
            return "You have insufficient privileges to use this function."

    def fn_unmute(self,args,client,destination):
        'Unmutes a given channel or current channel if none is given. Format: unmute <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.replace(' ','')
            if(args==''):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -m ' + endl).encode('utf-8'))
                return "Unmuted channel."
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' -m ' + endl).encode('utf-8'))
                return "Unmuted " + args + "."
        else:
            return "You have insufficient privileges to use this function."

    def fn_staff(self,args,client,destination):
        'Sends a message to all online staff members, and posts a message in the staff channel. Format: staff <message>'
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            for admin in ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],self.conf['server'][destination[0]]['admininform']):
                self.base_say(client + ' has sent a message to all staff members. The message is as follows: ' + args,[destination[0],admin])
            self.base_say(client + ' has sent a message to all staff members. The message is as follows: ' + args,[destination[0],'#ukofequestriaircstaff'])
            return "Message delivered. A staff member will be in contact with you shortly. :)"

    def fn_avg(self,args,client,destination):
        'finds the average of a list of numbers. Format: avg <number1> <number2> ... <number n-1> <number n>'
        numberlist = args.split()
        numbersum = sum(float(x) for x in numberlist)
        return "The average of " + ', '.join(numberlist) + " is: " + str(numbersum/float(len(numberlist))) + "."

    def fn_random_cocktail(self,args,client,destination):
        'Delivers ingredients and recipes for a random cocktail. Format: random_cocktail'
        cocktails = pickle.load(open('store/cocktails.p','rb'))
        number = random.randint(0,len(cocktails))
        cocktail = cocktails[number]
        output = "Randomly selected cocktail is: " + cocktail['name'] + " (#" + str(number) + "). The ingredients are: "
        ingredients = []
        for ingredient in cocktail['ingredients']:
            ingredients.append(ingredient[0] + ingredient[1])
        output = output + ", ".join(ingredients) + ". The recipe is: " + cocktail['instructions']
        if(output[-1]!='.'):
            output = output + "."
        return output

    def fn_cocktail(self,args,client,destination):
        'Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>'
        cocktails = pickle.load(open('store/cocktails.p','rb'))
        cocktailnames = []
        for cocktail in cocktails:
            cocktailnames.append(cocktail['name'].lower())
        closest = difflib.get_close_matches(args.lower(),cocktailnames)
        if(len(closest)==0 or closest[0]==''):
            return "I haven't got anything close to that name."
        else:
            for cocktail in cocktails:
                if(cocktail['name'].lower()==closest[0].lower()):
                    break
            ingredients = []
            for ingredient in cocktail['ingredients']:
                ingredients.append(ingredient[0] + ingredient[1])
            if(cocktail['instructions'][-1]!='.'):
                cocktail['instructions'] = cocktail['instructions'] + "."
            return "Closest I have is " + closest[0] + ". The ingredients are: " + ", ".join(ingredients) + ". The recipe is: " + cocktail['instructions']

    def fn_uptime(self,args,client,destination):
        'Returns hardware uptime. Format: uptime'
        uptime = time.time()-psutil.get_boot_time()
        days = math.floor(uptime/86400)
        hours = math.floor((uptime-86400*days)/3600)
        minutes = math.floor((uptime-86400*days-3600*hours)/60)
        seconds = uptime-86400*days-3600*hours-minutes*60
        return "My current (hardware) uptime is " + str(days) + " days, " + str(hours) + " hours, " + str(minutes) + " minutes and " + str(seconds) + " seconds."

    def fn_convert(self,args,client,destination):
        'converts values from one unit to another. Format: convert <value> <old unit> to <new unit>'
        args = args.lower()
        from_to = re.compile(' into | to | in |->',re.IGNORECASE).split(args)
        if(len(from_to)>2):
            return "I'm confused by your input, are you trying to convert between three units? or not provided me something to convert to?"
        valuestr = ''
        for char in from_to[0]:
            if(char in [str(x) for x in range(10)] + ['.']):
                valuestr = valuestr + char
            else:
                break
        from_to[0] = from_to[0][len(valuestr):]
        if(valuestr==''):
            for char in from_to[0][::-1]:
                if(char in [str(x) for x in range(10)] + ['.']):
                    valuestr = char + valuestr
                else:
                    break
            from_to[0] = from_to[0][:len(from_to[0])-len(valuestr)]
            if(valuestr==''):
                valuestr = '1'
        unit_from = from_to[0]
        while(unit_from[0]==' '):
            unit_from = unit_from[1:]
        value = float(valuestr)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Failed to load conversion data."
        if(unit_from.replace(' ','') not in convert['units']):
            if(unit_from.replace(' ','') in convert['alias']):
                unit_from = convert['alias'][unit_from.replace(' ','')]
            else:
                return unit_from + ' is not a recognised unit.'
        unit_from = unit_from.replace(' ','')
        if(len(from_to)<2):
            unit_to = convert['types'][convert['units'][unit_from]['type']]['base_unit']
        else:
            unit_to = from_to[1]
        if(unit_to.replace(' ','') not in convert['units']):
            if(unit_to.replace(' ','') in convert['alias']):
                unit_to = convert['alias'][unit_to.replace(' ','')]
            else:
                return unit_to + ' is not a recognised unit.'
        unit_to = unit_to.replace(' ','')
        if(convert['units'][unit_to]['type'] != convert['units'][unit_from]['type']):
            return 'These units are not of the same type, a conversion cannot be made.'
        result = value*convert['units'][unit_from]['value']/convert['units'][unit_to]['value']
        return str(value) + ' ' + unit_from + ' is ' + str(result) + ' ' + unit_to + "."

    def fn_convert_add_alias(self,args,client,destination):
        'Add a new alias for a conversion unit. Format: convert_add_alias <name> <unit>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.lower().split()
            name_a = args[0]
            name_b = ''.join(args[1:])
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            if(name_a in convert['units']):
                convert['alias'][name_b] = name_a
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Set " + name_b + " as an alias to " + name_a + "."
            elif(name_b in convert['units']):
                convert['alias'][name_a] = name_b
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Set " + name_a + " as an alias to " + name_b + "."
            else:
                return "Neither " + name_a + " nor " + name_b + " seem to be known units."
        else:
            return "You have insufficient privileges to add a conversion alias."

    def fn_convert_del_alias(self,args,client,destination):
        'Delete an alias for a conversion unit. Format: convert_del_alias <alias>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            if(args in convert['alias']):
                del convert['alias'][args]
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Deleted the " + args + " alias."
            else:
                return args + " is not a valid alias."
        else:
            return "You have insufficient privileges to delete a conversion alias."

    def fn_convert_list_alias(self,args,client,destination):
        'List all alaises, or all aliases of a given type if given. Format: convert_list_alias <type>'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args.replace(' ','') == ''):
            return "All conversion aliases: " + ', '.join([alias + '->' + convert['alias'][alias] for alias in convert['alias']]) + "."
        elif(args in convert['types']):
            return args + " conversion aliases: " + ', '.join([alias + '->' + convert['alias'][alias] for alias in convert['alias'] if convert['units'][convert['alias'][alias]]['type'] == args]) + "."
        elif(args in convert['units']):
            return args + " aliases: " + ', '.join([alias + '->' + args for alias in convert['alias'] if convert['alias'][alias] == args]) + "."
        else:
            return args + " is not a valid unit type."

    def fn_convert_add_unit(self,args,client,destination):
        'Add a conversion unit. value in the default for that type. Format: convert_add_unit <type> <name> <value>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            if(len(args.split()) < 3):
                return "Incorrect number of arguments, format is: convert_add_unit {type} {name} {value}."
            args = args.split()
            args[2] = ''.join(args[2:])
            if(args[0] in convert['types']):
                type = args[0]
                del args[0]
            elif(args[1] in convert['types']):
                type = args[1]
                del args[1]
            elif(args[2] in convert['types']):
                type = args[2]
                del args[2]
            else:
                return "Unit type does not seem to be defined."
            try:
                value = float(args[0])
                del args[0]
            except:
                try:
                    value = float(args[1])
                    del args[1]
                except:
                    return "Value does not seem to be defined."
            name = args[0]
            convert['units'][name] = {}
            convert['units'][name]['type'] = type
            convert['units'][name]['value'] = value
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Added " + name + " as a " + type + " unit, with a value of " + str(value) + " " + convert['types'][type]['base_unit'] + "."
        else:
            return "You have insufficient privileges to add a conversion unit."

    def fn_convert_del_unit(self,args,client,destination):
        'Deletes a unit from conversion data, including all alises. Format: convert_del_unit <name>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            if(args in convert['units']):
                del convert['units'][args]
                for alias in convert['alias']:
                    if(convert['alias'][alias] == args):
                        del convert['alias'][alias]
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Deleted " + args + " from conversion data."
            else:
                return args + " is not a valid unit."
        else:
            return "You have insufficient privileges to delete a conversion unit."

    def fn_convert_list_units(self,args,client,destination):
        'Lists all units in conversion data or all units of a type, if given. Format: convert_list_units <type>'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args.replace(' ','') == ''):
            return 'all available units: ' + ', '.join([unit + ' (' + convert['units'][unit]['type'] + ' unit, =' + str(convert['units'][unit]['value']) + convert['types'][convert['units'][unit]['type']]['base_unit'] + ')' for unit in convert['units']]) + "."
        elif(args.split()[0] in convert['types']):
            if(len(args.split())>1 and args.split()[1] == 'simple'):
                return 'Simplified list of ' + args.split()[0] + ' units: ' + ', '.join([unit for unit in convert['units'] if convert['units'][unit]['type'] == args.split()[0]]) + "."
            else:
                return 'List of' + args.split()[0] + ' units: ' + ', '.join([unit + ' (=' + str(convert['units'][unit]['value']) + convert['types'][convert['units'][unit]['type']]['base_unit'] + ')' for unit in convert['units'] if convert['units'][unit]['type'] == args.split()[0]]) + "."
        elif(args == 'simple'):
            return 'Simplified list of available units: ' + ', '.join([unit for unit in convert['units']]) + "."
        else:
            return "Invalid unit type."

    def fn_convert_add_type(self,args,client,destination):
        'Adds a new conversion unit type and base unit. Format: convert_add_type <name> <base_unit>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower().split()
            args[1] = ''.join(args[1:])
            convert['types'][args[0]] = {}
            convert['types'][args[0]]['base_unit'] = args[1]
            convert['units'][args[1]] = {}
            convert['units'][args[1]]['type'] = args[0]
            convert['units'][args[1]]['value'] = 1
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Added " + args[0] + " as a unit type, with " + args[1] + " as the base unit."
        else:
            return "You have insufficient privileges to add a new conversion unit type."

    def fn_convert_del_type(self,args,client,destination):
        'Delete a conversion unit type and all associated units and aliases. Format: convert_del_type <type>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            del convert['types'][args]
            units_list = list(convert['units'])
            for unit in units_list:
                if(convert['units'][unit]['type'] == args):
                    del convert['units'][unit]
                    alias_list = list(convert['alias'])
                    for alias in alias_list:
                        if(convert['alias'][alias] == unit):
                            del convert['alias'][alias]
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Deleted " + type + " unit type and all associated units and aliases."
        else:
            return "You have insufficient privileges to delete a conversion unit type."

    def fn_convert_list_types(self,args,client,destination):
        'Lists conversion unit types. Format: convert_list_types'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args == 'simple'):
            return 'Conversion unit types: ' + ', '.join([type for type in convert['types']]) + "."
        else:
            return 'Conversion unit types: ' + ', '.join([type + ' ( base unit: ' + convert['types'][type]['base_unit'] + ')' for type in convert['types']]) + "."
 
    def fn_convert_default_unit(self,args,client,destination):
        'Returns the default unit for a given type. Format: convert_default_unit <type>'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args not in convert['types']):
            return args + " is not a valid conversion unit type."
        return "The default unit for " + args + " is " + convert['types'][args]['base_unit'] + "."

    def fn_convert_unit_update(self,args,client,destination):
        'Update the value of a conversion unit. Format: convert_unit_update <name> <value>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower().split()
            if(args[0] in convert['units']):
                unit = args[0]
                valuestr = args[1]
            elif(args[1] in convert['units']):
                unit = args[1]
                valuestr = args[0]
            else:
                return "No valid unit given."
            try:
                value = float(valuestr)
            except:
                return "No valid value given."
            convert['units'][unit]['value'] = value
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Value for " + unit + " set to " + str(value) + " " + convert['types'][convert['units'][unit]['type']]['base_unit'] + "."
        else:
            return "You have insufficient privileges to update the value of a conversion unit."

    def fn_say(self,args,client,destination):
        'Say a message into a channel or server/channel pair (in the format "{server,channel}"). Format: say <channel> <message>'
        dest = args.split()[0]
        message = ' '.join(args.split()[1:])
        if(dest[0]=='{' and dest[-1]=='}'):
            dest = dest[1:-1]
            dest_serv = dest.split(',')[0].lower()
            dest_chan = dest.split(',')[1].lower()
        else:
            dest_serv = destination[0].lower()
            dest_chan = dest.lower()
        if(dest_serv.lower() not in self.conf['server']):
            return "I'm not in any server by this name."
        if(dest_chan[0]=='#'):
            if(dest_chan not in self.conf['server'][dest_serv]['channel']):
                return "I'm not in that channel."
            if(ircbot_chk.ircbot_chk.chk_swear(self,dest_serv,dest_chan,message)!=['none','none']):
                return "That message contains a word which is on swearlist for that channel."
        else:
            if(ircbot_chk.ircbot_chk.chk_recipientonline(dest_serv,dest_chan)):
                return "That person isn't online."
        self.base_say(message,[dest_serv,dest_chan])
        return "Message sent."



#convert_currency_update
#-pull currency data from somewhere


