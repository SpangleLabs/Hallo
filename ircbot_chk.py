import time #sleeps for checks that have to send data to the server and listen for responces
import re   #for chk_swear
import difflib #for chk_destination

from inc.commons import Commons

endl = '\r\n'

class ircbot_chk:

    def chk_op(self,server,client):
        # check if someone has op status for this bot
        client = client.lower()
        if('auth_op' in self.core['server'][server]):
            if(client in self.core['server'][server]['auth_op']):
                return True
            else:
                check = ircbot_chk.chk_userregistered(self,server,client) and (client in self.conf['server'][server]['ops'] or client in self.conf['server'][server]['gods'])
                if(check):
                    self.core['server'][server]['auth_op'].append(client)
                return check
        else:
            check = ircbot_chk.chk_userregistered(self,server,client) and (client in self.conf['server'][server]['ops'] or client in self.conf['server'][server]['gods'])
            if(check):
                self.core['server'][server]['auth_op'] = []
                self.core['server'][server]['auth_op'].append(client)
            return check

    def chk_god(self,server,client):
        # check if someone has god status for this bot
        client = client.lower()
        if('auth_god' in self.core['server'][server]):
            if(client in self.core['server'][server]['auth_god']):
                return True
            else:
                check = ircbot_chk.chk_userregistered(self,server,client) and client in self.conf['server'][server]['gods']
                if(check):
                    self.core['server'][server]['auth_op'].append(client)
                return check
        else:
            check = ircbot_chk.chk_userregistered(self,server,client) and client in self.conf['server'][server]['gods']
            if(check):
                self.core['server'][server]['auth_god'] = []
                self.core['server'][server]['auth_god'].append(client)
            return check

    def chk_userregistered(self,server,client):
        # check if a user is registered and logged in
        if(not self.conf['server'][server]['connected']):
            return False
        self.core['server'][server]['check']['userregistered'] = False
        self.base_say('INFO ' + client,[server,'nickserv'])
        for _ in range(12):
            print(Commons.currentTimestamp() + ' [' + server + "] waiting for nickserv")
            if(self.core['server'][server]['check']['userregistered']):
                print(Commons.currentTimestamp() + ' [' + server + '] got the reply.')
                break
            time.sleep(0.5)
        return self.core['server'][server]['check']['userregistered']

    def chk_nickregistered(self,server,client):
        # check if a nick is registered
        if(not self.conf['server'][server]['connected']):
            return False
        self.core['server'][server]['check']['nickregistered'] = False
        self.base_say('INFO ' + client,[server,'nickserv'])
        for _ in range(12):
            print(Commons.currentTimestamp() + ' [' + server + '] waiting for nickserv')
            if(self.core['server'][server]['check']['nickregistered']):
                print(Commons.currentTimestamp() + ' [' + server + '] got the reply.')
                break
            time.sleep(0.5)
        return self.core['server'][server]['check']['nickregistered']

    def chk_recipientonline(self,server,clients):
        # check if a list of recipients are online
        if(not self.conf['server'][server]['connected']):
            return []
        self.core['server'][server]['check']['recipientonline'] = ""
        self.core['server'][server]['socket'].send(('ISON ' + ' '.join(clients) + endl).encode('utf-8'))
        for _ in range(6):
            print(Commons.currentTimestamp() + ' [' + server + '] waiting for input on which recipients are online')
            if(self.core['server'][server]['check']['recipientonline'] == ""):
                time.sleep(0.5)
            else:
                print("got the list. " + self.core['server'][server]['check']['recipientonline'])
                break
        return self.core['server'][server]['check']['recipientonline'].split()

    def chk_names(self,server,channel):
        # check for a userlist of whatever channel
        if(not self.conf['server'][server]['connected']):
            return []
        self.core['server'][server]['check']['names'] = ""
        self.core['server'][server]['socket'].send(('NAMES ' + channel + endl).encode('utf-8'))
        for _ in range(6):
            if(self.core['server'][server]['check']['names']==""):
                print(Commons.currentTimestamp() + ' [' + server + '] waiting for userlist')
                time.sleep(0.5)
            else:
                print(Commons.currentTimestamp() + ' [' + server + '] got the list: ' + self.core['server'][server]['check']['names'])
                break
        return self.core['server'][server]['check']['names'].split()

    def chk_swear(self,server,channel,message):
        'checks to see if a message has swearing, returns a 2 item list, first item is: "none", "possible", "inform" or "comment", second item is whatever swear'
        if(not self.conf['server'][server]['connected']):
            return ["none","none"]
        if(channel not in self.conf['server'][server]['channel']):
            return ["none","none"]
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
            return [[server,chan] for chan in self.conf['server'][server]['channel']]
        asterix = False
        if(destchan[-1]=='*' and ircbot_chk.chk_op(self,server,client)):
            asterix = True
            destchan = destchan[:-1]
        chanlist = [[None,'No channels match this truncation.']]
        for chan in self.conf['server'][server]['channel']:
            if(chan[:len(destchan)]==destchan):
                chanlist.append([server,chan])
        if(len(chanlist)==1):
            chanlist = [[None,'No channels match this truncation.']]
        elif(not asterix and len(chanlist)>2):
            chanlist = [[None,'Too many channels match this truncation.']]
        else:
            chanlist = chanlist[1:]
        if(chanlist[0] != [[None,'No channels match this truncation.']]):
            return chanlist
        else:
            closechan = difflib.get_close_matches(destchan,[chan for chan in self.conf['server'][server]['channel']])
            if(len(closechan)==0 or closechan[0]==''):
                return [[None,'No channel names are close to this one']]
            else:
                return [[server,closechan[0]]]

    def chk_destination(self,server,channel,client,string):
        'Checks for valid server-channel pairs or known aliases, or close guesses, and returns proper pairs'
        string = string.strip()
        if(len(string)==0):
            return [[None,'No destination given.']]
        if(string[0]=='.'):
            #alias.
            string = string.lower()
            if('alias_chan' not in self.conf):
                return [[None,'No aliases are set.']]
            if(string[1:] not in self.conf['alias_chan']):
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
                    return ircbot_chk.fnn_chk_channel(self,destserv,client,destchan)
            else:
                if(destserv=='*' and ircbot_chk.chk_god(self,server,client)):
                    out_list = []
                    for serv in self.conf['server']:
                        out_list = out_list + ircbot_chk.fnn_chk_channel(self,serv,client,destchan)
                    out_list = [item for item in out_list if item[0] is not None]
                    if(len(out_list)==0):
                        return [[None,'Cannot find any channels matching your specification on any server.']]
                    else:
                        return out_list
                asterix = False
                if(destserv[-1]=='*' and ircbot_chk.chk_god(self,server,client)):
                    asterix = True
                    destserv = destserv[:-1]
                out_list = [[None,'No channels match this truncation.']]
                for serv in self.conf['server']:
                    if(serv[:len(destserv)]==destserv):
                        out_list = out_list + ircbot_chk.fnn_chk_channel(self,serv,client,destchan)
                out_list = [item for item in out_list if item[0] is not None]
                out_list.insert(0,[None,'No channels match this truncation.'])
                if(len(out_list)==1):
                    out_list = [[None,'No servers match this truncation.']]
                elif(not asterix and len(out_list)>2):
                    out_list = [[None,'Too many servers match this truncation.']]
                else:
                    out_list = out_list[1:]
                if(out_list[0] != [[None,'No channels match this truncation.']]):
                    return out_list
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
            if(string[-1]=='*' and ircbot_chk.chk_god(self,server,client)):
                asterix = True
                string = string[:-1]
            out_list = [[None,'No servers match this truncation.']]
            for serv in self.conf['server']:
                if(serv[:len(string)]==string and channel in self.conf['server'][serv]['channel']):
                    out_list.append([serv,channel])
            if(len(out_list)==1):
                out_list = [[None,'No servers match this truncation.']]
            elif(not asterix and len(out_list)>2):
                out_list = [[None,'Too many servers match this truncation']]
            if(out_list[0] != [[None,'No servers match this truncation.']]):
                return out_list
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

    def chk_msg_numbers(self,args):
        'checks that an argument is purely numbers'
        args = args.lower()
        validchars = [str(x) for x in range(10)] + ['.']
        if(args[0]=='-'):
            args = args[1:]
        for char in validchars:
            args = args.replace(char,"")
        if(args==""):
            return True
        else:
            return False

    def chk_msg_calc(self,args):
        'checks that an argument is purely numbers and calculation characters'
        args = args.lower()
        validchars = [str(x) for x in range(10)] + [".",")","^","*","x","/","%","+","-","pi","e"," ","acos(","asin(","atan(","cos(","sin(","tan(","sqrt(","log(","atanh(","acosh(","asinh(","tanh(","cosh(","sin(","gamma(","("]
        for char in validchars:
            args = args.replace(char,"")
        if(args==""):
            return True
        else:
            return False




