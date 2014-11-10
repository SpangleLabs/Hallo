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
        if(quote[-1] not in ['.','?','!']):
            quote = quote + '.'
        return quote

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
#        dragon = r''',-,- / / | ,-' _/ / / (-_ _,-' `Z_/ "#: ,-'_,-. \
#_ #' _(_-'_()\ \" | ,-6-_,--' | / "" L-'\ \,--^---v--v-._ / \ |
#\_________________,-' | \ \ Wny \ '''
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
            
    def fn_fursona(self,args,client,destination):
        'Generates your new fursona. Format: fursona'
        list_1 = ["eldritch","neon green","angelic","ghostly","scene","emo","hipster","alien","sweaty","OBSCENELY BRIGHT YELLOW","spotted","hairy","glowing","pastel pink","glittering blue","golden","shimmering red","robotic","black","goth","elegant","white","divine","striped","radioactive","red and green","slimy","slime","garbage","albino","skeleton","petite","swamp","aquatic","vampire","bright pink and yellow","mossy","stone","gray","fairy","zombie","pastel","mint green","giant","big pink","tiny pink","big white","tiny white","tiny black","translucent","glistening","glittering black","shimmering white","iridescent","glass","silver","jewel-encrusted","fuschia","purple","tiny purple","lilac","lavender","shimmering lilac","sparkling purple","tiny blue","heavenly","gilded","holy","blue and white striped","black and orange spotted","black and red","black and orange","ancient","green","purple and blue","pink and blue","candy","abyssal","floral","candle","melanistic","punk","ethereal","unholy","celestial","cyan","cream","cream and pink","cream and brown","yellow","black and pink","magenta","speckled","tiger-striped","chocolate","pastel goth","vintage","glossy black","glossy white","glossy gray","glossy blue","glossy pink","shimmery gray","glossy yellow","magma","plastic","leucistic","piebald"]
        list_2 = ["kestrel.","goat.","sheep.","dragon.","platypus.","blobfish.","hydra.","wolf.","fox.","sparkledog.","cow.","bull.","cat.","tiger.","panther.","hellhound.","spider.","beagle.","pomeranian.","whale.","hammerhead shark.","snake.","hyena.","lamb.","pony.","horse.","pup.","swan.","pigeon.","dove.","fennec fox.","fish.","rat.","possum.","hamster.","deer.","elk.","reindeer.","cheetah.","ferret.","bear.","panda.","koala.","kangaroo.","skink.","lizard.","iguana.","cerberus.","turtle.","raven.","cardinal.","bluejay.","antelope.","buffalo.","rabbit.","bunny.","frog.","newt.","salamander.","cobra.","coyote.","jellyfish.","bee.","wasp.","dinosaur.","bat.","worm.","chicken.","eel.","tiger.","sloth.","seal.","vulture.","barghest.","hedgehog.","peacock.","anglerfish.","dolphin.","liger.","llama.","alpaca.","walrus.","mantis.","ladybug.","penguin.","flamingo.","civet.","pudu.","crab.","maine coon.","fawn.","siamese.","amoeba.","owl.","unicorn.","crocodile.","alligator.","chihuahua.","great dane.","dachshund.","corgi.","rooster.","sparrow.","wyrm.","slug.","snail.","seagull.","badger.","gargoyle.","scorpion.","boa.","axolotl."]
        list_3 = ["it constantly drips with a tar-like black substance.","it enjoys performing occult rituals with friends.","it is a communist.","a golden halo floats above its head.","it wears a mcdonalds uniform because it works at mcdonalds.","it carries a nail bat.","it wears louboutin heels.","it has two heads.","it has an unknowable amount of eyes.","it drools constantly.","its tongue is bright green.","it has numerous piercings.","it is a cheerleader.","it is a farmhand.","when you see it you are filled with an ancient fear.","it wears a toga.","it is made of jelly.","it has incredibly long and luxurious fur.","it uses reddit but won't admit it.","it glows softly and gently- evidence of a heavenly being.","it is a ghost.","it dresses like a greaser.","crystals grow from its flesh.","it rides motorcycles.","it wears incredibly large and impractical sunglasses.","it instagrams its starbucks drinks.","it is a hired killer.","where its tail should be is just another head.","it dwells in a bog.","it is wet and dripping with algae.","it runs a blog dedicated to different types of planes throughout history.","it worships the moon.","it comes from a long line of royalty.","it frolics in flowery meadows.","it wears a ballerina's outfit.","it wears a neutral milk hotel t-shirt with red fishnets and nothing else.","it wears a lot of eye makeup.","it won't stop sweating.","it has far too many teeth and they are all sharp.","it is a tattoo artist.","it is shaking.","it is a witch.","it wears scarves all the time.","to look into its eyes is to peer into a distant abyss.","mushrooms grow from its skin.","its face is actually an electronic screen.","it loves to wear combat boots with cute stickers all over them.","it comes from space.","it is a knife collector.","it flickers in and out of this plane of reality.","it wishes it were a butt.","its eyes are red.","it is the most beautiful thing you have ever seen.","it loves strawberry milkshakes.","it cries all the time and can't really do much about it.","it lives alone in a dense forgotten wilderness.","it wears big christmas sweaters year-round.","it floats about a foot off of the ground.","it loves trash.","it has demonic wings.","it has a cutie mark of a bar of soap.","it is melting.","it wears opulent jewelry of gold and gemstones.","it has a hoard of bones.","it has ram horns.","it has a forked tongue.","it wears frilly dresses.","it has antlers.","it is a nature spirit.","its back is covered in candles which flicker ominously.","it wears a leather jacket with lots of patches.","it wears a snapback.","it has a tattoo that says 'yolo'.","electricity flickers through the air surrounding it.","it is a fire elemental.","it consumes only blood.","it works at an adorable tiny bakery.","it is a professional wrestler.","instead of eyes there are just more ears.","it speaks a forgotten and ancient language both disturbing and enchanting to mortal ears.","it works out.","it wishes it were a tree.","it is always blushing.","it uses ancient and powerful magic.","it loves raw meat.","it is always smiling.","it can fire lasers from its eyes.","a small rainbutt follows it everywhere.","it is made of glass.","fireflies circle it constantly.","it is always accompanied by glowing orbs of light.","it has human legs.","water drips from it constantly.","it has golden horns.","it loves gore.","it lives in a cave with its parents.","its purse costs more than most people's cars.","it always shivers even when it's not cold.","it has tentacles.","it never blinks.","it only listens to metal.","it wears a golden crown.","it wears a white sundress.","it has green hair pulled up into two buns.","its body is covered in occult sigils and runes which pulse ominously.","it loves to devour the rotting plant matter covering the forest floor.","it wears a plain white mask.","its eyes flash multiple colors rapidly.","it loves to wear nail polish but applies it messily.","it runs a jimmy carter fanblog.","it is a surfer.","it only wears hawaiian shirts.","everything it wears is made out of denim.","it has long braided hair.","it calls everybody comrade.","it lures men to their deaths with its beautiful voice.","it has braces.","it has full sleeve tattoos.","it dresses like a grandpa.","smoke pours from its mouth.","it is a makeup artist.","it dresses like a pinup girl.","it has only one large eye.","it plays the harp.","it has very long hair with many flowers in it.","it has a cyan buzzcut.","it is a garden spirit.","it has fangs capable of injecting venom.","numerous eyeballs float around it. watching. waiting.","it loves to play in the mud.","it wears a surgical mask.","its eyes are pitch black and cause those who look directly into them for too long to slowly grow older.","it wears numerous cute hairclips.","it has a very large tattoo of the 'blockbuster' logo.","it is constantly covered in honey that drips on everything and pools beneath it.","it wears a cherry-themed outfit.","it has heterochromia.","it is heavily scarred.","in place of a head it has a floating cube that glows and pulses softly.","it seems to be glitching.","it does not have organs- instead it is full of flowers.","its insides are glowing.","it is a skateboarder.","it is a superwholock blogger.","it is a skilled glass-blower.","it has a pet of the same species as itself.","it is the leader of an association of villains.","it wears a black leather outfit.","its pupils are slits.","it wears a crop top with the word OATMEAL in all caps.","it only wears crop tops and high waisted shorts.","it is always giving everyone a suspicious look.","it has a septum piercing.","instead of talking it just says numbers.","it is an internet famous scene queen.","its eyes are way too big to be normal.","it has super obvious tan lines.","it wears a maid outfit.","it is an emissary from hell.","its eyes have multiple pupils in them.","it has an impractically large sword.","it is a magical girl.","it has a scorpion tail.","it is a biologist specializing in marine invertebrates.","it runs. everywhere. all the time.","it is an esteemed fashion designer for beings with 6 or more limbs.","it wears short shorts that say CLAM.","it can't stop knitting.","it is always coated in glitter.","it worships powerful dolphin deities.","it has slicked back hair.","it has a thick beard.","it has a long braided beard plaited with ribbons.","it is a viking.","it wears a parka.","its outfit is completely holographic.","it wears an oversized pearl necklace.","it has stubble.","it carries a cellphone with a ridiculous amount of charms and keychains.","it wears crocs.","it has a hoard of gems and gold that was pillaged from innocent villagers.","it robs banks.","its facial features are constantly shifting.","it works as a librarian in hell.","it wears a fedora."]
        list_4 = ["it constantly drips with a tar-like black substance.","it enjoys performing occult rituals with friends.","it is a communist.","a golden halo floats above its head.","it wears a mcdonalds uniform because it works at mcdonalds.","it carries a nail bat.","it wears louboutin heels.","it has two heads.","it has an unknowable amount of eyes.","it drools constantly.","its tongue is bright green.","it has numerous piercings.","it is a cheerleader.","it is a farmhand.","when you see it you are filled with an ancient fear.","it wears a toga.","it is made of jelly.","it has incredibly long and luxurious fur.","it uses reddit but won't admit it.","it glows softly and gently- evidence of a heavenly being.","it is a ghost.","it dresses like a greaser.","crystals grow from its flesh.","it rides motorcycles.","it wears incredibly large and impractical sunglasses.","it instagrams its starbucks drinks.","it is a hired killer.","where its tail should be is just another head.","it dwells in a bog.","it is wet and dripping with algae.","it runs a blog dedicated to different types of planes throughout history.","it worships the moon.","it comes from a long line of royalty.","it frolics in flowery meadows.","it wears a ballerina's outfit.","it wears a neutral milk hotel t-shirt with red fishnets and nothing else.","it wears a lot of eye makeup.","it won't stop sweating.","it has far too many teeth and they are all sharp.","it is a tattoo artist.","it is shaking.","it is a witch.","it wears scarves all the time.","to look into its eyes is to peer into a distant abyss.","mushrooms grow from its skin.","its face is actually an electronic screen.","it loves to wear combat boots with cute stickers all over them.","it comes from space.","it is a knife collector.","it flickers in and out of this plane of reality.","it wishes it were a butt.","its eyes are red.","it is the most beautiful thing you have ever seen.","it loves strawberry milkshakes.","it cries all the time and can't really do much about it.","it lives alone in a dense forgotten wilderness.","it wears big christmas sweaters year-round.","it floats about a foot off of the ground.","it loves trash.","it has demonic wings.","it has a cutie mark of a bar of soap.","it is melting.","it wears opulent jewelry of gold and gemstones.","it has a hoard of bones.","it has ram horns.","it has a forked tongue.","it wears frilly dresses.","it has antlers.","it is a nature spirit.","its back is covered in candles which flicker ominously.","it wears a leather jacket with lots of patches.","it wears a snapback.","it has a tattoo that says 'yolo'.","electricity flickers through the air surrounding it.","it is a fire elemental.","it consumes only blood.","it works at an adorable tiny bakery.","it is a professional wrestler.","instead of eyes there are just more ears.","it speaks a forgotten and ancient language both disturbing and enchanting to mortal ears.","it works out.","it wishes it were a tree.","it is always blushing.","it uses ancient and powerful magic.","it loves raw meat.","it is always smiling.","it can fire lasers from its eyes.","a small rainbutt follows it everywhere.","it is made of glass.","fireflies circle it constantly.","it is always accompanied by glowing orbs of light.","it has human legs.","water drips from it constantly.","it has golden horns.","why is it always covered in blood?","it loves gore.","it lives in a cave with its parents.","its purse costs more than most people's cars.","it always shivers even when it's not cold.","it has tentacles.","it never blinks.","it only listens to metal.","it wears a golden crown.","it wears a white sundress.","it has green hair pulled up into two buns.","its body is covered in occult sigils and runes which pulse ominously.","it loves to devour the rotting plant matter covering the forest floor.","it wears a plain white mask.","its eyes flash multiple colors rapidly.","you are afraid.","it loves to wear nail polish but applies it messily.","it runs a jimmy carter fanblog.","it is a surfer.","it only wears hawaiian shirts.","everything it wears is made out of denim.","it has long braided hair.","it calls everybody comrade.","it lures men to their deaths with its beautiful voice.","it has braces.","it has full sleeve tattoos.","it dresses like a grandpa.","smoke pours from its mouth.","it is a makeup artist.","it dresses like a pinup girl.","it has only one large eye.","it plays the harp.","it has very long hair with many flowers in it.","it has a cyan buzzcut.","it is a garden spirit.","it has fangs capable of injecting venom.","numerous eyeballs float around it. watching. waiting.","it loves to play in the mud.","it wears a surgical mask.","its eyes are pitch black and cause those who look directly into them for too long to slowly grow older.","it wears numerous cute hairclips.","it has a very large tattoo of the 'blockbuster' logo.","it is constantly covered in honey that drips on everything and pools beneath it.","it wears a cherry-themed outfit.","it has heterochromia.","it is heavily scarred.","in place of a head it has a floating cube that glows and pulses softly.","it seems to be glitching.","its insides are glowing.","it does not have organs- instead it is full of flowers.","it is a skateboarder.","it is a superwholock blogger.","it is a skilled glass-blower.","it has a pet of the same species as itself.","it is the leader of an association of villains.","it wears a black leather outfit.","its pupils are slits..","it wears a crop top with the word OATMEAL in all caps.","it only wears crop tops and high waisted shorts.","it is always giving everyone a suspicious look.","it has a septum piercing.","its hair is beehive style. not an actual beehive.","instead of talking it just says numbers.","it has a halo. over its ass.","it is an internet famous scene queen.","its eyes are way too big to be normal.","it has super obvious tan lines.","it wears a maid outfit.","it is an emissary from hell.","its eyes have multiple pupils in them.","there are scorpions everywhere.","it has an impractically large sword.","it is a magical girl.","it has a scorpion tail.","it is a biologist specializing in marine invertebrates.","it runs. everywhere. all the time.","it is an esteemed fashion designer for beings with 6 or more limbs.","it wears short shorts that say CLAM.","it can't stop knitting.","it is always coated in glitter.","it worships powerful dolphin deities.","it has slicked back hair.","it has a thick beard.","it has a long braided beard plaited with ribbons.","it is a viking.","it wears a parka.","its outfit is completely holographic.","it wears an oversized pearl necklace.","it has stubble.","it carries a cellphone with a ridiculous amount of charms and keychains.","Welcome to Hell! Welcome to Hell!","it wears crocs.","it has a hoard of gems and gold that was pillaged from innocent villagers.","it robs banks and its partner in crime is the next fursona you generate.","its facial features are constantly shifting.","it works as a librarian in hell.","it wears a fedora."]
        result = "Your new fursona is: "+list_1[random.randint(0,len(list_1)-1)]+" "+list_2[random.randint(0,len(list_2)-1)]+" "+list_3[random.randint(0,len(list_3)-1)]+" "+list_4[random.randint(0,len(list_4)-1)]
        return result

        



