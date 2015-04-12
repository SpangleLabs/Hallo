#socket connects to the server
#time gets time for time stamps and does sleep
#os makes directories for logs, and gets the process ID
#sys is used to kill itself
#thread is used for multi threading
#re is used for regex, for swear detect
#pickle is used to store the config, also scriptures
#pprint is used to view the config
#importlib is used to import modules on the fly, hopefully
#copy is used to copy the self.conf variable
import socket, time, os, pickle, importlib
from threading import Thread
import collections
import imp
#from megahal import *
import sys
import re

from xml.dom import minidom

from inc.commons import Commons
from Server import Server, ServerFactory, ServerIRC

import ircbot_on
import mod_passive

#TODO: investigate this
endl = Commons.mEndLine

class Hallo:
    mDefaultNick = "Hallo"
    mDefaultPrefix = False
    mDefaultFullName = "HalloBot HalloHost HalloServer :an irc bot by spangle"
    mOpen = False
    mServerFactory = None
    mServerList = []

    def __init__(self):
        #Create ServerFactory
        self.mServerFactory = ServerFactory(self)
        #load config
        self.loadFromXml()
        self.mOpen = True
        #TODO: connect to servers
        #TODO: deprecate and remove this
        self.base_start()
        #If no servers, ask for a new server
        #TODO: make this check if any servers are connected
        if(len(self.mServerList)==0):
            self.conf = self.manualServerConnect()
        #connect to autoconnect servers
        print('connecting to servers')
        for server in self.mServerList:
            if(server.getAutoConnect()):
                Thread(target=server.run).start()
        time.sleep(2)
        #main loop, sticks around throughout the running of the bot
        print('connected to all servers.')
        while(self.mOpen):
            try:
                #TODO: replace this with whatever
                ircbot_on.ircbot_on.on_coreloop(self)
            except Exception as e:
                print("coreloop error: " + str(e))
            time.sleep(0.1)
        

    def loadFromXml(self):
        try:
            doc = minidom.parse("config/config,xml")
            self.mDefaultNick = doc.getElementsByTagName("default_nick")[0].firstChild.data
            self.mDefaultPrefix = doc.getElementsByTagName("default_prefix")[0].firstChild.data
            self.mDefaultFullName = doc.getElementsByTagName("default_full_name")[0].firstChild.data
            serverListXml = doc.getElementsByTagName("server_list")[0]
            for serverXml in serverListXml.getElementsByTagName("server"):
                serverObject = self.mServerFactory.newServerFromXml(serverXml.toxml())
                self.addServer(serverObject)
            return
        except (FileNotFoundError, IOError):
            print("Error loading config")
            self.manualServerConnect()
            
    def saveToXml(self):
        doc = minidom.Document();
        #create root element
        root = doc.createElement("config")
        doc.appendChild(root)
        #create default_nick element
        defaultNickElement = doc.createElement("default_nick")
        defaultNickElement.appendChild(doc.createTextNode(self.mDefaultNick))
        root.appendChild(defaultNickElement)
        #create default_prefix element
        defaultPrefixElement = doc.createElement("default_prefix")
        defaultPrefixElement.appendChild(doc.createTextNode(self.mDefaultPrefix))
        root.appendChild(defaultPrefixElement)
        #create default_full_name element
        defaultFullNameElement = doc.createElement("default_full_name")
        defaultFullNameElement.appendChild(doc.createTextNode(self.mDefaultFullName))
        root.appendChild(defaultFullNameElement)
        #create server list
        serverListElement = doc.createElement("server_list")
        for serverItem in self.mServerList:
            serverElement = minidom.parse(serverItem.toXml()).firstChild
            serverListElement.appendChild(serverElement)
        root.appendChild(serverListElement)
        #save XML
        doc.writexml(open("config/config.xml","w"),indent="  ",addindent="  ",newl="\n")
        
    def addServer(self,server):
        #adds a new server to the server list
        self.mServerList += server
        
    def getServerByName(self,serverName):
        for server in self.mServerList:
            if(server.getName()==serverName):
                return server
        return None
    
    def removeServer(self,server):
        self.mServerList.remove(server)
        
    def removeServerByName(self,serverName):
        for server in self.mServerList:
            if(server.getName()==serverName):
                self.mServerList.remove(server)
                
    def close(self):
        'Shuts down the entire program'
        for server in self.mServerList:
            server.disconnect()
        self.saveToXml()
        self.mOpen = False
        
    def getDefaultNick(self):
        'Default nick getter'
        return self.mDefaultNick

    def setDefaultNick(self,defaultNick):
        'Default nick setter'
        self.mDefaultNick = defaultNick
        
    def getDefaultPrefix(self):
        'Default prefix getter'
        return self.mDefaultPrefix
    
    def setDefaultPrefix(self,defaultPrefix):
        'Default prefix setter'
        self.mDefaultPrefix = defaultPrefix
        
    def getDefaultFullName(self):
        'Default full name getter'
        return self.mDefaultFullName
    
    def setDefaultFullName(self,defaultFullName):
        'Default full name setter'
        self.mDefaultFullName = defaultFullName
    
    def manualServerConnect(self):
        #TODO: add ability to connect to non-IRC servers
        print("No servers have been loaded or connected to. Please connect to an IRC server.")
        godNick = input("What nickname is the bot operator using? [deer-spangle]")
        godNick = godNick.replace(' ','')
        if(godNick==''):
            godNick = 'deer-spangle'
        serverAddr = input("What server should the bot connect to? [irc.freenode.net:6667]")
        serverAddr = serverAddr.replace(' ','')
        if(serverAddr==''):
            serverAddr = 'irc.freenode.net:6667'
        serverUrl = serverAddr.split(':')[0]
        serverPort = serverAddr.split(':')[1]
        serverMatch = re.match(r'([a-z\d\.-]+\.)?([a-z\d-]{1,63})\.([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})',serverUrl,re.I)
        serverName = serverMatch.group(2)
        #Create the server object
        newServer = Server(self,serverName,serverUrl,serverPort)
        #Add new server to server list
        self.addServer(newServer)
        #Save XML
        self.saveToXml()
        #TODO: remove all this crap
        self.conf['server'] = {}
        self.conf['server'][serverName] = {}
        self.conf['server'][serverName]['ops'] = []
        self.conf['server'][serverName]['gods'] = [godNick]
        self.conf['server'][serverName]['address'] = serverName
        self.conf['server'][serverName]['nick'] = self.mDefaultNick
        self.conf['server'][serverName]['full_name'] = self.mDefaultFullName
        self.conf['server'][serverName]['pass'] = False
        self.conf['server'][serverName]['port'] = serverPort
        self.conf['server'][serverName]['channel'] = {}
        self.conf['server'][serverName]['admininform'] = []
        self.conf['server'][serverName]['pingdiff'] = 600
        self.conf['server'][serverName]['connected'] = True
        print("Config file created.")
        #TODO: remove this
        pickle.dump(self.conf,open(self.configfile,"wb"))
        print("Config file saved.")

    def base_start(self):
        #starts up the bot, starts base_run on each server.
        #TODO: remove configfile loading
        try:
            self.conf = pickle.load(open("store/config.p","rb"))
        except EOFError:
            #TODO: remove all this crap
            self.conf = {}
            self.conf['function'] = {}
            self.conf['function']['default'] = {}
            self.conf['function']['default']['disabled'] = False
            self.conf['function']['default']['listed_to'] = 'user'
            self.conf['function']['default']['max_run_time'] = 180
            self.conf['function']['default']['privmsg'] = True
            self.conf['function']['default']['repair'] = False
            self.conf['function']['default']['return_to'] = 'channel'
            self.conf['function']['default']['time_delay'] = 0
            self.conf['nickserv'] = {}
            self.conf['nickserv']['online'] = ['lastseen:now','isonlinefrom:','iscurrentlyonline','nosuchnick','userseen:now']
            self.conf['nickserv']['registered'] = ['registered:']
        self.megahal = {}
        self.core = {}
        self.core['server'] = {}
        self.core['function'] = {}
        #TODO: deprecate this, use different module loading
        self.modules = []
        try:
            allowedmodules = pickle.load(open('store/allowedmodules.p','rb'))
        except:
            allowedmodules = []
        for mod in allowedmodules:
            imp.acquire_lock()
            try:
                importlib.import_module(mod)
                imp.reload(sys.modules[mod])
                if(mod not in self.modules):
                    self.modules.append(mod)
            except:
                print('Module: ' + mod + ' missing. Skipping it.')
            imp.release_lock()


