import random
import re
import pickle

import mod_euler
import ircbot_chk

class mod_chance:

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

    def fn_foof(self,args,client,destination):
        'FOOOOOOOOOF. Format: foof'
        rand = random.randint(0,2)
        if(rand==0):
            return 'doof'
        elif(rand==1):
            return 'doooooof'
        else:
            if(random.randint(0,20)==15):
                self.base_say('powering up...',destination);
                time.sleep(5);
                return 'd' * 100 + 'o' * 1000 + 'f' * 200 + '!' * 50
            else:
                return 'ddddoooooooooooooooooooooffffffffff.'

    def fn_thought_for_the_day(self,args,client,destination):
        'WH40K Thought for the day. Format: thought_for_the_day'
        thoughts = euler.euler.fnn_euler_readfiletolist(self,'store/WH40K_ToTD2.txt')
        rand = random.randint(0,len(thoughts)-1)
        if(thoughts[rand][-1] not in ['.','!','?']):
            thoughts[rand] = thoughts[rand] + "."
        return '"' + thoughts[rand] + '"'

    def fn_playball(self,args,client,destination):
        'Magic 8 ball with a NSFW twist. Format: playball'
        responses = ['Tongue Bath','Massage Breast','Give Oral','Lick Nipples','Kiss Lips','Their Choice','Spank Me','French Kiss','Massage','Striptease','Woman On Top','Self-Pleasure','Rear Entry','69','Your Choice','Booby Sex','Use Toy','Fondle','Role Play','Receive Oral']
        rand = random.randint(0,len(responses)-1)
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return responses[rand] + "."
        else:
            return '"playball" not defined. Try "/msg Hallo help commands" for a list of commands.'

    def fn_ouija(self,args,client,destination):
        'Ouija board function. "Ouija board" is copyright Hasbro. Format: ouija <message>'
        words = euler.euler.fnn_euler_readfiletolist(self,'store/ouija_wordlist.txt')
        numwords = random.randint(1,3)
        string = "I'm getting a message from the other side..."
        for x in range(numwords):
            rand = random.randint(0,len(words)-1)
            string = string + ' ' + words[rand]
        return string + "."

    def fn_scriptures(self,args,client,destination):
        'Recites a passage from the Amarr scriptures. Format: scriptures'
        scriptures = pickle.load(open('store/scriptures.p','rb'))
        rand = random.randint(0,len(scriptures)-1)
        if(scriptures[rand][-1] not in ['.','!','?']):
            scriptures[rand] = scriptures[rand] + "."
        return scriptures[rand]

