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
from PIL import Image
import io
import pickle
#from megahal/megahal import *
import euler
import threading
import json
import difflib

#Importing greetings
#try:
#    hallodata = shelve.open('Store/hallo-greetings')
#except ImportError:
#    import bsddb3
#    _db = bsddb3.hashopen('Store/hallo-greetings')
#    hallodata = shelve.Shelf(_db)

#Importing lists
#try:
#    hallolists = shelve.open('Store/hallo-lists')
#except ImportError:
#    import bsddb3
#    _db = bsddb3.hashopen('Store/hallo-lists')
#    hallolists = shelve.Shelf(_db)

endl = '\r\n'
#class hallo(euler,ircbot):
class hallobase():
    def init(self):
        self.longcat = False
#        import euler
    
    def fn_kick(self, args, client, destination):
        'Kick given user in given channel, or current channel if no channel given.'
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=2):
                user = args.split()[0]
                channel = ''.join(args.split()[1:])
                self.core['server'][destination[0]]['socket'].send(('KICK ' + channel + ' ' + user + endl).encode('utf-8'))
                return 'Kicked ' + user + ' from ' + channel + '.'
            elif(args.replace(' ','')!=''):
                args = args.replace(' ','')
                self.core['server'][destination[0]]['socket'].send(('KICK ' + channel + ' ' + args + endl).encode('utf-8'))
                return 'Kicked ' + args + '.'
            else:
                return 'Please, tell me who to kick.'
        else:
            return 'Insufficient privileges to kick.'
    

    def fn_op(self, args, client, destination):
        'Op member in given channel, or current channel if no channel given. Or command user if no member given. Format: op <name> <channel>'
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=2):
                nick = args.split()[0]
                channel = ''.join(args.split()[1:])
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
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=2):
                nick = args.split()[0]
                channel = ''.join(args.split()[1:])
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
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=2):
                nick = args.split()[0]
                channel = ''.join(args.split()[1:])
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
            nick = args.split()[0]
            channel = ''.join(args.split()[1:])
            if(nick.lower() == client.lower()):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -v ' + nick + endl).encode('utf-8'))
                return 'Voice status remove from ' + nick + ' in ' + channel + '.'
            else:
                if(self.chk_op(destination[0],client)):
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
                    if(self.chk_op(destination[0],client)):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + args + endl).encode('utf-8'))
                        return 'Voice status taken from ' + args + '.'
                    else:
                        return 'Insufficient privileges to remove voice status'
        else:
            self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + client + endl).encode('utf-8'))
            return 'Voice status taken.'

    def fn_slowclap(self,args,client,destination):
        'Slowclap. Format: slowclap'
        self.base_say('*clap*',destination)
        time.sleep(0.5)
        self.base_say('*clap*',destination)
        time.sleep(2)
        return '*clap.*'

#    def fn_hallo_add(self, args, client, destination):
#        'Add a greeting for a user.  Use "hallo_add <user> <greeting>".  Ops only.'
#        if(self.op(client)):
##            greetingslist = shelve.open('Store/hallo-greetings')
#            greetingslist = hallodata
#            name = args.split(' ')[0]
#            greeting = args[len(name) + 1:]
#            greetingslist[name] = greeting.replace('\\n', '\n')
##            greetingslist.close()
#            return 'Greeting added.'
#        else:
#            return 'Insufficient privelages to add a greeting.'
    
#    def fn_hallo(self, args, client, destination):
#        'Be greeted!  Use "hallo".'
##        greetingslist = shelve.open('Store/hallo-greetings')
#        greetingslist = hallodata
#        defaultgreeting = 'Hallo, ' + client + ', Have I met you before?'
#        greeting = greetingslist.has_key(client) and greetingslist[client] or defaultgreeting
##        greetingslist.close()
#        return greeting
    
#    def fn_hallo_list(self, args, client, destination):
#        'Get a list of greetings.  Use "hallo_list".  Ops only.'
#        if(self.op(client)):
##            greetingslist = shelve.open('Store/hallo-greetings')
#            greetingslist = hallodata
#            out = '\n'.join([key + ': ' + greetingslist[key] for key in greetingslist.keys()])
##            greetingslist.close()
#            return out
#        else:
#            return 'Insufficient privelages to list greetings.'