#######################################################
#######EVERYTHING BELOW HERE WILL NEED BREAKING INTO OTHER OBJECTS
#######################################################

    

    def base_disconnect(self,server):
        for channel in self.conf['server'][server]['channel']:
        #    self.base_say('Daisy daisy give me your answer do...',[server,channel])
            if(self.conf['server'][server]['channel'][channel]['in_channel'] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' Hallo has quit.',[server,channel])
        #    time.sleep(1)
        if('open' in self.core['server'][server] and self.core['server'][server]['open']):
            #self.core['server'][server]['socket'].send(('QUIT :Daisy daisy give me your answer do...' + endl).encode('utf-8'))
            self.core['server'][server]['socket'].send(('QUIT :Will I dream?' + endl).encode('utf-8'))
            self.core['server'][server]['socket'].close()
        #    self.conf['server'][server]['connected'] = False
            self.core['server'][server]['open'] = False

    def base_say(self,msg,destination,notice=False):
        # if the connection is open...
        #if not self.mOpen: return
        # send the message, accounting for linebreaks
        maxlength = 450 # max message length, inc channel name.
        command = 'PRIVMSG'
        if(notice):
            command = 'NOTICE'
        if(self.mOpen and self.core['server'][destination[0]]['open']):
            if(destination[1][0] == '#' and self.conf['server'][destination[0]]['channel'][destination[1]]['caps']):
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',msg)
                msg = msg.upper()
                for url in urls:
                    msg = msg.replace(url.upper(),url)
            for n, line in enumerate(msg.split('\n')):
                if((len(line)+len(destination[1]))>maxlength):
                    linefirst = line[:(maxlength-3-len(destination[1]))] + '...'
                    line = line[(maxlength-3-len(destination[1])):]
                    print((Commons.currentTimestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + linefirst).encode('ascii','replace').decode())
                    self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + linefirst + endl).encode('utf-8'))
                    while((len(line)+len(destination[1]))>(maxlength-3)):
                        linechunk = '...' + line [:(maxlength-6-len(destination[1]))] + '..'
                        line = line[(maxlength-6-len(destination[1])):]
                        print((Commons.currentTimestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + linechunk).encode('ascii','replace').decode())
                        self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + linechunk + endl).encode('utf-8'))
                    lineend = '...' + line
                    print((Commons.currentTimestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + lineend).encode('ascii','replace').decode())
                    self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + lineend + endl).encode('utf-8'))
                else:
                    print((Commons.currentTimestamp() + ' [' + destination[0] + '] ' + destination[1] + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + line).encode('ascii','replace').decode())
                    self.core['server'][destination[0]]['socket'].send((command + ' ' + destination[1] + ' :' + line + endl).encode('utf-8'))
                if(destination[1][0] != '#' or self.conf['server'][destination[0]]['channel'][destination[1]]['logging']):
                    self.base_addlog(Commons.currentTimestamp() + ' <' + self.conf['server'][destination[0]]['nick'] + '> ' + line,destination)
                # avoid flooding
                if n % 5 == 4:
                    time.sleep(2)


    def base_connect(self,server):
        count = 0
        while(self.core['server'][server]['connected'] == False and count<30):
            print(Commons.currentTimestamp() + " Not connected to " + server + " yet")
            time.sleep(0.5)
            count += 1
        self.conf['server'][server]['connected'] = True
        print(Commons.currentTimestamp() + " sending nick and user info to server: " + server)
        self.core['server'][server]['socket'].send(('NICK ' + self.conf['server'][server]['nick'] + endl).encode('utf-8'))
        self.core['server'][server]['socket'].send(('USER ' + self.conf['server'][server]['full_name'] + endl).encode('utf-8'))
        print(Commons.currentTimestamp() + " sent nick and user info to " + server)
        while(self.core['server'][server]['motdend'] == False):
            time.sleep(0.5)
        print(Commons.currentTimestamp() + " joining channels on " + server + ", identifying.")
        for channel in self.conf['server'][server]['channel']:
            if(self.conf['server'][server]['channel'][channel]['in_channel']):
                if(self.conf['server'][server]['channel'][channel]['pass'] == ''):
                    self.core['server'][server]['socket'].send(('JOIN ' + channel + endl).encode('utf-8'))
                else:
                    self.core['server'][server]['socket'].send(('JOIN ' + channel + ' ' + self.conf['server'][server]['channel'][channel]['pass'] + endl).encode('utf-8'))
        if self.conf['server'][server]['pass']:
            self.base_say('IDENTIFY ' + self.conf['server'][server]['pass'], [server,'nickserv'])

    def base_decode(self,raw_bytes):
        try:
            text = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = raw_bytes.decode('iso-8859-1')
            except UnicodeDecodeError:
                text = raw_bytes.decode('cp1252')
        return text

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
        log.write(msg.encode('ascii','ignore').decode() + '\n')
        log.close()

    def base_function(self,client,msg,function,args,destpair):
        server = destpair[0]
        destination = destpair[1]
        out = None
        notice = False
        msg_pm = msg[0]
        msg_cmd = msg[1]
        msg_cmdcln = msg[2]
        if(client.lower()==self.conf['server'][server]['nick'].lower()):
            return None
        #####SPLIT HERE
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
            #search modules for the method with the same name as the function requested.
            for module in self.modules:
                if(hasattr(__import__(module),module) and hasattr(getattr(__import__(module),module),'fn_' + function)):
                    method = getattr(getattr(__import__(module),module),'fn_' + function)
                if(isinstance(method,collections.Callable)):
                    break
        #if you managed to find a method, check it works
            if(isinstance(method, collections.Callable)):
                #####SPLIT FOR CHK_FUNC_DISABLED
                #check if the function has been disabled
                disabled = False
                disabled = self.conf['function']['default']['disabled']
                if('fn_' + function in self.conf['function'] and 'disabled' in self.conf['function']['fn_' + function]):
                    disabled = self.conf['function']['fn_' + function]['disabled']
                if(disabled):
                    out = "This function has been disabled, sorry"
                else:
                #####END SPLIT
                    ######SPLIT FOR CHK_FUNC_TIME_DELAY
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
                    #######END SPLIT
                        #this part wants to be changed to start another thread I guess, then this thread can monitor it.
                        #info needed will be max run time (loop for that long before check if it's dead (or replied) and then kill it.)
                        #also have to check processor and ram usage, I guess
                        #will need to get the id of the thread I just started, too
                        out = method(self,args,client,[server,destination])
                        if(out is not None):
                            out = str(out)
                        #record the time it was used.
                        if('fn_' + function not in self.core['function']):
                            self.core['function']['fn_' + function] = {}
                        self.core['function']['fn_' + function]['last_used'] = int(time.time())
                        #check where this function is meant to send its answer to, and how
                    return_to = self.conf['function']['default']['return_to']
                    if('fn_' + function in self.conf['function'] and 'return_to' in self.conf['function']['fn_' + function]):
                        return_to = self.conf['function']['fn_' + function]['return_to']
                    if(return_to == 'channel' or return_to == 'notice'):
                        destpair = [server,destination]
                    elif(return_to == 'privmsg'):
                        destpair = [server,client]
                    notice = False
                    if(return_to == 'notice'):
                        notice = True
        # if we can't handle the function, let them know
        elif(msg_pm):
            out = '"' + function + '" not defined.  Try "/msg ' + self.conf['server'][server]['nick'] + ' help commands" for a list of commands.'
        #    out = mod_chan_ctrl.mod_chan_ctrl.fn_staff(self,function + ' ' + args,client,[server,destination])
            if(out is None):
                return '"' + function + '" not defined. Try "/msg ' + self.conf['server'][server]['nick'] + ' help commands" for a list of commands.'
        elif(msg_cmd and msg_cmdcln):
            out = '"' + function + '" not defined.  Try "/msg ' + self.conf['server'][server]['nick'] + ' help commands" for a list of commands.'
        else:
            out = None
        ##### END SPLIT 
        if(out is not None):
            return [out,destpair,notice]
        else:
            return None
        
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
#            del self.core['server'][server]
#            del self.conf['server'][server]
#            self.conf['servers'].remove(server)
        Thread(target=self.base_connect, args=(server,)).start()
        nextline = b""
        while(self.mOpen and server in self.core['server'] and self.core['server'][server]['open']):
            try:
                nextbyte = self.core['server'][server]['socket'].recv(1)
            except:
                nextbyte = b""
            if(nextbyte==b""):
                self.core['server'][server]['lastping'] = 1
                self.core['server'][server]['reconnect'] = True
            if(nextbyte!=b"\n"):
                nextline = nextline + nextbyte
            else:
                nextstring = self.base_decode(nextline)
                Thread(target=self.base_parse, args=(server,nextstring)).start()
                nextline = b""


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
            print(Commons.currentTimestamp() + ' [' + server + '] PING')
            self.core['server'][server]['socket'].send(('PONG ' + data.split()[1] + endl).encode('utf-8'))
            ircbot_on.ircbot_on.on_ping(self,server,data.split()[1])
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
                if(destination!=nick):
                    if('ignore_list' in self.conf['server'][server]['channel'][destination]):
                        ignore_list = self.conf['server'][server]['channel'][destination]['ignore_list']
                    if(client.lower() in ignore_list):
                        msg_cmd = False
            # if it's a private message, answer to the client, not to yourself
            if msg_pm:
                destination = client
            if msg_ctcp:
                client = data.split('!')[0][1:].lower()
                args = ':'.join(data.split(':')[2:])[1:-1]
                # print and a clean version of the message
                if(len(args)>=6 and args[:6] == 'ACTION'):
                    line = Commons.currentTimestamp() + ' [' + server + '] ' + destination + ' **' + client + ' ' + args[7:] + '**'
                else:
                    line = Commons.currentTimestamp() + ' [' + server + '] ' + destination + ' <' + client + ' (CTCP)> ' + args
                print(line)
                #log the message
                if(msg_pm or server not in self.conf['server'] or destination not in self.conf['server'][server]['channel'] or self.conf['server'][server]['channel'][destination]['logging']):
                    self.base_addlog(line, [server,destination])
                ircbot_on.ircbot_on.on_ctcp(self,server,client,args)
            else:
                # print and a clean version of the message
                print(Commons.currentTimestamp() + ' [' + server + '] ' + destination + ' <' + client + '> ' + message)
                #log the message
                if(msg_pm or server not in self.conf['server'] or destination not in self.conf['server'][server]['channel'] or self.conf['server'][server]['channel'][destination]['logging']):
                    self.base_addlog(Commons.currentTimestamp() + ' <' + client + '> ' + message, [server,destination])
            #command colon variable, if command is followed by a colon and command doesn't exist, throw an error
            msg_cmdcln = False
            # if it's a public message, parse out the prefixed nick and clean up added whitespace/colons
            if msg_cmd:
                message = message[len(nick):]
                if(len(message)>=1 and message[0] == ','):
                    message = message[1:]
                if(len(message)>=1 and message[0] == ':'):
                    message = message[1:]
                    msg_cmdcln = True
                while(len(message)>=1 and message[0] == ' '):
                    message = message[1:]
            # now handle functions!
            if msg_cmd or msg_pm:
                if(len(message) > 0):
                    function = message.split()[0].lower()
                else:
                    function = ''
                args = message[len(function):]
                # parse out leading whitespace
                if(len(args)>=1):
                    while(len(args)>=1 and args[0] in [' ',',']):
                        args = args[1:]
                #Encase functions in error handling, because programmers might make functions which are a tad crashy
                try:
                    out = self.base_function(client,[msg_pm,msg_cmd,msg_cmdcln],function,args,[server,destination])
                    if(out is not None):
                        self.base_say(out[0],out[1],out[2])
                except Exception as e:
                    # if we have an error, let them know and print it to the screen
                    if(self.mOpen):
                        self.base_say('Error occured.  Try "/msg ' + nick + ' help"',[server,destination])
                    print('ERROR: ' + str(e))
                if(msg_pm):
                    # let programmers define extra code in addition to function stuff
                    ircbot_on.ircbot_on.on_pm(self,server,client,msg_pm and nick or destination,':'.join(data.split(':')[2:]).replace(endl,''))
            elif msg_pub:
                #passive functions
