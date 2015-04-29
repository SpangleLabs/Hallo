import random

import ircbot_chk

class mod_chance:

    def fn_playball(self,args,client,destination):
        'Magic 8 ball with a NSFW twist. Format: playball'
        responses = ['Tongue Bath','Massage Breast','Give Oral','Lick Nipples','Kiss Lips','Their Choice','Spank Me','French Kiss','Massage','Striptease','Woman On Top','Self-Pleasure','Rear Entry','69','Your Choice','Booby Sex','Use Toy','Fondle','Role Play','Receive Oral']
        rand = random.randint(0,len(responses)-1)
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return responses[rand] + "."
        else:
            return '"playball" not defined. Try "/msg Hallo help commands" for a list of commands.'

