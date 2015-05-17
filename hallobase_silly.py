import random       #for choosing ouija words, pony episodes, etc
import time         #checking the time for the time function

import ircbot_chk   #for checking users have appropriate permissions to use certain functions

endl = "\r\n"

class hallobase_silly():
#    def init(self):
#        self.longcat = False

    def fn_slowclap(self,args,client,destination):
        'Slowclap. Format: slowclap'
        if(args.replace(' ','')!=''):
            self.base_say('*clap*',[destination[0],args])
            time.sleep(0.5)
            self.base_say('*clap*',[destination[0],args])
            time.sleep(2)
            self.base_say('*clap.*',[destination[0],args])
            return "done. :)"
        else:
            self.base_say('*clap*',destination)
            time.sleep(0.5)
            self.base_say('*clap*',destination)
            time.sleep(2)
            return '*clap.*'

    def fn_time(self, args, client, destination):
        'Current time for a given user. Format: time <username>'
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
        return 'The time is ' + timeword + ' ' + timezone + '.'

    def fn_is(self,args,client,destination):
        'Placeholder. Format: is'
        return 'I am?'

    def fn_(self, args, client, destination):
        'I wonder if this works. Format: '
        return 'Yes?'

    def fn_alarm(self, args, client, destination):
        'Alarm. Format: alarm <subject>'
        return 'woo woooooo woooooo ' + args + ' wooo wooo!'

    def fn_mods(self, args, client, destination):
        'Mods.. asleep? Format: "mods asleep" to post pictures of arctic terns. "mods napping" to post pictures of plush arctic terns.'
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

    def fn_silence_the_rabble(self,args,client,destination):
        'ETD only. deops all but D000242 and self. sets mute. Format: silence_the_rabble'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client) and destination[1].lower() == '#ecco-the-dolphin'):
#            names = ircbot_chk.ircbot_chk.chk_names(self,destination[0],destination[1])
            if('@' + self.conf['server'][destination[0]]['nick'] not in self.core['server'][destination[0]]['channel'][destination[1]]['user_list']):
                return 'I cannot handle it, master!'
            for user in self.core['server'][destination[0]]['channel'][destination[1]]['user_list']:
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

    def fn_poke_the_asshole(self,args,client,destination):
        'ETD only. voices and unvoices Dolphin repeatedly. Format: poke_the_asshole'
        if('000242' in client and destination[1].lower() == '#ecco-the-dolphin'):
            if(args.isdigit()):
                number = int(args)
            else:
                number = 5
            for _ in range(number):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v Dolphin' + endl).encode('utf-8'))
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v Dolphin' + endl).encode('utf-8'))
            return 'Dolphin: You awake yet?'
        else:
            return '"poketheasshole" not defined.  Try "/msg Hallo help commands" for a list of commands.'

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

        



