import random
import pickle

import mod_euler
import ircbot_chk

class mod_chance:

    def fn_thought_for_the_day(self,args,client,destination):
        'WH40K Thought for the day. Format: thought_for_the_day'
        thoughts = mod_euler.mod_euler.fnn_euler_readfiletolist(self,'store/WH40K_ToTD2.txt')
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
        words = mod_euler.mod_euler.fnn_euler_readfiletolist(self,'store/ouija_wordlist.txt')
        numwords = random.randint(1,3)
        string = "I'm getting a message from the other side..."
        for _ in range(numwords):
            rand = random.randint(0,len(words)-1)
            string = string + ' ' + words[rand]
        return string + "."

    def fn_scriptures(self,args,client,destination):
        'Recites a passage from the Amarr scriptures. Format: scriptures'
        scriptures = pickle.load(open('store/scriptures.p','rb'),errors='ignore')
        rand = random.randint(0,len(scriptures)-1)
        if(scriptures[rand][-1] not in ['.','!','?']):
            scriptures[rand] = scriptures[rand] + "."
        return scriptures[rand]

