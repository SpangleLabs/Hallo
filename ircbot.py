# ircbot.py
# ircbot.py
# Ben Pringle made the base, it was rotten, dr-spangle made it work.
#
# A superclass designed for making Internet Relay Chat bots using Python.
# Extend it and define new methods for added function!

#socket connets to the server
#time gets time for timestamps and does sleep
#os makes directories for logs, and gets the process ID
#sys is used to kill itself
#thread is used for multithreading
#re is used for regex, for sweardetect
#pickle is used to store the config, also scriptures
#pprint is used to view the config
#importlib is used to import modules on the fly, hopefully
#copy is used to copy the self.conf variable
import socket, time, os, sys, _thread, re, pickle, pprint, importlib, copy
from threading import Thread
import collections
import imp
#from megahal import *
import hashlib
import random

import hallobase
import passive
import idlechan
import ircbot_on
import ircbot_base
import ircbot_chk

endl = '\r\n' # constant for ease/readability

class ircbot:

    def __init__(self):
        # connect
        ircbot_on.ircbot_on.on_init(self)
#        self.base_start()
  #      self.megahal = MegaHAL()

    def base_timestamp(self):
        # return the timestamp, e.g. [05:21:42]
        return '[' + str(time.gmtime()[3]).rjust(2,'0') + ':' + str(time.gmtime()[4]).rjust(2,'0') + ':' + str(time.gmtime()[5]).rjust(2,'0') + ']'
    
    def base_addlog(self,msg,destination):
        # log a message for future reference
        if(not os.path.exists('logs/')):
            os.makedirs('logs/')
        if(not os.path.exists('logs/' + destination[0])):
            os.makedirs('logs/' + destination[0])
        if(not os.path.exists('logs/' + destination[0] + '/' + destination[1])):
            os.makedirs('logs/' + destination[0] + '/' + destination[1])
        # date is the file name
        filename = str(time.gmtime()[0]).rjust(4,'0') + '-' + str(time.gmtime()[1]).rjust(2,'0') + '-' + str(time.gmtime()[2]).rjust(2,'0') + '.txt'
        # open and write the message
        log = open('logs/' + destination[0] + '/' + destination[1] + '/' + filename, 'a')
        log.write(msg + '\n')
        log.close()
        
    def base_close(self):
        # disconnect
        for server in self.conf['server']:
            self.base_disconnect(server)
        pickle.dump(self.conf,open(self.configfile,"wb"))
        self.open = False

    def base_disconnect(self,server):
        for channel in self.conf['server'][server]['channel']:
        #    self.base_say('Daisy daisy give me your answer do...',[server,channel])
            if(self.conf['server'][server]['channel'][channel]['in_channel'] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' Hallo has quit.',[server,channel])
        #    time.sleep(1)
        if(self.core['server'][server]['open']):
            self.core['server'][server]['socket'].send(('QUIT :Daisy daisy give me your answer do...' + endl).encode('utf-8'))
            self.core['server'][server]['socket'].close()
        #    self.conf['server'][server]['connected'] = False
            self.core['server'][server]['open'] = False

    def base_say(self,msg,destination,notice=False):
        # if the connection is open...
        #if not self.open: return
        # send the message, accounting for linebreaks
        maxlength = 450 # max message length, inc channel name.
        command = 'PRIVMSG'
        if(notice):
            command = 'NOTICE'
        if(self.open and self.core['server'][destination[0]]['open']):
            if(destination[1][0] == '#' and self.conf['server'][destination[0]]['channel'][destination[1]]['caps']):
                msg = msg.upper()
            for n, line in enumerate(msg.split('\n')):
                if((len(line)+len(destination[1]))>maxlength):
                    linefirst = line[:(maxlength-3-len(destination[1]))] + '...'
                    line = line[(maxlength-3-len(destination[1])):]
                    print(self.base_timestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + linefirst)
                    self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + linefirst + endl).encode('utf-8'))
                    while((len(line)+len(destination[1]))>(maxlength-3)):
                        linechunk = '...' + line [:(maxlength-6-len(destination[1]))] + '..'
                        line = line[(maxlength-6-len(destination[1])):]
                        print(self.base_timestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + linechunk)
                        self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + linechunk + endl).encode('utf-8'))
                    lineend = '...' + line
                    print(self.base_timestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + lineend)
                    self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + lineend + endl).encode('utf-8'))
                else:
                    print(self.base_timestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + line)
                    self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + line + endl).encode('utf-8'))
                if(destination[1][0] != '#' or self.conf['server'][destination[0]]['channel'][destination[1]]['logging']):
                    self.base_addlog(self.base_timestamp() + ' <' + self.conf['server'][destination[0]]['nick'] + '>: ' + line,destination)
                # avoid flooding
                if n % 5 == 0:
                    time.sleep(2)

    def base_parse(self,server,data):
        # take a line of data from irc server's socket and process it
        nick = self.conf['server'][server]['nick']
        data = data.replace("\r","")
        unhandled = False
        if(self.core['server'][server]['lastping']!=0 and self.conf['server'][server]['pingdiff']==600):
            self.conf['server'][server]['pingdiff'] = int(time.time())-self.core['server'][server]['lastping']
        self.core['server'][server]['lastping'] = int(time.time())
        if(len(data) < 5 or (data[0] != ":" and data[0:4] != "PING")):
            #the above basically means the message is invalid, those are the only things a valid line can start with. so ditch to a logfile
            if(len(data) >= 5):
            #there's no point logging blank data sent to hallo. just log the rest.
                logbrokendata = open('logs/brokendata.txt','a')
                logbrokendata.write(server + ":: " + data.replace('\x01','\\0x01') + '\n---\n')
                logbrokendata.close()
        elif('PING' == data.split()[0]):
            # return pings so we don't get timed out
            print(self.base_timestamp() + ' [' + server + '] PING')
            self.core['server'][server]['socket'].send(('PONG ' + data.split()[1] + endl).encode('utf-8'))
        elif('PRIVMSG' == data.split()[1]):
            message = ':'.join(data.split(':')[2:]).replace(endl, '')
            # parse out the sender
            client = data.split('!')[0].replace(':', '')
            # parse out where the data went to (e.g. channel or pm to hallo)
            destination = data.split()[2].lower()
            # test for private message, public message, ctcp or command (cmdcln is commandcolon, which says if it is nick then a colon, which is a sure sign it's a command, not a mention.)
            msg_pm = destination.lower() == nick.lower()
            msg_pub = not msg_pm
            msg_cmd = message[0:len(nick)].lower() == nick.lower()
            msg_ctcp = len(data.split(':')[2]) > 0 and data.split(':')[2][0] == '\x01'
            if(msg_pub):
                if(destination not in self.core['server'][server]['channel']):
                    self.core['server'][server]['channel'][destination] = {}
                self.core['server'][server]['channel'][destination]['last_message'] = int(time.time())
            if(msg_cmd):
                ignore_list = []
                if('ignore_list' in self.conf['server'][server]['channel'][destination]):
                    ignore_list = self.conf['server'][server]['channel'][destination]['ignore_list']
                if(client.lower() in ignore_list):
                    msg_cmd = False
            #command colon variable, if command is followed by a colon and command doesn't exist, throw an error
            msg_cmdcln = False
            # print and a clean version of the message
            print(self.base_timestamp() + ' [' + server + '] ' + destination + ' <' + client + '> ' + message)
            # if it's a private message, answer to the client, not to yourself
            if msg_pm:
                destination = client
            #log the message
            if(msg_pm or self.conf['server'][server]['channel'][destination]['logging']):
                self.base_addlog(self.base_timestamp() + ' <' + client + '> ' + message, [server,msg_pm and client or destination])
            # if it's a public message, parse out the prefixed nick and clean up added whitespace/colons
            if msg_cmd:
                message = message[len(nick):]
                if(len(message)>=1):
                    if(message[0] == ','):
                        message = message[1:]
                    if(message[0] == ':'):
                        message = message[1:]
                        msg_cmdcln = True
                    while(message[0] == ' ' and len(message)>=1):
                        message = message[1:]
            # now handle functions!
            if msg_ctcp:
                client = data.split('!')[0][1:].lower()
                args = ':'.join(data.split(':')[2:])[1:-1]
                print(self.base_timestamp() + ' [' + server + '] The above was a ctcp one.')
                ircbot_on.ircbot_on.on_ctcp(self,server,client,args)
            elif msg_cmd or msg_pm:
                if(len(message) > 0):
                    function = message.split()[0].lower()
                else:
                    function = ''.lower()
                args = message[len(function):]
                # parse out leading whitespace
                if(len(args)>=1):
                    while(len(args)>=1 and args[0] in [' ',',']):
                        args = args[1:]
                #Encase functions in error handling, because programmers might make functions which are a tad crashy
           #     found = False
                try:
                    functions = []
                    for module in self.modules:
                        functions = functions + dir(getattr(__import__(module),module))
                    privmsg = self.conf['function']['default']['privmsg']
                    if('fn_' + function in self.conf['function'] and 'privmsg' in self.conf['function']['fn_' + function]):
                        privmsg = self.conf['function']['fn_' + function]['privmsg']
                    for func in functions:
                        if('fn_' + function==func or (func[:3]=='fn_' and 'fn_' + function=='fn_' + func[3:].replace('_',''))):
                            function = func[3:]
                    if('fn_' + function in functions and (not msg_pm or privmsg)):
                        method = False
                        addonmodule = False
                        if(hasattr(self,'fn_' + function)):
                            method = getattr(self,'fn_' + function)
                        if(not isinstance(method, collections.Callable)):
                            for module in self.modules:
                                if(hasattr(__import__(module),module) and hasattr(getattr(__import__(module),module),'fn_' + function)):
                                    method = getattr(getattr(__import__(module),module),'fn_' + function)
                                    addonmodule = True
                                if(isinstance(method,collections.Callable)):
                                    break
                        if(isinstance(method, collections.Callable)):
                            #check if the function has been disabled
                            disabled = False
                            disabled = self.conf['function']['default']['disabled']
                            if('fn_' + function in self.conf['function'] and 'disabled' in self.conf['function']['fn_' + function]):
                                disabled = self.conf['function']['fn_' + function]['disabled']
                            if(disabled):
                                out = "This function has been disabled, sorry"
                            else:
                                time_delay = 0
                                time_delay = self.conf['function']['default']['time_delay']
                                if('fn_' + function in self.conf['function'] and 'time_delay' in self.conf['function']['fn_' + function]):
                                    time_delay = self.conf['function']['fn_' + function]['time_delay']
                                last_used = 0
                                if('fn_' + function in self.core['function'] and 'last_used' in self.core['function']['fn_' + function]):
                                    last_used = self.core['function']['fn_' + function]['last_used']
                                if(last_used!=0 and time_delay!=0 and (int(time.time())-last_used)<time_delay):
                                    out = "You're trying to use this function too fast after its last use, sorry. Please wait."
                                else:
                                    if(addonmodule):
                                        #this part wants to be changed to start another thread I guess, then this thread can monitor it.
                                        #info needed will be max run time (loop for that long before check if it's dead (or replied) and then kill it.)
                                        #also have to check processor and ram usage, I guess
                                        #will need to get the id of the thread I just started, too
                                        out = str(method(self,args,client,[server,destination]))
                                    else:
                                        out = str(method(args,client,[server,destination]))
                                    #record the time it was used.
                                    if('fn_' + function not in self.core['function']):
                                        self.core['function']['fn_' + function] = {}
                                    self.core['function']['fn_' + function]['last_used'] = int(time.time())
                            #check where this function is meant to send its answer to, and how
                            return_to = self.conf['function']['default']['return_to']
                            if('fn_' + function in self.conf['function'] and 'return_to' in self.conf['function']['fn_' + function]):
                                return_to = self.conf['function']['fn_' + function]['return_to']
                            if(return_to == 'channel'):
                                self.base_say(out,[server,destination])
                            elif(return_to == 'privmsg'):
                                self.base_say(out,[server,client])
                            elif(return_to == 'notice'):
                                self.base_say(out,[server,destination],True)
                    # if we can't handle the function, let them know
                    elif(msg_pm):
                     #   self.base_say('"' + function + '" not defined.  Try "/msg ' + nick + ' help commands" for a list of commands.',[server,destination])
                        hallobase.hallobase.fn_staff(self,function + ' ' + args,client,[server,destination])
                    elif(msg_cmd and msg_cmdcln):
                        self.base_say('"' + function + '" not defined.  Try "/msg ' + nick + ' help commands" for a list of commands.',[server,destination])
                except Exception as e:
                    # if we have an error, let them know and print it to the screen
                    if(self.open):
                        self.base_say('Error occured.  Try "/msg ' + nick + ' help"',[server,destination])
                    print('ERROR: ' + str(e))
                if(msg_pm):
                    # let programmers define extra code in addition to function stuff
                    ircbot_on.ircbot_on.on_pm(self,server,client,msg_pm and nick or destination,':'.join(data.split(':')[2:]).replace(endl,''))
            elif msg_pub:
                #passive functions
           #     if(self.conf['server'][server]['channel'][destination]['passivefunc']):
                out = passive.passive.fnn_passive(self,message,client,[server,destination])
                if(out is not None):
                    self.base_say(out,[server,destination])
        elif('JOIN' == data.split()[1]):
            # handle JOIN events
            channel = ':'.join(data.split(':')[2:]).replace(endl,'').lower()
            client = data.split('!')[0][1:]
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' joined ' + channel)
            if(self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' ' + client + ' joined ' + channel,[server,channel])
            ircbot_on.ircbot_on.on_join(self,server,client,channel)
        elif('PART' == data.split()[1]):
            # handle PART events
            channel = data.split()[2]
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' left ' + channel + ' (' + message + ')')
            if(self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' ' + client + ' left ' + channel + ' (' + message + ')',[server,channel])
            ircbot_on.ircbot_on.on_part(self,server,client,channel,message)
        elif('QUIT' == data.split()[1]):
            #handle QUIT events
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' quit: ' + message)
            for channel in self.conf['server'][server]['channel']:
                if(self.conf['server'][server]['channel'][channel]['in_channel'] and self.conf['server'][server]['channel'][channel]['logging'] and client in self.core['server'][server]['channel'][channel]['user_list']):
                    self.base_addlog(self.base_timestamp() + ' ' + client + ' quit: ' + message,[server,channel])
            ircbot_on.ircbot_on.on_quit(self,server,client,message)
        elif('MODE' == data.split()[1]):
            # handle MODE events
            channel = data.split()[2].replace(endl, '').lower()
            client = data.split('!')[0][1:]
            mode = data.split()[3].replace(endl, '')
            if(len(data.split())>=4):
                args = ' '.join(data.split()[4:]).replace(endl, '')
            else:
                args = ''
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' set ' + mode + ' ' + args + ' on ' + channel)
            if(channel in self.conf['server'][server]['channel'] and 'logging' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' ' + client + ' set ' + mode + ' ' + args + ' on ' + channel,[server,channel])
            ircbot_on.ircbot_on.on_mode(self,server,client,channel,mode,args)
        elif('NOTICE' == data.split()[1]):
            # handle NOTICE messages
            channel = data.split()[2].replace(endl,'')
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] ' + channel + ' Notice from ' + client + ': ' + message)
            if(channel in self.conf['server'][server]['channel'] and 'logging' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' ' + channel + ' notice from ' + client + ': ' + message,[server,channel])
            ircbot_on.ircbot_on.on_notice(self,server,client,channel,message)
        elif('NICK' == data.split()[1]):
            #handle nick changes
            client = data.split('!')[0][1:]
            if(data.count(':')>1):
                newnick = data.split(':')[2]
            else:
                newnick = data.split()[2]
            print(self.base_timestamp() + ' [' + server + '] Nick change: ' + client + ' -> ' + newnick)
            for channel in self.conf['server'][server]['channel']:
                if(self.conf['server'][server]['channel'][channel]['in_channel'] and self.conf['server'][server]['channel'][channel]['logging'] and client in self.core['server'][server]['channel'][channel]['user_list']):
                    self.base_addlog(self.base_timestamp() + ' Nick change: ' + client + ' -> ' + newnick,[server,channel])
            ircbot_on.ircbot_on.on_nickchange(self,server,client,newnick)
        elif('INVITE' == data.split()[1]):
            #handle invites
            client = data.split('!')[0][1:]
            channel = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] invite to ' + channel + ' from ' + client)
            if(channel in self.conf['server'][server]['channel'] and 'logging' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' invite to ' + channel + ' from ' + client,[server,'@SERVER'])
            ircbot_on.ircbot_on.on_invite(self,server,client,channel)
        elif('KICK' == data.split()[1]):
            #handle kicks
            channel = data.split()[2]
            client = data.split()[1]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' was kicked from ' + channel + ': ' + message)
            if(self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(self.base_timestamp() + ' ' + client + ' was kicked from ' + channel + ': ' + message,[server,channel])
            ircbot_on.ircbot_on.on_kick(self,server,client,channel,message)
        elif data == '':
            #blank message thingy
            #print 'Blank'
            pass
        elif(len(data.split()[1]) == 3 and data.split()[1].isdigit()):
            #if this, it's a server info message. There's a few we care about, but the 376 end of MOTD is what we really want (what we really really want)
            if(data.split()[1] == "376"):
                self.core['server'][server]['motdend'] = True
            elif(data.split()[1] == "303"):
                self.core['server'][server]['check']['recipientonline'] = ':'.join(data.split(':')[2:])
                if(self.core['server'][server]['check']['recipientonline']==''):
                    self.core['server'][server]['check']['recipientonline'] = ' '
            elif(data.split()[1] == "353"):
                channel = data.split(':')[1].split()[-1].lower()
                self.core['server'][server]['check']['names'] = ':'.join(data.split(':')[2:])
                self.core['server'][server]['channel'][channel]['user_list'] = [nick.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','') for nick in self.core['server'][server]['check']['names'].split()]
                if(self.core['server'][server]['check']['names']==''):
                    self.core['server'][server]['check']['names'] = ' '
            print(self.base_timestamp() + ' [' + server + '] Server info: ' + data)
        elif not data.replace(endl, '').isspace():
            # if not handled, be confused ^_^
            unhandled = True
            print(self.base_timestamp() + ' [' + server + '] Unhandled data: ' + data)
  #          logunhandleddata = open('/home/dr-spangle/http/log_unhandleddata.txt','a')
  #          logunhandleddata.write(data + '\n---\n')
  #          logunhandleddata.close()
        ircbot_on.ircbot_on.on_rawdata(self,server,data,unhandled)

    def base_connect(self,server):
        while(self.core['server'][server]['connected'] == False):
            print(self.base_timestamp() + " Not connected to " + server + " yet")
            time.sleep(0.5)
        self.conf['server'][server]['connected'] = True
        print(self.base_timestamp() + " sending nick and user info to server: " + server)
        self.core['server'][server]['socket'].send(('NICK ' + self.conf['server'][server]['nick'] + endl).encode('utf-8'))
        self.core['server'][server]['socket'].send(('USER ' + self.conf['server'][server]['full_name'] + endl).encode('utf-8'))
        print(self.base_timestamp() + " sent nick and user info to " + server)
        while(self.core['server'][server]['motdend'] == False):
            time.sleep(0.5)
        print(self.base_timestamp() + " joining channels on " + server + ", identifying.")
        for channel in self.conf['server'][server]['channel']:
            if(self.conf['server'][server]['channel'][channel]['in_channel']):
                if(self.conf['server'][server]['channel'][channel]['pass'] == ''):
                    self.core['server'][server]['socket'].send(('JOIN ' + channel + endl).encode('utf-8'))
                else:
                    self.core['server'][server]['socket'].send(('JOIN ' + channel + ' ' + self.conf['server'][server]['channel'][channel]['pass'] + endl).encode('utf-8'))

        if self.conf['server'][server]['pass']:
            self.base_say('IDENTIFY ' + self.conf['server'][server]['pass'], [server,'nickserv'])

    def base_start(self,configfile="store/config.p"):
        #starts up the bot, starts base_run on each server.
        self.configfile = configfile
        self.conf = pickle.load(open(configfile,"rb"))
        self.megahal = {}
        self.core = {}
        self.core['server'] = {}
        self.core['function'] = {}
        self.open = True
        self.modules = []
        try:
            allowedmodules = pickle.load(open('store/allowedmodules.p','rb'))
        except:
            allowedmodules = []
        for mod in allowedmodules:
            imp.acquire_lock()
            importlib.import_module(mod)
            imp.reload(sys.modules[mod])
            imp.release_lock()
            if(mod not in self.modules):
                self.modules.append(mod)
        for server in self.conf['server']:
            if(self.conf['server'][server]['connected']):
                Thread(target=self.base_run, args=(server,)).start()
        time.sleep(2)
        while(self.open):
            servers = 0
            for server in self.conf['server']:
                if(self.conf['server'][server]['connected']):
                    servers = servers+1
                if(self.conf['server'][server]['connected'] and self.core['server'][server]['open'] and self.core['server'][server]['lastping']!=0 and (int(time.time())-self.core['server'][server]['lastping'])>(120+self.conf['server'][server]['pingdiff'])):
                    print("TIMED OUT FROM " + server + ", RECONNECTING.")
                    self.base_disconnect(server)
                    del self.core['server'][server]
                    time.sleep(1)
                    Thread(target=self.base_run, args=(server,)).start()
                if(self.conf['server'][server]['connected']):
        #            print("aaa")
                    for channel in self.conf['server'][server]['channel']:
        #                print("bbb")
                        if(self.conf['server'][server]['channel'][channel]['in_channel']):
        #                    print("ccc")
                        #    print("in channel " + channel + " on server " + server + ". idle_time = " + self.conf['server'][server]['channel'][channel]['idle_time'] + " and last_message = " + self.core['server'][server]['channel'][channel]['last_message'] + " current time = " + str(int(time.time())))
                            if('idle_time' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['idle_time']!=0 and self.core['server'][server]['channel'][channel]['last_message']!=0 and (int(time.time())-self.core['server'][server]['channel'][channel]['last_message'])>self.conf['server'][server]['channel'][channel]['idle_time']):
                                print("channel idle")
                                self.core['server'][server]['channel'][channel]['last_message'] = int(time.time())
                                out = idlechan.idlechan.fnn_idlechan(self,self.conf['server'][server]['channel'][channel]['idle_args'],'',[server,channel])
                                if(out is not None):
                                    self.base_say(out,[server,channel])
            if(servers==0):
                self.base_close()
        #    for filename in self.megahal:
        #        if((int(time.time())-self.megahal[filename]['last_used'])>600):
        #            self.megahal[filename]['brain'].sync()
        #            self.megahal[filename]['brain'].close()
        #   #         del self.megahal[filename]
        #            print("Closed megahal brain: " + filename)
            time.sleep(0.1)

    def base_run(self,server):
        # begin pulling data from a given server
        self.core['server'][server] = {}
        self.core['server'][server]['check'] = {}
        self.core['server'][server]['check']['names'] = ""
        self.core['server'][server]['check']['recipientonline'] = ""
        self.core['server'][server]['check']['nickregistered'] = False
        self.core['server'][server]['check']['userregistered'] = False
        self.core['server'][server]['channel'] = {}
        for channel in self.conf['server'][server]['channel']:
            self.core['server'][server]['channel'][channel] = {}
            self.core['server'][server]['channel'][channel]['last_message'] = 0
            self.core['server'][server]['channel'][channel]['user_list'] = []
            if(self.conf['server'][server]['channel'][channel]['megahal_record']):
                self.core['server'][server]['channel'][channel]['megahalcount'] = 0
        self.core['server'][server]['lastping'] = 0
        self.core['server'][server]['connected'] = False
        self.core['server'][server]['motdend'] = False
        self.core['server'][server]['open'] = True
        self.core['server'][server]['socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.core['server'][server]['socket'].connect((self.conf['server'][server]['address'],self.conf['server'][server]['port']))
        except Exception as e:
            print("CONNECTION ERROR: " + str(e))
            self.core['server'][server]['open'] = False
            del self.core['server'][server]
            del self.conf['server'][server]
          #  self.conf['servers'].remove(server)
        Thread(target=self.base_connect, args=(server,)).start()
        nextline = ""
        while(self.open and self.core['server'][server]['open']):
            nextbyte = self.core['server'][server]['socket'].recv(1).decode('utf-8','ignore')
            if(nextbyte!="\n"):
                nextline = nextline + nextbyte
            else:
                Thread(target=self.base_parse, args=(server,nextline)).start()
                nextline = ""

if __name__ == '__main__':
    ircbot().base_start("store/config.p")
#    ircbot().run(raw_input('network: '), raw_input('nick: '), [raw_input('channel: ')])