#    def fn_hallo_del(self, args, client, destination.):
#        'Delete a greeting for a user.  Use "hallo_del <user>".  Requires op.'
#        if(self.op(client)):
##            greetingslist = shelve.open('Store/hallo-greetings')
#            greetingslist = hallodata
#            del greetingslist[args]
##            greetingslist.close()
#            return 'Greeting for ' + args + ' deleted.'
#        else:
#            return 'Insufficient privelages to list greetings.'
   
    def fn_longcat_on(self, args, client, destination):
        'turn on longcat function.  Use with caution!'
        if(destination[1].lower() == '#ukofequestria'):
            return 'Longcat cannot be activated here, sorry.'
        else:
            if(self.chk_op(destination[0],client)):
                self.longcat = True
                return 'Longcat enabled.  Use "longcat_off" to turn it off.'
    
    def fn_longcat_off(self, args, client, destination):
        'Turn off longcat functon.'
        if(self.chk_op(destination[0],client)):
            self.longcat = False
            return 'Longcat disabled.  Use "longcat_on" to turn it on.'

    def fn_longcat(self, args, client, destination):
        'Make a longcat!'
        if(destination[1].lower() == '#ukofequestria'):
            return 'Sorry, longcat is not available here.'
        else:
            if(self.longcat):
                if(self.chk_god(destination[0],client)):
                    longcathead = '    /\___/\ \n   /       \ \n  |  #    # |\n  \     @   |\n   \   _|_ /\n   /       \______\n  / _______ ___   \ \n  |_____   \   \__/\n   |    \__/\n'
                    longcatsegment = '   |       |\n'
                    longcattail = '   /        \ \n  /   ____   \ \n  |  /    \  |\n  | |      | |\n  /  |      |  \ \n  \__/      \__/'
                    longcatsegments = int(args)
                    longcat = longcathead + longcatsegment * longcatsegments + longcattail + '\n Longcat is L' + 'o' * longcatsegments + 'ng!'
                    return longcat
                else:
                    return 'Longcat is for gods only :P'
            else:
                return 'Longcat is disabled.  Use "longcat_on" to enable it.'

#    def fn_longyo(self, args, client, destination):
#        'Make a longyo'
#        return 'yo' * int(args)

    def fn_roll(self, args, client, destination):
        'Roll X-Y returns a random number between X and Y'
        if(args.count('-')==1):
            num = args.split('-')
            ranges = int(num[0])
            rangee = int(num[1])
            if(ranges<rangee):
                rand = random.randint(ranges,rangee)
                return 'I roll ' + str(rand) + '!!!'
            else:
                return 'Smaller number goes first, I bet it was ari or Ripp_ who tried putting them in the other way.'
        elif(args.lower().count('d')==1):
            num = args.lower().split('d')
            sides = int(num[1])
            dice = int(num[0])
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
                return "More than zero dice. I'm gonna bet Zephyr did that one."
        else:
            return "Please give input in the form of X-Y or XdY"

    def fn_choose(self, args, client, destination):
        'choose X, Y or Z or ... Returns one of the options separated by "or" or a comma.'
#        args = args.lower()
#        choices = args.split(', or |, | or ')
        choices = re.compile(', | or ',re.IGNORECASE).split(args)
#        allchoices = []
#        for x in choices:
#           morechoices = x.split(', ')
#           for y in morechoices: 
#              allchoices.append(y)
#        numchoices = len(allchoices)
        numchoices = len(choices)
        if(numchoices==1):
           return 'Please present me with more than 1 thing to choose from!'
        else:
           rand = random.randint(0,numchoices-1)
#           choice = allchoices[rand]
           choice = choices[rand]
