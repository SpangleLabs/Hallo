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

    def fn_invite(self,args,client,destination):
        'Invite someone to a channel'
        args_split = args.split()
        if(not ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return "This function is for ops only."
        if(len(args_split) == 1):
            if(ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])[0][0] is not None):
                nick = client
                channel = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])
            else:
                nick = args_split[0]
                channel = [destination]
        else:
            if(ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])[0][0] is not None):
                nick = args_split[1]
                channel = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])
            elif(ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[1])[0][0] is not None):
                nick = args_split[0]
                channel = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[1])
            else:
                return "Invalid channel."
        channels = []
        for destpair in channel:
            if(destpair[0]==destination[0]):
                channels.append(destpair[1])
        for chan in channels:
            self.core['server'][destination[0]]['socket'].send(('INVITE '  + nick + ' ' + chan + endl).encode('utf-8'))
        return "Invited " + nick + " to " + ', '.join(channels) + "."


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
        while(len(args)>1 and args[0] in [' ',':']):
            args = args[1:]
        choices = re.compile(', | or ',re.IGNORECASE).split(args)
        numchoices = len(choices)
        if(numchoices==1):
           return 'Please present me with more than 1 thing to choose from!'
        else:
           rand = random.randint(0,numchoices-1)
           choice = choices[rand]
           return 'I choose "' + choice + '".'

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

    def fn_say(self,args,client,destination):
        'Say a message into a channel or server/channel pair (in the format "{server,channel}"). Format: say <channel> <message>'
        dest = args.split()[0]
        message = ' '.join(args.split()[1:])
        destlist = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,dest)
        if(len(destlist)==1 and destlist[0][0] is None):
            return "Failed to find destination, error returned was: " + destlist[0][1]
        skipped = 0
        for destpair in destlist:
            if(ircbot_chk.ircbot_chk.chk_swear(self,destpair[0],destpair[1],message)!=['none','none']):
                skipped = skipped + 1
            else:
                if(self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']):
                    self.base_say(message,destpair)
        if(skipped==0):
            if(len(destlist)==1):
                return "Message sent."
            else:
                return "Messages sent to " + str(len([destpair for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])) + " channels: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])
        else:
            if(len(destlist)==1):
                return "That message contains a word which is on the swearlist for that channel."
            else:
                return "Messages sent to " + str(len([destpair for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])-skipped) + " channels: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if sel.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']]) + " But not sent to " + str(skipped) + " channels, due to swearlist violation: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])



#convert_currency_update
#-pull currency data from somewhere


