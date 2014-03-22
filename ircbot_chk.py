import time #sleeps for checks that have to send data to the server and listen for responces
import re   #for chk_swear
import difflib #for chk_destination

endl = '\r\n'

class ircbot_chk:

    def chk_op(self,server,client):
        # check if someone has op status for this bot
        client = client.lower()
        return ircbot_chk.chk_userregistered(self,server,client) and ((len(self.conf['server'][server]['ops'])!=0 and self.conf['server'][server]['ops'].count(client) > 0) or (len(self.conf['server'][server]['gods'])!=0 and self.conf['server'][server]['gods'].count(client) > 0))

    def chk_god(self,server,client):
        # check if someone has god status for this bot
        client = client.lower()
        return ircbot_chk.chk_userregistered(self,server,client) and len(self.conf['server'][server]['gods'])!=0 and self.conf['server'][server]['gods'].count(client) > 0

    def chk_userregistered(self,server,client):
        # check if a user is registered and logged in
        self.core['server'][server]['check']['userregistered'] = False
        self.base_say('INFO ' + client,[server,'nickserv'])
        for x in range(12):
            print(self.base_timestamp() + ' [' + server + "] waiting for nickserv")
            if(self.core['server'][server]['check']['userregistered']):
                print(self.base_timestamp() + ' [' + server + '] got the reply.')
                break
            time.sleep(0.5)
        return self.core['server'][server]['check']['userregistered']

    def chk_nickregistered(self,server,client):
        # check if a nick is registered
        self.core['server'][server]['check']['nickregistered'] = False
        self.base_say('INFO ' + client,[server,'nickserv'])
        for x in range(12):
            print(self.base_timestamp() + ' [' + server + '] waiting for nickserv')
            if(self.core['server'][server]['check']['nickregistered']):
                print(self.base_timestamp() + ' [' + server + '] got the reply.')
                break
            time.sleep(0.5)
        return self.core['server'][server]['check']['nickregistered']

    def chk_recipientonline(self,server,clients):
        # check if a list of recipients are online
        self.core['server'][server]['check']['recipientonline'] = ""
        self.core['server'][server]['socket'].send(('ISON ' + ' '.join(clients) + endl).encode('utf-8'))
        for a in range(6):
            print(self.base_timestamp() + ' [' + server + '] waiting for input on which recipients are online')
            if(self.core['server'][server]['check']['recipientonline'] == ""):
                time.sleep(0.5)
            else:
                print("got the list. " + self.core['server'][server]['check']['recipientonline'])
                break
        return self.core['server'][server]['check']['recipientonline'].split()

    def chk_names(self,server,channel):
        # check for a userlist of whatever channel
        self.core['server'][server]['check']['names'] = ""
        self.core['server'][server]['socket'].send(('NAMES ' + channel + endl).encode('utf-8'))
        for a in range(6):
            if(self.core['server'][server]['check']['names']==""):
                print(self.base_timestamp() + ' [' + server + '] waiting for userlist')
                time.sleep(0.5)
            else:
                print(self.base_timestamp() + ' [' + server + '] got the list: ' + self.core['server'][server]['check']['names'])
                break
        return self.core['server'][server]['check']['names'].split()

    def chk_swear(self,server,channel,message):
        'checks to see if a message has swearing, returns a 2 item list, first item is: "none", "possible", "inform" or "comment", second item is whatever swear'
        if(self.conf['server'][server]['channel'][channel]['sweardetect']):
            for swear in self.conf['server'][server]['channel'][channel]['swearlist']['possible']:
                if(re.search(swear,message,re.I)):
                    return ["possible",swear]
            for swear in self.conf['server'][server]['channel'][channel]['swearlist']['inform']:
                if(re.search(swear,message,re.I)):
                    return ["inform",swear]
            for swear in self.conf['server'][server]['channel'][channel]['swearlist']['comment']:
                if(re.search(swear,message,re.I)):
                    return ["comment",swear]
            return ["none","none"]
        else:
            return ["none","none"]

    def fnn_chk_channel(self,server,client,destchan):
        if(destchan=='*' and ircbot_chk.chk_op(self,server,client)):
            return [[destserv,chan] for chan in self.conf['server'][destserv]['channel']]
        asterix = False
        if(destchan[-1]=='*' and ircbot_chk.chk_op(self,server,client)):
            asterix = True
            destchan = destchan[:-1]
        chanlist = [[None,'No channels match this truncation.']]
        foreach(chan in self.conf['server'][destserv]['channel']):
            if(chan[:len(destchan)]==destchan):
                chanlist.append([destserv,chan])
        if(len(chanlist)==1):
            chanlist = [[None,'No channels match this truncation.']]
        elif(not asterix and len(chanlist)>2):
            chanlist = [[None,'Too many channels match this truncation.']]
        else:
            chanlist = chanlist[1:]
        if(chanlist[0][0] is not None):
            return chanlist
        else:
            closechan = difflib.get_close_matches(destchan,[chan for chan in self.conf['server'][destserv]['channel']])
            if(len(closechan)==0 or closechan[0]==''):
                return [[None,'No channel names are close to this one']]
            else:
                return [[destchan,closechan[0]]

    def chk_destination(self,server,channel,client,string):
        'Checks for valid server-channel pairs or known aliases, or close guesses, and returns proper pairs'
        if(len(string)==0):
            return [[None,'No destination given.']]
        if(string[0]=='.'):
            #alias. not ready yet
            if('alias_chan' in self.conf):
                return [[None,'No aliases are set.']]
            if(args in self.conf['alias_chan']):
                return [[None,'No alias by that name.']]
            return [[self.conf['alias_chan'][string[1:]]['server'],self.conf['alias_chan'][string[1:]]['channel']]]
        if(string[0]=='#'):
            #just specifying channel, assume the given server
            if(server in self.conf['server'] and string.lower() in self.conf['server'][server]['channel']):
                return [[server,string.lower()]]
            elif(server in self.conf['server']):
                return ircbot_chk.fnn_chk_channel(self,server,client,string)
            else:
                return [[None,'This message arrived from a server I am not on.']]
        if(',' in string):
            #comma separated, see if they're using the old swirlybracket syntax.
            if(string[0]=='{' and string[-1]=='}'):
                string = string[1:-1]
            destpair = string.split(',')
            destserv = destpair[0]
            destchan = destpair[1]
            if(destserv==''):
                destserv = server
            if(destchan==''):
                destchan = channel
            if(destserv in self.conf['server']):
                if(destchan in self.conf['server'][destserv]['channel']):
                    return [[destserv,destchan]]
                else:
                    return ircbot_chk.fnn_chk_channel(self,server,client,destchan)
            else:
                if(destserv=='*' and ircbot.chk_god(self,server,client)):
                    list = []
                    foreach(serv in self.conf['server']):
                        list = list + ircbot_chk.fnn_chk_channel(self,serv,client,destchan)
                    list = [item for item in list if item[0] is not None]
                    if(len(list)==0):
                        return [[None,'Cannot find any channels matching your specification on any server.']]
                    else:
                        return list
                asterix = False
                if(destserv[-1]=='*' and ircbot_chk_god(self,server,client)):
                    asterix = True
                    destserv = destserv[:-1]
                list = [[None,'No channels match this truncation.']]
                foreach(serv in self.conf['server']):
                    if(serv[:len(destserv)]==destserv)
                        list = list + ircbot_chk.fnn_chk_channel(self,serv,client,destchan)
                list = [item for item in list if item[0] is not None]
                list.insert(0,[None,'No channels match this truncation.'])
                if(len(list)==1):
                    list = [[None,'No servers match this truncation.']]
                elif(not asterix and len(list)>2):
                    list = [[None,'Too many servers match this truncation.']]
                else:
                    list = list[1:]
                if(list[0][0] is not None):
                    return list
                else:
                    closeserv = difflib.get_close_matches(destserv,[serv for serv in self.conf['server']])
                    if(len(closeserv)==0 or closeserv[0]==''):
                        return [[None,'No server names are close to this one.']]
                    else:
                        return ircbot_chk.fnn_chk_channel(self,closeserv[0],client,destchan)
        if(string in self.conf['server']):
            if(channel in self.conf['server'][string]['channel']):
                return [[string,channel]]
            else:
                return [[None,'There is no channel by the same name as this one on that server']]
        else:
            asterix = False
            if(string[-1]=='*' and ircbot_chk_god(self,server,client)):
                asterix = True
                string = string[:-1]
            list = [[None,'No servers match this truncation.']]
            foreach(serv in self.conf['server']):
                if(serv[:len(string)]==string and channel in self.conf['server'][serv]['channel']):
                    list.append([serv,channel])
            if(len(list)==1):
                list = [[None,'No servers match this truncation.']]
            elif(not asterix and len(list)>2):
                list = [[None,'Too many servers match this truncation']]
            if(list[0][0] is not None):
                return list
            else:
                closeserv = difflib.get_close_matches(string,[serv for serv in self.conf['server']])
                if(len(closeserv)==0 or closeserv[0]==''):
                    return [[None,'No server names are close to this one.']]
                else:
                    if(channel in self.conf['server'][closeserv[0]]['channel']):
                        return [[closeserv[0],channel]]
                    else:
                        return [[None,'No channel with the right name on that server.']]
            return [[None,'Something strange happened.']]
        #checked everything, not sure what happens now
        return [[None,'Something very strange happened.']]