#           listchoice = allchoices[0]
#           z = 0
#           while z < (numchoices-2):
#              listchoice += ', ' + allchoices[z+1]
#              z += 1
#           listchoice += ' or ' + allchoices[numchoices-1]
           return 'I choose "' + choice + '"'

    def fn_ponyep(self, args, client, destination):
        'Chooses a pony episode to watch at random'
        episodes = ["S01E01 - Episode 1","S01E02 - Episode 2","S01E03 - The Ticket Master","S01E04 - Applebuck Season","S01E05 - Griffon the Brush-Off","S01E06 - Boast Busters","S01E07 - Dragonshy","S01E08 - Look Before You Sleep","S01E09 - Bridle Gossip","S01E10 - Swarm of the Century","S01E11 - Winter Wrap-Up","S01E12 - Call of the Cutie","S01E13 - Fall Weather Friends","S01E14 - Suited for Success","S01E15 - Feeling Pinkie Keen","S01E16 - Sonic Rainboom","S01E17 - Stare Master","S01E18 - The Show Stoppers","S01E19 - A Dog and Pony Show","S01E20 - Green is not your Color","S01E21 - Over a Barrel","S01E22 - A Bird in the Hoof","S01E23 - The Cutie Mark Chronicles","S01E24 - Owls well that Ends well","S01E25 - Party of One","S01E26 - The Best Night Ever","S02E01 - Return of Harmony Part 1","S02E02 - Return of Harmony Part 2","S02E03 - Lesson Zero","S02E04 - Luna Eclipsed","S02E05 - Sisterhooves Social","S02E06 - The Cutie Pox","S02E07 - May the Best Pet Win","S02E08 - The Mysterious Mare Do Well","S02E09 - Sweet and Elite","S02E10 - Secret of My Excess","S02E11 - Hearth's Warming Eve","S02E12 - Family Appreciation Day","S02E13 - Baby Cakes","S02E14 - The Last Roundup","S02E15 - The Super Speedy Cider Squeezy 6000","S02E16 - Read it and Weep","S02E17 - Hearts and Hooves day","S02E18 - A Friend In Deed","S02E19 - Putting Your Hoof Down","S02E20 - It's About Time","S02E21 - Dragon Quest","S02E22 - Hurricane Fluttershy","S02E23 - Ponyville Confidential","S02E24 - MMMystery on the Friendship Express","S02E25 - Canterlot Wedding Part 1","S02E26 - Canterlot Wedding Part 2","S03E01 - The Crystal Empire Part 1","S03E02 - The Crystal Empire Part 2","S03E03 - Too Many Pinkie Pies","S03E04 - One Bad Apple","S03E05 - Magic Duel","S03E06 - Sleepless in Ponyville","S03E07 - Wonderbolts Academy","S03E08 - Apple Family Reunion","S03E09 - Spike at your Service","S03E10 - Keep Calm and Flutter On","S03E11 - Just for Sidekicks","S03E12 - Games Ponies Play","S03E13 - Magical Mystery Cure"]
        songepisodes = ["S01E01 - Episode 1","S01E02 - Episode 2","S01E03 - The Ticket Master","S01E11 - Winter Wrap-Up","S01E14 - Suited for Success","S01E18 - The Show Stoppers","S01E23 - The Cutie Mark Chronicles","S01E26 - The Best Night Ever","S02E07 - May the Best Pet Win","S02E09 - Sweet and Elite","S02E11 - Hearth's Warming Eve","S02E13 - Baby Cakes","S02E15 - The Super Speedy Cider Squeezy 6000","S02E17 - Hearts and Hooves day","S02E18 - A Friend In Deed","S02E25 - Canterlot Wedding Part 1","S02E26 - Canterlot Wedding Part 2","S03E01 - The Crystal Empire Part 1","S03E02 - The Crystal Empire Part 2","S03E04 - One Bad Apple","S03E08 - Apple Family Reunion","S03E13 - Magical Mystery Cure"]
        if(args.lower()!="song"):
           numepisodes = len(episodes)
           rand = random.randint(0,numepisodes-1)
           episode = episodes[rand]
        else:
           numepisodes = len(songepisodes)
           rand = random.randint(0,numepisodes-1)
           episode = songepisodes[rand]
        return 'You should choose "' + episode + '"'

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
            if int(float(post_calc)) == 0:
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
        'Calc function, but written in python'
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
        return answer

    def fn_finnbot(self, args, client, destination):
        'Nothing to see here.'
        ariquotes = ["|:", "After hearing you say that, I don't think we can ever be friends", "Brb, cutting down a forest", "Can't answer, I'm shaving and it'll take all day", "Can't hear you over all this atheism!", "Can this wait until after i've listened to this song 100 times on repeat?", "Could use less degrees", "Don't want to hear it, too busy complaining about the tap water", "Goony goon goon", "Hang on, I have to help some micronationalist", "Hey guys, check out my desktop: http://hallo.dr-spangle.com/DESKTOP.PNG", "If we get into a fight, I'll pick you up and run away", "I happen to be an expert on this subject", "I think I've finished constructing a hate engine", "It's about time for me to play through adom again", "It's kind of hard to type while kneeling", "I wish I could answer, but i'm busy redditing", "*lifeless stare*", "Lol, perl", "Lol, remember when i got eli to play crawl for a week?", "Needs moar haskell", "NP: Bad Religion - whatever song", "Remember that thing we were going to do? Now I don't want to do it", "Smells like Oulu", "Some Rahikkala is getting married, you are not invited", "That blows, but I cannot relate to your situation", "This somehow reminds me of my army days", "Whatever, if you'll excuse me, i'm gonna bike 50 kilometers", "You guys are things that say things", "You're under arrest for having too much fun","I have found a new favourite thing to hate"]
        ariswearquotes = ["FUCK. FINNISH. PEOPLE!!!", "FUCK MANNERHEIM", "YOU'RE A PERSON OF SHIT"]
        if(self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect']):
            for quote in ariswearquotes:
                ariquotes.append(quote)
        numquotes = len(ariquotes)
        rand = random.randint(0,numquotes-1)
        quote = ariquotes[rand]
        return quote

    def fn_time(self, args, client, destination):
        'Current time'
        timestamp = time.time()
        timezone = 'UTC'
        if(args==''):
           name = 'time'
        else:
           name = args.split()[0].lower()
        if(name=='d000242' or name=='d00242' or name=='eli'):
           offset = 8
           timezone = 'for D000242'
        elif(name=='icebreaker' or name=='ice' or name=='isaac'):
           offset = -7
           timezone = 'for icebreaker'
        elif(name=='ari' or name=='finnbot' or name=='finbot'):
           offset = 3
           timezone = 'for ari'
        elif(name=='beets' or name=='ruth'):
           offset = -4
           timezone = 'for beets'
        elif(name=='dolphin' or name=='fucker'):
           offset = -7
           timezone = 'for dolphin'
        elif(name=='dr-spangle' or name=='dr-spang1e' or name=='hallo' or name=='spangle' or name=='josh' or name=='britfag' or name=='britbot'):
           offset = 1 
           timezone = 'for spangle'
        elif(name=='zephyr' or name=='zephyr42' or name=='safi'):
           offset = 1
           timezone = 'for zephyr'
        elif(name=='eve' or name=='eve online' or name=='spreadsheetsonline' or name=='spreadsheets online'):
           offset = 0
           timezone = 'for EvE'
        elif(name=='time'):
           offset = 0
           timezone = ''
        else:
           offset = 0
           timezone = 'UTC (Not sure what your input meant.)'
        timestamp = timestamp+(3600*offset)
        timeword = time.strftime('%H:%M:%S %d/%m/%Y',time.gmtime(timestamp))
        return 'The time is ' + timeword + ' ' + timezone

    def fn_is(self, args, client, destination):
        'Placeholder'
        return 'I am?'

    def fn_(self, args, client, destination):
        'wonder if this works'
        return 'Yes?'

    def fn_alarm(self, args, client, destination):
        'Alarm.'
        return 'woo woooooo woooooo ' + args + ' wooo wooo'

    def fn_mods(self, args, client, destination):
        'Mods.. asleep?'
        if(args.lower()=='asleep'):
           number = random.randint(0,61)
           if(number < 10):
              link = 'http://dr-spangle.com/AT/0' + str(number) + '.JPG'
           else:
              link = 'http://dr-spangle.com/AT/' + str(number) + '.JPG'
           return 'Mods are asleep? Post arctic terns!! ' + link
        elif(args.lower()=='napping'):
           number = random.randint(0,1)
           link = 'http://dr-spangle.com/AT/N0' + str(number) + '.JPG'
           return 'Mods are napping? Post plush arctic terns! ' + link
        else:
           return 'I am not sure I care.'

    def fn_bestpony(self, args, client, destination):
        'Who is bestpony?'
        arr_ponies = [["Applejack|she", "Fluttershy|she", "Pinkie Pie|she", "Rainbow Dash|she", "Rarity|she", "Twilight Sparkle|she"], ["Princess Cadence|she", "Princess Celestia|she", "Princess Luna|she", "Shining Armor|he"], ["Applebloom|she", "Babs Seed|she", "Scootaloo|she", "Sweetie Belle|she"], ["Big Macintosh|he", "Blossomforth|she", "Cheerilee|she", "Daisy|she", "Derpy Hooves|she", "Dr Hooves|he", "Filthy Rich|he", "Golden Harvest|she", "Granny Smith|she", "Lily|she", "Lotus Blossom|she", "Lyra Heartstrings|she", "Mayor Mare|she", "Minuette|she", "Mr Carrot Cake|he", "Mrs Cup Cake|she", "Nurse Redheart|she", "Pound Cake|he", "Pumpkin Cake|she", "Sweetie Drops|she", "Rose|she"], ["Discord|he", "Fido|he", "Flim|he", "Garble|he", "Gilda|she", "King Sombra|he", "Nightmare Moon|she", "Queen Chrysalis|she", "Rover|he", "Spot|he", "The GREAT and POWERFUL Trixie!|she"], ["Fleetfoot|she", "Soarin|he", "Spitfire|she"], ["DJ-PON3|she", "Donut Joe|he", "Fancy Pants|he", "Fleur de Lis|she", "Hoity Toity|he", "Jet Set|he", "Octavia Melody|she", "Photo Finish|she", "Prince Blueblood|he", "Sapphire Shores|she", "Upper Crust|she"], ["Flitter|she", "Lightning Dust|she", "Stormwalker|she", "Thunderlane|he"], ["Diamond Tiara|she", "Featherweight|he", "Pip Squeak|he", "Silver Spoon|she", "Snails|he", "Snips|he", "Twist|she"], ["Chancellor Puddinghead|she", "Clover the Clever|she", "Commander Hurricane|she", "Princess Platinum|she", "Private Pansy|she", "Smart Cookie|she"], ["Chief Thunderhooves|he", "Crackle|she", "Cranky Doodle Donkey|he", "Gustave Le Grand|he", "Iron Will|he", "Little Strongheart|she", "Madame Leflour|she", "Manny Roar|he", "Matilda|she", "muffinmare|she", "Mulia Mild|she", "Rocky|he", "Sir Lintsalot|he", "Smarty Pants|she", "Spike|he", "Steven Magnet|he", "Zecora|she"], ["Braeburn|he", "Daring Do|she", "Ms. Harshwhinny|she"], ["Angel|he", "Gummy|he", "Opalescence|she", "Owlowiscious|he", "Peewee|he", "Tank|he", "Winona|she"]]
        arr_weights = ["mane6", "mane6", "mane6", "mane6", "mane6", "princess", "princess", "princess", "princess", "cmc", "cmc", "cmc", "ponyville", "ponyville", "villain", "villain", "wonderbolt", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming", "notapony", "other", "pet"]
        arr_categories = ["mane6", "princess", "cmc", "ponyville", "villain", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming", "notapony", "other", "pet"]
        activearray = arr_ponies[arr_categories.index(arr_weights[random.randint(0,len(arr_weights)-1)])]
        bestpony = activearray[random.randint(0,len(activearray)-1)]
        if(client.lower() == 'd000242'):
            bestpony = "Pinkie Pie|she"
        arr_premessage = ["Obviously {X} is best pony because ", "Well, everyone knows that {X} is bestpony, I mean ", "The best pony is certainly {X}, ", "There's no debate, {X} is bestpony, ", "Bestpony? You must be talking about {X}, "]
        arr_postmessage = ["{Y}'s just such a distinctive character.", "{Y} really just stands out.", "{Y} really makes the show worth watching for me.", "{Y} stands up for what's best for everypony.", "I can really identify with that character.", "I just love the colourscheme I suppose.", "I mean, why not?"]
        num_ponies = len(arr_ponies)
        num_premessage = len(arr_premessage)
        num_postmessage = len(arr_postmessage)
        randpony = random.randint(0,num_ponies-1)
        randpre = random.randint(0,num_premessage-1)
        randpost = random.randint(0,num_postmessage-1)
        return arr_premessage[randpre].replace("{X}",bestpony.split("|")[0]) + arr_postmessage[randpost].replace("{Y}",bestpony.split("|")[1])

    def fn_boop(self, args, client, destination):
        'Boops people'
        if(args==''):
            return "This function boops people, as such you need to specify a person for me to boop, in the form 'Hallo boop <name>' but without the <> brackets"
        args = args.split()
        online = ' '.join(self.chk_recipientonline(destination[0],args))
        if(online==' ' or online==''):
            return 'No one called "' + args + '" is online.'
        else:
            return '\x01ACTION boops ' + online.replace(' ','') + '.\x01'

    def fn_cupcake(self, args, client, destination):
        'Gives out cupcakes (much better than muffins.)'
        online = self.chk_recipientonline(destination[0],args.split()[0])
        if(online==' ' or online==''):
            return 'No one called "' + args.split()[0] + '" is online.'
        else:
            if(len(args.split()) >= 2):
                return '\x01ACTION gives ' + args.split()[0] + ' a ' + ' '.join(args.split()[1:]) + ' cupcake, from ' + client + '\x01'
            else:
                return '\x01ACTION gives ' + args.split()[0] + ' a cupcake, from ' + client + '\x01'

    def fn_eulerreload(self,args,client,destination):
        'Reloads the euler module.'
        if(self.chk_op(destination[0],client)):
            import euler
            reload(euler)
            from euler import eulerclass
            return "Euler functions reloaded."
        else:
            return "You do not have permission to use this command, sorry."

    def fn_speak(self,args,client,destination):
        'He can talk!'
        if(self.chk_god(destination[0],client)):
       #     return client + ": " + self.megahal.get_reply_nolearn(args)
            return "*woof!!!*"
        elif(self.chk_ops(destination[0],client)):
            return "*woof!*"
        else:
            return "*woof*"

    def fn_speaklearn(self,args,client,destination):
        'Teach him a file, gods only.'
        if(self.chk_god(destination[0],client)):
    #        self.megahal.train(args)
    #        self.megahal.sync()
            return "Learnt the file " + args + " ... hopefully."
        else:
            return "You're not spangle."

    def fn__S(self,args,client,destination):
        'redirects to speak function'
        return self.fn_speak(args,client,destination)

    def fn_silencetherabble(self,args,client,destination):
        'ETD only. deops all but D000242 and self. sets mute.'
        if(self.chk_god(destination[0],client) and destination[1].lower() == '#ecco-the-dolphin'):
            names = self.chk_names(destination[0],destination[1])
            if('@' + self.conf['server'][destination[0]]['nick'] not in names):
                return 'I cannot handle it, master!'
            for user in names.split():
                if('000242' not in user and self.conf['server'][destination[0]]['nick'] not in user):
                    stripuser = user.replace('@','').replace('+','')
                    if('@' in user):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -o ' + stripuser + endl).encode('utf-8'))
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + stripuser + endl).encode('utf-8'))
                    if('+' in user):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + stripuser + endl).encode('utf-8'))
            self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +m' + endl).encode('utf-8'))
            return 'I have done your bidding, master.'
        else:
            return 'You are not my master.'

    def fn_poketheasshole(self,args,client,destination):
        'ETD only. voices and unvoices Dolphin repeatedly.'
        if('000242' in client and destination[1].lower() == '#ecco-the-dolphin'):
            if(args.isdigit()):
                 number = int(args)
            else:
                 number = 5
            for x in range(number):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v Dolphin' + endl).encode('utf-8'))
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v Dolphin' + endl).encode('utf-8'))
            return 'Dolphin: You awake yet?'
        else:
            return '"poketheasshole" not defined.  Try "/msg Hallo help commands" for a list of commands.'

    def fn_foof(self,args,client,destination):
        'FOOOOOOOOOF'
        rand = random.randint(0,2)
        if(rand==0):
            return 'doof'
        elif(rand==1):
            return 'doooooof'
        else:
            return 'ddddoooooooooooooooooooooffffffffff.'

    def fn_thoughtfortheday(self,args,client,destination):
        'WH40K Thought for the day.'
        thoughts = euler.euler.fnn_euler_readfiletolist(self,'store/WH40K_ToTD2.txt')
        rand = random.randint(0,len(thoughts)-1)
        return '"' + thoughts[rand] + '"'

    def fn_eightball(self,args,client,destination):
        'Magic 8 ball.'
        responses = ['It is certain','It is decidedly so','Without a doubt','Yes definitely','You may rely on it','As I see it yes','Most likely','Outlook good','Yes','Signs point to yes','Reply hazy try again','Ask again later','Better not tell you now','Cannot predict now','Concentrate and ask again',"Don't count on it",'My reply is no','My sources say no','Outlook not so good','Very doubtful']
        rand = random.randint(0,len(responses)-1)
        return responses[rand]

    def fn_ouija(self,args,client,destination):
        'Ouija board function. "Ouija board" is copyright Hasbro.'
        words = euler.euler.fnn_euler_readfiletolist(self,'/usr/share/cracklib/cracklib-small')
        numwords = random.randint(1,3)
        string = "I'm getting a message from the other side..."
        for x in range(numwords):
            rand = random.randint(0,len(words)-1)
            string = string + ' ' + words[rand]
        return string

    def fn_chosenone(self,args,client,destination):
        'Specifies who the chosen one is.'
        names = self.chk_names(destination[0],destination[1])
        tempnameslist = names.split()
        nameslist = []
        for name in tempnameslist:
            if('_S' != name and self.conf['server'][destination[0]]['nick'] not in name):
                nameslist.append(name.replace('+','').replace('%','').replace('@','').replace('~','').replace('&',''))
        rand = random.randint(0,len(nameslist)-1)
        return 'It should be obvious by now that ' + nameslist[rand] + ' is the chosen one.'

    def fn_channels(self,args,client,destination):
        'Hallo will tell you which channels he is in, ops only.'
        if(self.chk_op(destination[0],client)):
            return "I'm in these channels: " + ', '.join(self.conf['server'][destination[0]]['channels']) + ". I think..."
        else:
            return "Sorry, this function is for ops only."

    def fn_amiregistered(self,args,client,destination):
        'Hallo checks if you are registered, tells you result.'
        if(self.chk_userregistered(destination[0],client)):
            return "Yup, you are registered."
        else:
            return "It doesn't seem you are registered with nickserv right now."

    def fn_scriptures(self,args,client,destination):
        'Recites a passage from the scriptures.'
        scriptures = pickle.load(open('store/scriptures.p','r'))
        rand = random.randint(0,len(scriptures)-1)
        return scriptures[rand]

    def fn_active_threads(self,args,client,destination):
        'Returns current number of active threads.. should probably be gods only'
        return "I think I have " + str(threading.active_count()) + " active threads right now."

    def fn_inspace(self,args,client,destination):
        'Returns the number of people in space right now, and their names.'
        pagerequest = urllib.request.Request('http://www.howmanypeopleareinspacerightnow.com/space.json')
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageopener = urllib.request.build_opener()
        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read()
        space = json.loads(code.decode('utf-8'))
        return "There are " + str(space['number']) + " people in space right now. Their names are: " + ', '.join(x['name'] for x in space['people'])

    def fn_deer(self,args,client,destination):
        'ascii art deer.'
        deer = r'''   /|       |\
`__\\       //__'
   ||      ||
 \__`\     |'__/
   `_\\   //_'
   _.,:---;,._
   \_:     :_/
     |@. .@|
     |     |
     ,\.-./ \
     ;;`-'   `---__________-----.-.
     ;;;                         \_\
     ';;;                         |
      ;    |                      ;
       \   \     \        |      /
        \_, \    /        \     |\
          |';|  |,,,,,,,,/ \    \ \_
          |  |  |           \   /   |
          \  \  |           |  / \  |
           | || |           | |   | |
           | || |           | |   | |
           | || |           | |   | |
           |_||_|           |_|   |_|
          /_//_/           /_/   /_/'''
        if(self.chk_god(destination[0],client)):
            return deer
        else:
            return "You have insufficient privileges to summon the deer"


    def fn_dragon(self,args,client,destination):
        'prints ascii dragon'
        dragon = r''',-,- / / | ,-' _/ / / (-_ _,-' `Z_/ "#: ,-'_,-. \ 
_ #' _(_-'_()\ \" | ,-6-_,--' | / "" L-'\ \,--^---v--v-._ / \ | 
\_________________,-' | \ \ Wny \ '''
        dragon = r'''hmm.. nah. have another deer
       ""\/ \/""
         "\__/"
          (oo)
 -. ______-LJ
  ,'        |
  |.____..  /
  \\      /A\
  |A      |//'''
        if(self.chk_god(destination[0],client)):
            return dragon
        else:
            return "You have insufficient privileges."
     
    def fn_mute(self,args,client,destination):
        'Mutes a given channel or current channel'
        if(self.chk_op(destination[0],client)):
            args = args.replace(' ','')
            if(args==''):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +m ' + endl).encode('utf-8'))
                return "Muted the channel."
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +m ' + endl).encode('utf-8'))
                return "Muted " + args
        else:
            return "You have insufficient privileges to use this function."

    def fn_unmute(self,args,client,destination):
        'Unmutes a given channel or current channel if none is given.'
        if(self.chk_op(destination[0],client)):
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
        'Sends a message to all online staff members, and posts a message in the staff channel'
        for admin in self.chk_recipientonline(destination[0],self.conf['server'][destination[0]]['admininform']):
            self.base_say(client + ' has sent a message to all staff members. The message is as follows: ' + args,[destination[0],admin])
        self.base_say(client + ' has sent a message to all staff members. The message is as follows: ' + args,[destination[0],'#ukofequestriaircstaff'])
        return "Message delivered. A staff member will be in contact with you shortly. :)"

    def fn_avg(self,args,client,destination):
        'finds the average of a list of numbers'
        numberlist = args.split()
        numbersum = sum(float(x) for x in numberlist)
        return "The average of " + ', '.join(numberlist) + " is: " + str(numbersum/float(len(numberlist)))

    def fn_random_cocktail(self,args,client,destination):
        'Delivers ingredients and recipes for a random cocktail.'
        cocktails = pickle.load(open('store/cocktails.p','rb'))
        number = random.randint(0,len(cocktails))
        cocktail = cocktails[number]
        output = "Randomly selected cocktail is: " + cocktail['name'] + " (#" + str(number) + "). The ingredients are: "
        ingredients = []
        for ingredient in cocktail['ingredients']:
            ingredients.append(ingredient[0] + ingredient[1])
        output = output + ", ".join(ingredients) + ". The recipe is: " + cocktail['instructions']
        return output

    def fn_cocktail(self,args,client,destination):
        'Returns ingredients and instructions for a given cocktail (or closest guess)'
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
            return "Closest I have is " + closest[0] + ". The ingredients are: " + ", ".join(ingredients) + ". The recipe is: " + cocktail['instructions']

#    def fn_listadd(self, args, client, destination):
#        'Creates a new list for this user'
#        if(self.op(client)):
#            greetingslist = shelve.open('Store/hallo-greetings')
#            listlist = hallolists
#            name = args.split(' ')[0]
#            list = args[len(name) + 1:]
#            listlist[name] = greeting.replace('\\n', '\n')
#            listlist.close()
#            return 'Greeting added.'
#        else:
#            return 'Insufficient privelages to add a greeting.'

