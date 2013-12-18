import time #sleeps for checks that have to send data to the server and listen for responces
import re   #for chk_swear

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