#               if(self.conf['server'][server]['channel'][destination]['passivefunc']):
                out = mod_passive.mod_passive.fnn_passive(self,message,client,[server,destination])
                if(out is not None):
                    self.base_say(out,[server,destination])
        elif('JOIN' == data.split()[1]):
            # handle JOIN events
            channel = ':'.join(data.split(':')[2:]).replace(endl,'').lower()
            client = data.split('!')[0][1:]
            print(Commons.currentTimestamp() + ' [' + server + '] ' + client + ' joined ' + channel)
            if(self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' ' + client + ' joined ' + channel,[server,channel])
            ircbot_on.ircbot_on.on_join(self,server,client,channel)
        elif('PART' == data.split()[1]):
            # handle PART events
            channel = data.split()[2]
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(Commons.currentTimestamp() + ' [' + server + '] ' + client + ' left ' + channel + ' (' + message + ')')
            if(self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' ' + client + ' left ' + channel + ' (' + message + ')',[server,channel])
            ircbot_on.ircbot_on.on_part(self,server,client,channel,message)
        elif('QUIT' == data.split()[1]):
            #handle QUIT events
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(Commons.currentTimestamp() + ' [' + server + '] ' + client + ' quit: ' + message)
            for channel in self.conf['server'][server]['channel']:
                if(self.conf['server'][server]['channel'][channel]['in_channel'] and self.conf['server'][server]['channel'][channel]['logging'] and client in self.core['server'][server]['channel'][channel]['user_list']):
                    self.base_addlog(Commons.currentTimestamp() + ' ' + client + ' quit: ' + message,[server,channel])
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
            print(Commons.currentTimestamp() + ' [' + server + '] ' + client + ' set ' + mode + ' ' + args + ' on ' + channel)
            if(channel in self.conf['server'][server]['channel'] and 'logging' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' ' + client + ' set ' + mode + ' ' + args + ' on ' + channel,[server,channel])
            ircbot_on.ircbot_on.on_mode(self,server,client,channel,mode,args)
        elif('NOTICE' == data.split()[1]):
            # handle NOTICE messages
            channel = data.split()[2].replace(endl,'')
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(Commons.currentTimestamp() + ' [' + server + '] ' + channel + ' Notice from ' + client + ': ' + message)
            if(channel in self.conf['server'][server]['channel'] and 'logging' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' ' + channel + ' notice from ' + client + ': ' + message,[server,channel])
            ircbot_on.ircbot_on.on_notice(self,server,client,channel,message)
        elif('NICK' == data.split()[1]):
            #handle nick changes
            client = data.split('!')[0][1:]
            if(data.count(':')>1):
                newnick = data.split(':')[2]
            else:
                newnick = data.split()[2]
            print(Commons.currentTimestamp() + ' [' + server + '] Nick change: ' + client + ' -> ' + newnick)
            for channel in self.conf['server'][server]['channel']:
                if(self.conf['server'][server]['channel'][channel]['in_channel'] and self.conf['server'][server]['channel'][channel]['logging'] and client in self.core['server'][server]['channel'][channel]['user_list']):
                    self.base_addlog(Commons.currentTimestamp() + ' Nick change: ' + client + ' -> ' + newnick,[server,channel])
            ircbot_on.ircbot_on.on_nickchange(self,server,client,newnick)
        elif('INVITE' == data.split()[1]):
            #handle invites
            client = data.split('!')[0][1:]
            channel = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(Commons.currentTimestamp() + ' [' + server + '] invite to ' + channel + ' from ' + client)
            if(channel in self.conf['server'][server]['channel'] and 'logging' in self.conf['server'][server]['channel'][channel] and self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' invite to ' + channel + ' from ' + client,[server,'@SERVER'])
            ircbot_on.ircbot_on.on_invite(self,server,client,channel)
        elif('KICK' == data.split()[1]):
            #handle kicks
            channel = data.split()[2]
            client = data.split()[3]
            message = ':'.join(data.split(':')[4:]).replace(endl,'')
            print(Commons.currentTimestamp() + ' [' + server + '] ' + client + ' was kicked from ' + channel + ': ' + message)
            if(self.conf['server'][server]['channel'][channel]['logging']):
                self.base_addlog(Commons.currentTimestamp() + ' ' + client + ' was kicked from ' + channel + ': ' + message,[server,channel])
            ircbot_on.ircbot_on.on_kick(self,server,client,channel,message)
        elif data == '':
            #blank message thingy
            #print 'Blank'
            pass
        elif(len(data.split()[1]) == 3 and data.split()[1].isdigit()):
            #if this, it's a server info message. There's a few we care about, but the 376 end of MOTD is what we really want (what we really really want)
            ircbot_on.ircbot_on.on_numbercode(self,server,data.split()[1],data)
            print(Commons.currentTimestamp() + ' [' + server + '] Server info: ' + data)
        elif not data.replace(endl, '').isspace():
            # if not handled, be confused ^_^
            unhandled = True
            print(Commons.currentTimestamp() + ' [' + server + '] Unhandled data: ' + data)
#            logunhandleddata = open('/home/dr-spangle/http/log_unhandleddata.txt','a')
#            logunhandleddata.write(data + '\n---\n')
#            logunhandleddata.close()
        ircbot_on.ircbot_on.on_rawdata(self,server,data,unhandled)



if __name__ == '__main__':
    Hallo()
#    ircbot().run(raw_input('network: '), raw_input('nick: '), [raw_input('channel: ')])
