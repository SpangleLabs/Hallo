import time
from subprocess import call
from threading import Thread

import ircbot_chk
import mod_idlechan    #for idle channel functions
import mod_conversion
import hallobase_ctrl

endl = '\r\n'

class ircbot_on:

    def on_init(self):
        pass # override this method to do any startup code

    def on_ping(self,server,code):
        # handle pings from servers.
   #     call(["beep","-f 25","-l 50"])
   #     time.sleep(0.15)
   #     call(["beep","-f 40","-l 40"])
        pass

    def on_join(self,server,client,channel):
        # handle join events from other users (or from hallo!)
        if('auto_list' in self.conf['server'][server]['channel'][channel]):
            for entry in self.conf['server'][server]['channel'][channel]['auto_list']:
                if(client.lower()==entry['user']):
                    for x in range(7):
                        if(ircbot_chk.ircbot_chk.chk_userregistered(self,server,client)):
                            self.core['server'][server]['socket'].send(('MODE ' + channel + ' ' + entry['flag'] + ' ' + client + endl).encode('utf-8'))
                            break
                        time.sleep(5)
        if(client.lower() == self.conf['server'][server]['nick'].lower()):
            self.conf['server'][server]['channel'][channel]['in_channel'] = True
            namesonline = ircbot_chk.ircbot_chk.chk_names(self,server,channel)
            namesonline = [x.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','').lower() for x in namesonline]
            self.core['server'][server]['channel'][channel]['user_list'] = namesonline
            if('auto_list' in self.conf['server'][server]['channel'][channel]):
                for entry in self.conf['server'][server]['channel'][channel]['auto_list']:
                    if(entry['user'] in namesonline):
                        for x in range(7):
                            if(ircbot_chk.ircbot_chk.chk_userregistered(self,server,entry['user'])):
                                self.core['server'][server]['socket'].send(('MODE ' + channel + ' ' + entry['flag'] + ' ' + entry['user'] + endl).encode('utf-8'))
                                break
                            time.sleep(5)
        else:
            self.core['server'][server]['channel'][channel]['user_list'].append(client.lower())

    def on_part(self,server,client,channel,args):
        #pass # override this method to handle PART events from other users
        self.core['server'][server]['channel'][channel]['user_list'].remove(client.lower())
        stillonserver = False
        for channel_server in self.core['server'][server]['channel']:
            if(client.lower() in self.core['server'][server]['channel'][channel_server]['user_list']):
                stillonserver = True
        if(not stillonserver):
            if(client.lower() in self.core['server'][server]['auth_op']):
                self.core['server'][server]['auth_op'].remove(client.lower())
            if(client.lower() in self.core['server'][server]['auth_god']):
                self.core['server'][server]['auth_god'].remove(client.lower())

    def on_quit(self,server,client,args):
        #pass # override this method to handle QUIT events from other users
        for channel in self.conf['server'][server]['channel']:
            if(client.lower() in self.core['server'][server]['channel'][channel]['user_list']):
                self.core['server'][server]['channel'][channel]['user_list'].remove(client.lower())
        if('auth_op' in self.core['server'][server] and client.lower() in self.core['server'][server]['auth_op']):
            self.core['server'][server]['auth_op'].remove(client.lower())
        if('auth_god' in self.core['server'][server] and client.lower() in self.core['server'][server]['auth_god']):
            self.core['server'][server]['auth_god'].remove(client.lower())

    def on_mode(self,server,client,channel,mode,args):
         #pass # override this method to handle MODE changes
        if(mode=='-k'):
            self.conf['server'][server]['channel'][channel]['pass'] = ''
        elif(mode=='+k'):
            self.conf['server'][server]['channel'][channel]['pass'] = args

    def on_ctcp(self,server,client,args):
        # handle ctcp messages and events to privmsg
        if(args.lower()=='version'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01' + endl).encode('utf-8'))
        elif(args.lower()=='time'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01TIME Fribsday 15 Nov 2024 ' + str(time.gmtime()[3]+100).rjust(2,'0') + ':' + str(time.gmtime()[4]+20).rjust(2,'0') + ':' + str(time.gmtime()[5]).rjust(2,'0') + 'GMT\x01' + endl).encode('utf-8'))
        elif(len(args)>4 and args[0:4].lower()=='ping'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01PING ' + args[5:] + '\x01' + endl).encode('utf-8'))
        elif(len(args)>=8 and args[0:8].lower()=='userinfo'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + " :\x01Hello, I'm hallo, I'm a robot who does a few different things, mostly roll numbers and choose things, occassionally giving my input on who is the best pony. dr-spangle built me, if you have any questions he tends to be better at replying than I.\x01" + endl).encode('utf-8'))
        elif(len(args)>=10 and args[0:10].lower()=='clientinfo'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01VERSION, NOTICE, TIME, USERINFO and obviously CLIENTINFO are supported.\x01' + endl).encode('utf-8'))

    def on_pm(self,server,client,destination,message):
        pass # override this method to handle messages alternately

    def on_notice(self,server,client,channel,args):
        # handle notices
        if(self.core['server'][server]['connected'] == False):
            self.core['server'][server]['connected'] = True
            print(self.base_timestamp() + ' [' + server + "] ok we're connected now.")
        if('endofmessage' in args.replace(' ','').lower() and self.core['server'][server]['motdend'] == False):
            self.core['server'][server]['motdend'] = True
        if(any(nickservmsg in args.replace(' ','').lower() for nickservmsg in self.conf['nickserv']['online']) and client.lower()=='nickserv' and self.core['server'][server]['check']['userregistered'] == False):
            self.core['server'][server]['check']['userregistered'] = True
        if(any(nickservmsg in args.replace(' ','').lower() for nickservmsg in self.conf['nickserv']['registered']) and client.lower()=='nickserv' and self.core['server'][server]['check']['nickregistered'] == False):
            self.core['server'][server]['check']['nickregistered'] = True
        pass # override this method to handle notices alternatively

    def on_nickchange(self,server,client,newnick):
        # handle people changing their nick
        for channel in self.conf['server'][server]['channel']:
            if(client.lower() in self.core['server'][server]['channel'][channel]['user_list']):
                self.core['server'][server]['channel'][channel]['user_list'].remove(client.lower())
                self.core['server'][server]['channel'][channel]['user_list'].append(newnick.lower())
        if(client == self.conf['server'][server]['nick']):
            self.conf['server'][server]['nick'] = newnick
        if(client.lower() in self.core['server'][server]['auth_op']):
            self.core['server'][server]['auth_op'].remove(client.lower())
            self.core['server'][server]['auth_op'].append(newnick.lower())
        if('auth_god' in self.core['server'][server] and client.lower() in self.core['server'][server]['auth_god']):
            self.core['server'][server]['auth_god'].remove(client.lower())
            self.core['server'][server]['auth_god'].append(newnick.lower())
        for channel in self.conf['server'][server]['channel']:
            if('auto_list' in self.conf['server'][server]['channel'][channel]):
                for entry in self.conf['server'][server]['channel'][channel]['auto_list']:
                    if(newnick == entry['user']):
                        for x in range(7):
                            if(ircbot_chk.ircbot_chk.chk_userregistered(self,server,newnick)):
                                self.core['server'][server]['socket'].send(('MODE ' + channel + ' ' + entry['flag'] + ' ' + newnick + endl).encode('utf-8'))
                                break
                            time.sleep(5)

    def on_invite(self,server,client,channel):
        if(ircbot_chk.ircbot_chk.chk_op(self,server,client)):
            hallobase_ctrl.hallobase_ctrl.fn_join(self,channel,client,[server,''])
        pass # override to do something on invite

    def on_kick(self,server,client,channel,message):
        self.core['server'][server]['channel'][channel]['user_list'].remove(client.lower())
        if(client == self.conf['server'][server]['nick']):
            self.conf['server'][server]['channel'][channel]['in_channel'] = False

    def on_numbercode(self,server,code,data):
        #handle 3 digit number codes sent by servers.
        if(code == "376"):
            self.core['server'][server]['motdend'] = True
        elif(code == "303"):
            self.core['server'][server]['check']['recipientonline'] = ':'.join(data.split(':')[2:])
            if(self.core['server'][server]['check']['recipientonline']==''):
                self.core['server'][server]['check']['recipientonline'] = ' '
        elif(code == "353"):
            #This is a NAMES request reply, tells you who is in a channel
            channel = data.split(':')[1].split()[-1].lower()
            self.core['server'][server]['check']['names'] = ':'.join(data.split(':')[2:])
            self.core['server'][server]['channel'][channel]['user_list'] = [nick.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','').lower() for nick in self.core['server'][server]['check']['names'].split()]

    def on_rawdata(self,server,data,unhandled):
        pass # override this method to do general data handling

    def on_coreloop(self):
        'This function is ran once every 0.1 seconds.'
        servers = 0
        # loop through all servers, to do per-seerver tasks
        #print('aaa')
        for server in self.conf['server']:
            if(self.conf['server'][server]['connected']):
                servers = servers+1
            # if you're supposed to be connected, but have pinged out, reconnect
        #    print('aab' + server)
            if('reconnect' in self.core['server'][server] and self.core['server'][server]['reconnect']):
                print("TIMED OUT FROM " + server + ", RECONNECTING.")
                self.core['server'][server]['reconnect'] = False
                self.core['server'][server]['open'] = False
                self.core['server'][server]['socket'].close()
                time.sleep(1)
                del self.core['server'][server]
                self.core['server'][server] = {}
                time.sleep(1)
                Thread(target=self.base_run, args=(server,)).start()
            # if you're connected, check each channel, if you're in any channels there, check for idlechan activation.
  #          print('aac' + server)
            if(self.conf['server'][server]['connected']):
                for channel in self.conf['server'][server]['channel']:
                    if(self.conf['server'][server]['channel'][channel]['in_channel']):
                        if('idle_time' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['idle_time']!=0 and self.core['server'][server]['channel'][channel]['last_message']!=0 and (int(time.time())-self.core['server'][server]['channel'][channel]['last_message'])>self.conf['server'][server]['channel'][channel]['idle_time']):
                            print("channel idle")
                            self.core['server'][server]['channel'][channel]['last_message'] = int(time.time())
                            out = mod_idlechan.mod_idlechan.fnn_idlechan(self,self.conf['server'][server]['channel'][channel]['idle_args'],'',[server,channel])
                            if(out is not None):
                                self.base_say(out,[server,channel])
        #    print('aad' + server)
        #if not connected to any servers, shut down
        #print('bbb')
        if(servers==0):
            self.base_close()
        if('convert_currency_update' not in self.core or (time.time()-self.core['convert_currency_update'])>3600):
            self.core['convert_currency_update'] = time.time()
            mod_conversion.mod_conversion.fn_convert_currency_update(self,'','',['',''])
            print('updated currencies')
  #      megahalclose = []
  #      #print('ccc')
  #      for filename in self.megahal:
  #          if((int(time.time())-self.megahal[filename]['last_used'])>600):
  #              megahalclose.append(filename)
  #      for filename in megahalclose:
  #          self.megahal[filename]['brain'].sync()
  #          self.megahal[filename]['brain'].close()
  #          del self.megahal[filename]
  #          print("Closed megahal brain: " + filename)
  #      del megahalclose
  #      print('ddd')


