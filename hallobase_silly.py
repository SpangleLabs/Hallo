import random       #for choosing ouija words, pony episodes, etc
import time         #checking the time for the time function
import pickle       #to load amarr scriptures

import ircbot_chk   #for checking users have appropriate permissions to use certain functions

class hallobase_silly():
   # def init(self):
   #     self.longcat = False

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

    def fn_longcat_on(self, args, client, destination):
        'Turn on longcat function. Use with caution! Format: longcat_on'
        if(destination[1].lower() == '#ukofequestria'):
            return 'Longcat cannot be activated here, sorry.'
        else:
            if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                self.longcat = True
                return 'Longcat enabled.  Use "longcat_off" to turn it off.'

    def fn_longcat_off(self, args, client, destination):
        'Turn off longcat functon. Format: longcat_off'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            self.longcat = False
            return 'Longcat disabled.  Use "longcat_on" to turn it on.'

    def fn_longcat(self, args, client, destination):
        'Make a longcat! Format: longcat <length>'
        if(destination[1].lower() == '#ukofequestria'):
            return 'Sorry, longcat is not available here.'
        else:
            if(self.longcat):
                if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
                    longcathead = '    /\___/\ \n   /       \ \n  |  #    # |\n  \     @   |\n   \   _|_ /\n   /       \______\n  / _______ ___   \ \n  |_____   \   \__/\n   |    \__/\n'
                    longcatsegment = '   |       |\n'
                    longcattail = '   /        \ \n  /   ____   \ \n  |  /    \  |\n  | |      | |\n  /  |      |  \ \n  \__/      \__/'
                    longcatsegments = int(args)
                    longcat = longcathead + longcatsegment * longcatsegments + longcattail + '\n Longcat is L' + 'o' * longcatsegments + 'ng!'
                    return longcat
                else:
                    return 'Longcat is for gods only.'
            else:
                return 'Longcat is disabled.  Use "longcat_on" to enable it.'

    def fn_finnbot(self, args, client, destination):
        'Simulates a typical finn in conversation. Format: finnbot'
        ariquotes = ["|:", "After hearing you say that, I don't think we can ever be friends", "Brb, cutting down a forest", "Can't answer, I'm shaving and it'll take all day", "Can't hear you over all this atheism!", "Can this wait until after i've listened to this song 100 times on repeat?", "Could use less degrees", "Don't want to hear it, too busy complaining about the tap water", "Goony goon goon", "Hang on, I have to help some micronationalist", "Hey guys, check out my desktop: http://hallo.dr-spangle.com/DESKTOP.PNG", "If we get into a fight, I'll pick you up and run away", "I happen to be an expert on this subject", "I think I've finished constructing a hate engine", "It's about time for me to play through adom again", "It's kind of hard to type while kneeling", "I wish I could answer, but i'm busy redditing", "*lifeless stare*", "Lol, perl", "Lol, remember when i got eli to play crawl for a week?", "Needs moar haskell", "NP: Bad Religion - whatever song", "Remember that thing we were going to do? Now I don't want to do it", "Smells like Oulu", "Some Rahikkala is getting married, you are not invited", "That blows, but I cannot relate to your situation", "This somehow reminds me of my army days", "Whatever, if you'll excuse me, i'm gonna bike 50 kilometers", "You guys are things that say things", "You're under arrest for having too much fun","I have found a new favourite thing to hate"]
        ariswearquotes = ["FUCK. FINNISH. PEOPLE!!!", "FUCK MANNERHEIM", "YOU'RE A PERSON OF SHIT"]
        if(self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect']):
            for quote in ariswearquotes:
                ariquotes.append(quote)
        numquotes = len(ariquotes)
        rand = random.randint(0,numquotes-1)
        quote = ariquotes[rand]
        return quote + "."

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
           # names = ircbot_chk.ircbot_chk.chk_names(self,destination[0],destination[1])
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
            for x in range(number):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v Dolphin' + endl).encode('utf-8'))
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v Dolphin' + endl).encode('utf-8'))
            return 'Dolphin: You awake yet?'
        else:
            return '"poketheasshole" not defined.  Try "/msg Hallo help commands" for a list of commands.'

    def fn_deer(self,args,client,destination):
        'ascii art deer. Format: deer'
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
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return deer
        else:
            return "You have insufficient privileges to summon the deer."

    def fn_dragon(self,args,client,destination):
        'Prints ascii dragon. Format: dragon'
        dragon = r''',-,- / / | ,-' _/ / / (-_ _,-' `Z_/ "#: ,-'_,-. \
_ #' _(_-'_()\ \" | ,-6-_,--' | / "" L-'\ \,--^---v--v-._ / \ |
\_________________,-' | \ \ Wny \ '''
        dragon = r'''hmm.. nah. have another deer.
       ""\/ \/""
         "\__/"
          (oo)
 -. ______-LJ
  ,'        |
  |.____..  /
  \\      /A\
  |A      |//'''
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return dragon
        else:
            return "You have insufficient privileges."

    def fn_train(self,args,client,destination):
        'Prints ascii train. Format: train'
        train = r'''chugga chugga, chugga chugga, woo woo!
            ____.-==-, _______  _______  _______  _______  _..._
           {"""""LILI|[" " "'"]['""'"""][''"""'']["" """"][LI LI]
  ^#^#^#^#^/_OO====OO`'OO---OO''OO---OO''OO---OO''OO---OO`'OO-OO'^#^#^#^
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return train
        else:
            return "You have insufficient power to summon a train."

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

    def fn_in_space(self,args,client,destination):
        'Returns the number of people in space right now, and their names. Format: in_space'
        pagerequest = urllib.request.Request('http://www.howmanypeopleareinspacerightnow.com/space.json')
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageopener = urllib.request.build_opener()
        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read()
        space = json.loads(code.decode('utf-8'))
        return "There are " + str(space['number']) + " people in space right now. Their names are: " + ', '.join(x['name'] for x in space['people']) + "."

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

