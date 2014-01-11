

class hallobase_silly():

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
        'turn on longcat function.  Use with caution!'
        if(destination[1].lower() == '#ukofequestria'):
            return 'Longcat cannot be activated here, sorry.'
        else:
            if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                hallobase.longcat = True
                return 'Longcat enabled.  Use "longcat_off" to turn it off.'

    def fn_longcat_off(self, args, client, destination):
        'Turn off longcat functon.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            hallobase.longcat = False
            return 'Longcat disabled.  Use "longcat_on" to turn it on.'

    def fn_longcat(self, args, client, destination):
        'Make a longcat!'
        if(destination[1].lower() == '#ukofequestria'):
            return 'Sorry, longcat is not available here.'
        else:
            if(hallobase.longcat):
                if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
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

    def fn_pony_ep(self, args, client, destination):
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

    def fn_is(self,args,client,destination):
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

    def fn_cupcake(self, args, client, destination):
        'Gives out cupcakes (much better than muffins.)'
        online = ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],args.split()[0])
        if(online==' ' or online==''):
            return 'No one called "' + args.split()[0] + '" is online.'
        else:
            if(len(args.split()) >= 2):
                return '\x01ACTION gives ' + args.split()[0] + ' a ' + ' '.join(args.split()[1:]) + ' cupcake, from ' + client + '\x01'
            else:
                return '\x01ACTION gives ' + args.split()[0] + ' a cupcake, from ' + client + '\x01'

    def fn_silence_the_rabble(self,args,client,destination):
        'ETD only. deops all but D000242 and self. sets mute.'
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
        if('spangle' in client.lower()):
            return 'ddddoooooooooooooooooooooffffffffff.'
        if(rand==0):
            return 'doof'
        elif(rand==1):
            return 'doooooof'
        else:
            return 'ddddoooooooooooooooooooooffffffffff.'

    def fn_thought_for_the_day(self,args,client,destination):
        'WH40K Thought for the day.'
        thoughts = euler.euler.fnn_euler_readfiletolist(self,'store/WH40K_ToTD2.txt')
        rand = random.randint(0,len(thoughts)-1)
        return '"' + thoughts[rand] + '"'

    def fn_playball(self,args,client,destination):
        'Magic 8 ball.'
        responses = ['Tongue Bath','Massage Breast','Give Oral','Lick Nipples','Kiss Lips','Their Choice','Spank Me','French Kiss','Massage','Striptease','Woman On Top','Self-Pleasure','Rear Entry','69','Your Choice','Booby Sex','Use Toy','Fondle','Role Play','Receive Oral']
        rand = random.randint(0,len(responses)-1)
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return responses[rand]
        else:
            return '"playball" not defined. Try "/msg Hallo help commands" for a list of commands.'

    def fn_ouija(self,args,client,destination):
        'Ouija board function. "Ouija board" is copyright Hasbro.'
        words = euler.euler.fnn_euler_readfiletolist(self,'store/ouija_wordlist.txt')
        numwords = random.randint(1,3)
        string = "I'm getting a message from the other side..."
        for x in range(numwords):
            rand = random.randint(0,len(words)-1)
            string = string + ' ' + words[rand]
        return string

    def fn_scriptures(self,args,client,destination):
        'Recites a passage from the Amarr scriptures.'
        scriptures = pickle.load(open('store/scriptures.p','rb'))
        rand = random.randint(0,len(scriptures)-1)
        return scriptures[rand]

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
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
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


