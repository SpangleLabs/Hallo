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
import hallobase
import passive
import idlechan
import hashlib
import random

endl = '\r\n' # constant for ease/readability

class ircbot:

    def __init__(self):
        # connect
        self.on_init()
#        self.base_start()
  #      self.megahal = MegaHAL()

    def on_init(self):
        pass # override this method to do any startup code

    def on_join(self,server,client,channel):
        # handle join events from other users (or from hallo!)
        if(client.lower() in self.conf['server'][server]['channel'][channel]['voice_list']):
            for x in range(7):
                if(self.chk_userregistered(server,client)):
                    self.core['server'][server]['socket'].send(('MODE ' + channel + ' +v ' + client + endl).encode('utf-8'))
                    time.sleep(5)
                    break
        if(client.lower() == self.conf['server'][server]['nick'].lower()):
            self.conf['server'][server]['channel'][channel]['in_channel'] = True
            namesonline = self.chk_names(server,channel)
            namesonline = [x.lower() for x in namesonline]
            for user in self.conf['server'][server]['channel'][channel]['voice_list']:
                if(user in namesonline and "+" + user not in namesonline):
                    for x in range(7):
                        if(self.chk_userregistered(server,user)):
                            self.core['server'][server]['socket'].send(('MODE ' + channel + ' +v ' + user + endl).encode('utf-8'))
                            time.sleep(5)
                            break

    def on_part(self,server,client,channel,args):
        pass # override this method to handle PART events from other users

    def on_quit(self,server,client,args):
        pass # override this method to handle QUIT events from other users

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
        if(client == self.conf['server'][server]['nick']):
            self.conf['server'][server]['nick'] = newnick
        for channel in self.conf['server'][server]['channels']:
            if(newnick in self.conf['server'][server]['channel'][channel]['voice_list']):
                for x in range(7):
                    if(self.chk_userregistered(server,client)):
                        self.core['server'][server]['socket'].send(('MODE ' + channel + ' +v ' + newnick + endl).encode('utf-8'))
                        time.sleep(5)
                        break

    def on_invite(self,server,client,channel):
        if(self.chk_op(server,client)):
            self.fn_join(channel,client,[server,''])
        pass # override to do something on invite

    def on_kick(self,server,client,channel,message):
        if(client == self.conf['server'][server]['nick']):
            self.conf['server'][server]['channel'][channel]['in_channel'] = False

    def on_rawdata(self,server,data,unhandled):
        pass # override this method to do general data handling

    def fn_join(self,args,client,destination):
        'Join a channel.  Use "join <channel>".  Requires op'
        if(self.chk_op(destination[0],client)):
            channel = args.split()[0].lower()
            password = args[len(channel):]
            while(len(password)>0 and password[0]==' '):
                password = password[1:]
            while(len(password)>0 and password[-1:]==' '):
                password = password[:-1]
            if(channel not in self.conf['server'][destination[0]]['channels']):
                self.conf['server'][destination[0]]['channels'].append(channel)
                self.conf['server'][destination[0]]['channel'][channel] = {}
                self.conf['server'][destination[0]]['channel'][channel]['logging'] = True
                self.conf['server'][destination[0]]['channel'][channel]['megahal_record'] = False
                self.conf['server'][destination[0]]['channel'][channel]['sweardetect'] = False
                self.conf['server'][destination[0]]['channel'][channel]['in_channel'] = False
                self.conf['server'][destination[0]]['channel'][channel]['caps'] = False
                self.conf['server'][destination[0]]['channel'][channel]['passivefunc'] = True
                self.conf['server'][destination[0]]['channel'][channel]['idle_time'] = 0
                self.conf['server'][destination[0]]['channel'][channel]['idle_args'] = ''
                self.conf['server'][destination[0]]['channel'][channel]['voice_list'] = []
                self.conf['server'][destination[0]]['channel'][channel]['pass'] = password
                self.conf['server'][destination[0]]['channel'][channel]['swearlist'] = {}
                self.conf['server'][destination[0]]['channel'][channel]['swearlist']['possible'] = []
                self.conf['server'][destination[0]]['channel'][channel]['swearlist']['inform'] = []
                self.conf['server'][destination[0]]['channel'][channel]['swearlist']['comment'] = []
                self.conf['server'][destination[0]]['channel'][channel]['swearlist']['commentmsg'] = ''
            if(password == ''):
                if(self.conf['server'][destination[0]]['channel'][channel]['pass'] == ''):
                    self.core['server'][destination[0]]['socket'].send(('JOIN ' + channel + endl).encode('utf-8'))
                else:
                    self.core['server'][destination[0]]['socket'].send(('JOIN ' + channel + ' ' + self.conf['server'][destination[0]]['channel'][args]['pass'] + endl).encode('utf-8'))
            else:
                self.core['server'][destination[0]]['socket'].send(('JOIN ' + channel + ' ' + password + endl).encode('utf-8'))
                self.conf['server'][destination[0]]['channel'][channel]['pass'] = password
            return 'Joined ' + channel + '.'
        else:
            return 'Insufficient privileges to join.'

    def fn_part(self,args,client,destination):
        'Leave a channel.  Use "part <channel>".  Requires op'
        if(self.chk_op(destination[0],client)):
            if(args.replace(' ','')==""):
                self.core['server'][destination[0]]['socket'].send(('PART ' + destination[1] + endl).encode('utf-8'))
                self.conf['server'][destination[0]]['channel'][destination[1]]['in_channel'] = False
            else:
                self.core['server'][destination[0]]['socket'].send(('PART ' + args + endl).encode('utf-8'))
                self.conf['server'][destination[0]]['channel'][args.split()[0]]['in_channel'] = False
            return 'Parted ' + args + '.'
        else:
            return 'Insufficient privileges to part.'

    def fn_quit(self,args,client,destination):
        'Quit IRC.  Use "quit".  Requires godmode.'
        if(self.chk_god(destination[0],client)):
      #      self.megahal.sync()
            self.base_close()
            sys.exit(0)
        else:
            return 'Insufficient privileges to quit.'

    def fn_connect(self,args,client,destination):
        'Connects to a new server. Requires godmode'
        if(self.chk_god(destination[0],client)):
            args = args.lower()
            title = args.split('.')[1]
            if(title not in self.conf['servers']):
                self.conf['servers'].append(title)
                self.conf['server'][title] = {}
                self.conf['server'][title]['ops'] = list(self.conf['server'][destination[0]]['ops'])
                self.conf['server'][title]['gods'] = list(self.conf['server'][destination[0]]['gods'])
                self.conf['server'][title]['address'] = args
                self.conf['server'][title]['channels'] = []
                self.conf['server'][title]['nick'] = self.conf['server'][destination[0]]['nick']
                self.conf['server'][title]['full_name'] = self.conf['server'][destination[0]]['full_name']
                self.conf['server'][title]['pass'] = False
                self.conf['server'][title]['port'] = self.conf['server'][destination[0]]['port']
                self.conf['server'][title]['channel'] = {}
                self.conf['server'][title]['admininform'] = []
                self.conf['server'][title]['pingdiff'] = 600
                self.conf['server'][title]['connected'] = False
            Thread(target=self.base_run, args=(title,)).start()
            return "Connected to " + args
        else:
            return "Insufficient privileges to connect to a new server."

    def fn_disconnect(self,args,client,destination):
        'Disconnects from server. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            self.base_say('Disconnecting...',destination)
            args = args.lower()
  #          self.core['server'][destination[0]]['open'] = False
            self.conf['server'][server]['connected'] = False
            self.base_disconnect(destination[0])
            return "Disconnected."
        else:
            return "Insufficient privileges to disconnect from server."

    def fn_god_add(self,args,client,destination):
        'Adds a member to godlist. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            args = args.replace(' ','').lower()
            if(self.chk_nickregistered(destination[0],args)):
                if(args not in self.conf['server'][destination[0]]['gods']):
                    self.conf['server'][destination[0]]['gods'].append(args)
                    return "Added " + args + " to godlist for this server."
                else:
                    return "This person is already in the god list."
            else:
                return "This person's not registered, so I can't add them to the godlist."
        else:
            return "Insufficient privileges to add a member to godlist."

    def fn_god_list(self,args,client,destination):
        'Lists godlist for this server. Requires godmode'
        if(self.chk_god(destination[0],client)):
            return "Godlist for this server: " + ', '.join(self.conf['server'][destination[0]]['gods'])
        else:
            return "Insufficient privileges to list godlist."

    def fn_god_del(self,args,client,destination):
        'Removes someone from the godlist. Requires godmode'
        if(self.chk_god(destination[0],client)):
            args = args.replace(' ','').lower()
            if(args in self.conf['server'][destination[0]]['gods']):
                self.conf['server'][destination[0]]['gods'].remove(args)
                return "Removed " + args + " from godlist"
            else:
                return "That person isn't even in the godlist"
        else:
            return "Insufficient privileges to remove someone from godlist."

    def fn_ops_add(self,args,client,destination):
        'Adds a member to the ops list. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            args = args.replace(' ','').lower()
            if(self.chk_nickregistered(destination[0],args)):
                if(args not in self.conf['server'][destination[0]]['ops']):
                    self.conf['server'][destination[0]]['ops'].append(args)
                    return "Added " + args + " to ops list."
                else:
                    return "That person is already in the op list."
            else:
                return "This person's not registered, so I can't add them to the ops list."
        else:
            return "Insufficient privileges to add member to ops list."

    def fn_ops_list(self,args,client,destination):
        'Lists ops list for this server. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            return "Ops list for this server: " + ', '.join(self.conf['server'][destination[0]]['ops'])
        else:
            return "Insufficient privileges list ops for this server."

    def fn_ops_del(self,args,client,destination):
        'Removes someone from the ops list. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            args = args.replace(' ','').lower()
            if(args in self.conf['server'][destination[0]]['ops']):
                self.conf['server'][destination[0]]['ops'].remove(args)
                return "Removed " + args + " from ops list."
            else:
                return "That person isn't even in the ops list."
        else:
            return "Insufficient privileges to remove someone from ops list."

    def fn_voice_add(self,args,client,destination):
        'Adds a user to psuedoautovoice, format is "voice_add {user} {channel}"'
        if(self.chk_op(destination[0],client)):
            args = args.lower()
            channel = destination[1]
            if(len(args.split())>1):
                channel = args.split()[1]
                args = args.split()[0]
            if(args not in self.conf['server'][destination[0]]['channel'][channel]['voice_list']):
                if(self.chk_nickregistered(destination[0],args)):
                    self.conf['server'][destination[0]]['channel'][channel]['voice_list'].append(args)
                    if(self.chk_userregistered(destination[0],args)):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' +v ' + args + endl).encode('utf-8'))
                    return "Added " + args + " to the pseudoautovoice list for " + channel
                else:
                    return "It seems that " + args + " isn't a registered nick."
            else:
                return args + " is already on my pseudo-auto-voice list for " + channel
        else:
            return "Sorry, this function is for ops only."

    def fn_voice_list(self,args,client,destination):
        'Lists users on pseudoautovoice, ops only. no arguments, or channel to list'
        if(self.chk_op(destination[0],client)):
            if(args==''):
                args = destination[1]
            return "Users on pseudoautovoice list for " + args + ": " + ', '.join(self.conf['server'][destination[0]]['channel'][args]['voice_list'])
        else:
            return "Sorry, this function is for ops only."

    def fn_voice_del(self,args,client,destination):
        'Remove a user from autovoice list, ops only. same arguments as voice_add'
        if(self.chk_op(destination[0],client)):
            args = args.lower()
            channel = destination[1]
            if(len(args.split())>1):
                channel = args.split()[1]
                args = args.split()[0]
            if(args in self.conf['server'][destination[0]]['channel'][channel]['voice_list']):
                self.conf['server'][destination[0]]['channel'][channel]['voice_list'].remove(args)
                return "Removed " + args + " from pseudo-auto-voice list for " + channel
            else:
                return args + " isn't even on the autovoice list for " + channel
        else:
            return "Sorry, this function is for ops only."

    def fn_admininform_add(self,args,client,destination):
        'Add a user to the admin swear inform list, ops only.'
        if(self.chk_op(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args not in self.conf['server'][destination[0]]['admininform']):
                self.conf['server'][destination[0]]['admininform'].append(args)
                return "Added " + args + " to the admininform list."
            else:
                return "This person is already on the admininform list"
        else:
            return "Sorry, this function is for ops only."

    def fn_admininform_list(self,args,client,destination):
        'Lists users who are informed when sweardetect detects swearing.'
        if(self.chk_op(destination[0],client)):
            return "Users on admininform for this server: " + ', '.join(self.conf['server'][destination[0]]['admininform'])
        else:
            return "Sorry, this function is for ops only."

    def fn_admininform_del(self,args,client,destination):
        'Delete a user from being informed about swearing in selected channels'
        if(self.chk_op(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args in self.conf['server'][destination[0]]['admininform']):
                self.conf['server'][destination[0]]['admininform'].remove(args)
                return "Removed " + args + " from admininform list"
            else:
                return args + " isn't even on the admininform list for " + destination[0]
        else:
            return "Sorry, this function is for ops only."

    def fn_ignorelist_add(self,args,client,destination):
        'Adds a user to the ignore list, ops only.'
        if(self.chk_op(destination[0],client)):
            args = args.lower().replace(' ','')
            if('ignore_list' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'] = []
            if(args not in self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'].append(args)
                return "Added " + args + " to the ignore list."
            else:
                return "This person is already on the ignore list."
        else:
            return "Sorry, this function is for ops only."

    def fn_ignorelist_list(self,args,client,destination):
        'List users on the ignore list for this channel. Ops only.'
        if(self.chk_op(destination[0],client)):
            if('ignore_list' in self.conf['server'][destination[0]]['channel'][destination[1]]):
                return "Users on ignore list for this channel: " + ', '.join(self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'])
            else:
                return "There is no ignore list for this channel."
        else:
            return "Sorry, this function is for ops only."

    def fn_admininform_del(self,args,client,destination):
        'Delete a user from the ignore list for this channel. Ops only.'
        if(self.chk_op(destination[0],client)):
            args = args.lower().replace(' ','')
            if('ignore_list' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'] = []
            if(args in self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'].remove(args)
                return "Removed " + args + " from ignore list"
            else:
                return args + " isn't even on the ignore list for " + destination[1] + " on " + destination[0]
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_add(self,args,client,destination):
        'Add a swear to a channel swear list, format is "swear_add <list> <channel> <swearregex>". List is either "possible", "inform" or "comment"'
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=3):
                list = args.split()[0]
                channel = args.split()[1].lower()
                regex = ' '.join(args.split()[2:])
                if(list.lower() in ['possible','inform','comment']):
                    if(channel in self.conf['server'][destination[0]]['channels']):
                        self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()].append(regex)
                        return "Added " + regex + " to " + list + " swear list for " + channel + "."
                    else:
                        return "I'm not in that channel."
                else:
                    return "That's not a valid list. Valid lists are 'possible', 'inform' or 'comment'"
            else:
                return "Not enough arguments, remember to provide me with a list, then channel, then the regex for the swear you want to add. Lists are either 'possible', 'inform' or 'comment'"
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_list(self,args,client,destination):
        'Lists swears in a given channel. Format is swear_list <list> <channel>. Please only ask for this in privmsg.'
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=2):
                list = args.split()[0]
                channel = args.split()[1].lower()
                if(list.lower() in ['possible','inform','comment']):
                    if(channel in self.conf['server'][destination[0]]['channels']):
                        if(destination[1]!=channel):
                            return "Here is the " + list + " swear list for " + channel + ": " + ', '.join(self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()])
                        else:
                            return "I'm not printing a swear list in a channel."
                    else:
                        return "I'm not even in that channel."
                else:
                    return "That's not a valid list"
            else:
                return "That's not enough arguments, remember to provide me with a list, then a channel. Lists are either 'possible', 'inform' or 'comment'"
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_del(self,args,client,destination):
        'Deletes a swear from a swear list, format is "swear_del <list> <channel> <swearregex>". List is either "possible", "inform" or "comment"'
        if(self.chk_op(destination[0],client)):
            if(len(args.split())>=3):
                list = args.split()[0]
                channel = args.split()[1].lower()
                regex = ' '.join(args.split()[2:])
                if(list.lower() in ['possible','inform','comment']):
                    if(channel in self.conf['server'][destination[0]]['channels']):
                        if(regex in self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()]):
                            self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()].remove(regex)
                            return "Removed " + regex + " from " + list + " swear list for " + channel + "."
                        else:
                            return "That's not in the " + list + " swear list for " + channel + "."
                    else:
                        return "I'm not in that channel."
                else:
                    return "That's not a valid list. Valid lists are 'possible', 'inform' or 'comment'"
            else:
                return "Not enough arguments, remember to provide me with a list, then channel, then the regex for the swear you want to remove. Lists are either 'possible', 'inform' or 'comment'."
        else:
            return "Sorry, this function is for ops only."

    def fn_nickserv_registered_add(self,args,client,destination):
        'Add a string to the list of nickserv messages to look for when checking if a nick is registered'
        if(self.chk_god(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args not in self.conf['nickserv']['registered']):
                self.conf['nickserv']['registered'].append(args)
                return "Added " + args + " to the nickserv registered list."
            else:
                return "This message is already on the nickserv registered list"
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_registered_list(self,args,client,destination):
        'Lists all the nickserv messages to look for when checking if a nick is registered.'
        if(self.chk_god(destination[0],client)):
            return "Nick registered nickserv messages: " + ', '.join(self.conf['nickserv']['registered'])
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_registered_del(self,args,client,destination):
        'Deletes a string from the list of nickserv messages to look for when checking is a nick is registered'
        if(self.chk_god(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args in self.conf['nickserv']['registered']):
                self.conf['server']['registered'].remove(args)
                return "Removed " + args + " from nickserv registered list."
            else:
                return "This message isn't even on the nickserv registered list."
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_online_add(self,args,client,destination):
        'Add a string to the list of nickserv messages to look for when checking if a nick is online'
        if(self.chk_god(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args not in self.conf['nickserv']['online']):
                self.conf['nickserv']['online'].append(args)
                return "Added " + args + " to the nickserv online list."
            else:
                return "This message is already on the nickserv online list"
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_online_list(self,args,client,destination):
        'Lists all the nickserv messages to look for when checking if a nick is online.'
        if(self.chk_god(destination[0],client)):
            return "Nick online nickserv messages: " + ', '.join(self.conf['nickserv']['online'])
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_online_del(self,args,client,destination):
        'Deletes a string from the list of nickserv messages to look for when checking is a nick is online'
        if(self.chk_god(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args in self.conf['nickserv']['online']):
                self.conf['server']['online'].remove(args)
                return "Removed " + args + " from nickserv online list."
            else:
                return "This message isn't even on the nickserv online list"
        else:
            return "Sorry, this function is for gods only."


    def fn_server_address(self,args,client,destination):
        'Sets address for a given server. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            if(len(args.split())!=2):
                return "Please give two inputs, the server name first, then the server's address"
            else:
                if(args.split()[0] in self.conf['servers']):
                    self.base_say("Changed " + args.split()[0] + " address to: " + args.split()[1],destination)
                    self.core['server'][args.split()[0]]['lastping'] = 1
                    return "Changed " + args.split()[0] + " address to: " + args.split()[1]
                else:
                    return "I don't have a server in config called " + args.split()[0]
        else:
            return "Insufficient privileges to change a server address."

    def fn_server_port(self,args,client,destination):
        'Sets port for a given server. Requires godmode.'
        if(self.chk_god(destination[0],client)):
            if(len(args.split())!=2):
                return "Please give two inputs, the server name first, then the server's port"
            else:
                if(args.split()[0] in self.conf['servers']):
                    self.base_say("Changed " + args.split()[0] + " port to: " + args.split()[1],destination)
                    self.core['server'][args.split()[0]]['lastping'] = 1
                    return "Changed " + args.split()[0] + " port to: " + args.split()[1]
                else:
                    return "I don't have a server in config called " + args.split()[0]
        else:
            return "Insufficient privileges to change a server port."

    def fn_changenick(self,args,client,destination):
        'Tells hallo to change his nick, godmode only.'
        if(self.chk_god(destination[0],client)):
            args = args.replace(' ','')
            oldnick = self.conf['server'][destination[0]]['nick']
         #   self.conf['server'][destination[0]]['nick'] = args
            self.core['server'][destination[0]]['socket'].send(('NICK ' + args + endl).encode('utf-8'))
            if(self.conf['server'][destination[0]]['pass'] != False):
                self.base_say('identify ' + self.conf['server'][destination[0]]['pass'],[destination[0],'nickserv'])
            return "Changed nick from " + oldnick + " to " + args
        else:
            return "Insufficient privileges to change nickname"

    def fn_server_pass(self,args,client,destination):
        'Changes nickserv password, godmode only.'
        if(self.chk_god(destination[0],client)):
            args = args.replace(' ','')
            self.base_say('identify ' + args,[destination[0],'nickserv'])
            self.conf['server'][destination[0]]['pass'] = args
            return "Changed password."
        else:
            return "Insufficient privileges to change nickname"

    def fn_channel_caps(self,args,client,destination):
        'Sets or toggles caps lock for channel, ops only'
        if(self.chk_op(destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['caps'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['caps']
                return "Caps lock toggled."
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['caps'] = True
                return "Caps lock on"
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['caps'] = False
                return "Caps lock off"
        else:
            return "Insufficient privileges to set caps lock."

    def fn_channel_logging(self,args,client,destination):
        'Sets or toggles logging for channel, ops only'
        if(self.chk_op(destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['logging']
                return "Logging toggled"
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = True
                return "Logging on"
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = False
                return "Logging off"
        else:
            return "Insufficient privileges to set logging."

    def fn_channel_megahalrecord(self,args,client,destination):
        'Sets or toggles megahal recording for channel, gods only'
        if(self.chk_god(destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record']
                return "Megahal recording toggled"
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] = True
                return "Megahal recording on"
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] = False
                return "Megahal recording off"
        else:
            return "Insufficient privileges to set megahal recording."

    def fn_channel_sweardetect(self,args,client,destination):
        'Sets or toggles sweardetection for channel, ops only'
        if(self.chk_op(destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect']
                return "Swear detection toggled"
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect'] = True
                return "Swear detection on"
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect'] = False
                return "Swear detection off"
        else:
            return "Insufficient privileges to set swear detection."

    def fn_channel_passivefunc(self,args,client,destination):
        'Sets or toggles passive functions for channel, gods only'
        if(self.chk_god(destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc']
                return "Passive functions toggled"
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc'] = True
                return "Passive functions on"
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc'] = False
                return "Passive functions off"
        else:
            return "Insufficient privileges to set passive functions status."

    def fn_channel_idletime(self,args,client,destination):
        'Sets the amount of time a channel can be idle before idle channel functions activate, gods only'
        if(self.chk_god(destination[0],client)):
            if(args==''):
                return "Please provide a time, in seconds, before idle channel functions activate."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['idle_time'] = int(args)
                if('idle_args' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                    self.conf['server'][destination[0]]['channel'][destination[1]]['idle_args'] = ''
                return "Idle time set to " + args + " seconds."
        else:
            return "Insufficient privileges to set idle channel time."

    def fn_channel_idleargs(self,args,client,destination):
        'Sets the arguments to pass to the idle channel function, gods only'
        if(self.chk_god(destination[0],client)):
            self.conf['server'][destination[0]]['channel'][destination[1]]['idle_args'] = args
            return "Idle channel arguments set to: " + args
        else:
            return "Insufficient privileges to set idle channel arguments."

    def fn_channel_pass(self,args,client,destination):
        'Sets a password for a channel, use channel_pass {channel} {password}'
        if(self.chk_op(destination[0],client)):
            channel = args.split()[0]
            password = args[len(channel):]
            while(len(password)>0 and password[0]==' '):
                password = password[1:]
            while(len(password)>0 and password[-1:]==' '):
                password = password[:-1]
            self.conf['server'][destination[0]]['channel'][destination[1]]['pass'] = password
            return "Stored password for " + destination[1]
        else:
            return "Insufficient privileges to set channel password"

    def fn_function_conf(self,args,client,destination):
        'Set a function config variable, Format: function_conf <function> <variable> <value>, functionname should include "fn_" and variable can be "listed_to", "disabled", "repair", "privmsg", "max_run_time", "time_delay" or "return_to"'
        if(self.chk_god(destination[0],client)):
            if(len(args.split())>=3):
                 function = args.split()[0].lower()
                 variable = args.split()[1].lower()
                 value = ' '.join(args.split()[2:])
                 functions = dir(self)
                 for module in self.modules:
                     functions = functions + dir(getattr(__import__(module),module))
                 functions = functions + ['default']
                 if(function in functions):
                     if(function not in self.conf['function']):
                         self.conf['function'][function] = {}
                     if(variable=='disabled' or variable=='privmsg'):
                         if(value.lower() in ['true','on','1']):
                             self.conf['function'][function][variable] = True
                             return "Set " + variable + " to True for " + function + "."
                         elif(value.lower() in ['false','off','0']):
                             self.conf['function'][function][variable] = False
                             return "Set " + variable + " to False for " + function + "."
                         else:
                             return "That's an invalid value for " + variable + ". It can only be True or False."
                     elif(variable=='max_run_time' or variable=='time_delay'):
                         try:
                             self.conf['function'][function][variable] = int(value)
                             return "Set " + variable + " to " + value + " for " + function + "."
                         except TypeError:
                             return "That's an invalid value for " + variable + ". It must be a number (in seconds)."
                     elif(variable=='listed_to'):
                         if(value.lower() in ['user','op','god']):
                             self.conf['function'][function][variable] = value.lower()
                             return "Set " + variable + " to " + value + " for " + function + "."
                         else:
                             return "That's an invalid value for " + variable + ". It must be 'user', 'op', or 'god'."
                     elif(variable=='return_to'):
                         if(value.lower() in ['channel','notice','privmsg','none']):
                             self.conf['function'][function][variable] = value.lower()
                             return "Set " + variable + " to " + value + " for " + function + "."
                         else:
                             return "That's an invalid value for " + variable + ". It must be 'channel', 'notice', 'privmsg' or 'none'."
                     elif(variable=='repair'):
                         if(value.lower() in ['false','off','0']):
                             self.conf['function'][function][variable] = False
                             return "Set " + variable + " to False for " + function + "."
                         else:
                             self.conf['function'][function][variable] = value
                             return "Set " + variable + " to " + value + " for " + function + "."
                     else:
                         return "Invalid variable. Valid variables are 'listed_to', 'disabled', 'repair', 'privmsg', 'max_run_time' or 'return_to'."
                 else:
                     return "Invalid function."
            else:
                return "Not enough arguments given, please provide me with a function name, variable and value. Function names should include preceeding fn_ and variables can be 'listed_to', 'disabled', 'repair', 'privmsg', 'max_run_time', 'time_delay' or 'return_to'"
        else:
            return "Insufficient privileges to change function variables"

    def fn_core_view(self,args,client,destination):
        'View the core variable, privmsg only. gods only.'
        if(self.chk_god(destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole core variable here, that would be rude."
            else:
                return "erm, really? my core variable... erm, if you insist. Here goes:\n" + pprint.pformat(self.core)
        else:
            return "Insufficient privileges to view core variable."

    def fn_config_view(self,args,client,destination):
        'View the config, privmsg only. gods only.'
        if(self.chk_god(destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole config here, that would be rude."
            else:
                #return "erm.. the config file... one sec. here it is:\n" + pprint.pformat(self.conf)
                prettyconf = pprint.pformat(self.conf)
                filename = "conf_" + hashlib.md5(str(random.randint(1,1000)*time.time()).encode('utf-8')).hexdigest() + ".txt"
                link = "http://hallo.dr-spangle.com/" + filename
                file = open("../http/" + filename,'w')
                file.write(prettyconf)
                file.close()
                self.base_say("Config written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../http/" + filename)
                return "File removed."
        else:
            return "Insufficient privileges to view config file"

    def fn_config_save(self,args,client,destination):
        'Save the config and pickle it. godmod only.'
        if(self.chk_god(destination[0],client)):
            pickle.dump(self.conf,open(self.configfile,"wb"))
            return "config file saved."
        else:
            return "Insufficient privileges to save config file."

    def fn_help(self,args,client,destination):
        'Gives information about commands.  Use "help commands" for a list of commands, or "help <command>" for help on a specific command.'
        if(args.lower() == 'commands'):
            access_level = ['user']
            if(self.chk_op(destination[0],client)):
                access_level.append('op')
                if(self.chk_god(destination[0],client)):
                    access_level.append('god')
            commands = []
            # loop through all bot commands
            functions = dir(self)
            for fn in functions:
                # use the one they're asking about
                if(isinstance(getattr(self, fn), collections.Callable) and fn.startswith('fn_')):
                    listed_to = self.conf['function']['default']['listed_to']
                    if(fn in self.conf['function'] and 'listed_to' in self.conf['function'][fn]):
                        listed_to = self.conf['function'][fn]['listed_to']
                    if(listed_to in access_level):
                        commands.append(fn.split('.')[-1])
            for module in self.modules:
                for fn in dir(getattr(__import__(module),module)):
                    if(isinstance(getattr(getattr(__import__(module),module),fn), collections.Callable) and fn.startswith('fn_')): 
                        listed_to = self.conf['function']['default']['listed_to']
                        if(fn in self.conf['function'] and 'listed_to' in self.conf['function'][fn]):
                            listed_to = self.conf['function'][fn]['listed_to']
                        if(listed_to in access_level):
                            commands.append(fn)
       #         functions = functions + [ module + '.' + module + '.' + i for i in dir(getattr(__import__(module),module))]
            return ', '.join(cmd[3:] for cmd in commands)
        elif(args != ''):
            fn = 'fn_'+args.lower().split()[0]
            method = 'placeholder'
            addonmodule = False
            if(hasattr(self,fn)):
                method = getattr(self, fn)
            if(not isinstance(method, collections.Callable)):
                for module in self.modules:
                    if(hasattr(__import__(module),module) and hasattr(getattr(__import__(module),module),fn)):
                        method = getattr(getattr(__import__(module),module),fn)
                        addonmodule = True
                    if(isinstance(method, collections.Callable)):
                        break
            if(isinstance(method, collections.Callable)):
                if(addonmodule):
                    doc = method.__doc__
                else:
                    doc = method.__doc__
                return doc
        else:
            return 'Use "help commands" for a list of commands, or "help <command>" for help on a specific command.  Note:  <>s mean you should replace them with an argument, described within them.  If you are not using private messaging, prefix your commands with "' + self.conf['server'][destination[0]]['nick'] + '".'

    def fn_modulereload(self,args,client,destination):
        'reloads a specified module. Godmode only.'
        try:
            allowedmodules = pickle.load(open('store/allowedmodules.p','rb'))
        except IOError:
            allowedmodules = []
        if(self.chk_god(destination[0],client)):
            args = args.lower().replace(' ','')
            if(args in allowedmodules):
                imp.acquire_lock()
                importlib.import_module(args)
                imp.reload(sys.modules[args])
                imp.release_lock()
                if(args not in self.modules):
                    self.modules.append(args)
                return "Reloaded module."
            else:
                return "This module is not allowed. sorry."
        else:
            return "Insufficient privileges"

    def chk_op(self,server,client):
        # check if someone has op status for this bot
        client = client.lower()
        return self.chk_userregistered(server,client) and ((len(self.conf['server'][server]['ops'])!=0 and self.conf['server'][server]['ops'].count(client) > 0) or (len(self.conf['server'][server]['gods'])!=0 and self.conf['server'][server]['gods'].count(client) > 0))

    def chk_god(self,server,client):
        # check if someone has god status for this bot
        client = client.lower()
        return self.chk_userregistered(server,client) and len(self.conf['server'][server]['gods'])!=0 and self.conf['server'][server]['gods'].count(client) > 0

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
            print(self.base_timestamp() + ' [' + server + '] waiting for input on which admins are online')
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

    def fnn_sweardetect(self,args,client,destination):
        swearinform = [r'\bmong\b',r'\bshit\b',r'fuck',r'\bcunt\b',r'\bwank(er|ing|)\b',r'\bnigger\b',r'\bbastard\b',r'\bbollocks\b',r'\ba(rse|ss)(hole|)\b',r'\bpaki\b',r'\bwhore\b',r'\btwat\b',r'\bpiss(ed|ing|)\b',r'\bspastic\b',r'\bsperg(y|ier|)\b',r'\bR34\b',r'\bporn(o|ograpy|)\b']
        swearinformcaution = [r'fag(got|)\b',r'\bprick\b',r'\bshag\b',r'\bslag\b',r'\bdick(head|)\b',r'\bballs\b',r'\bjew\b',r'\bbitch\b',r'\bbugger\b']
        swearcomment = []
        swears = False
        if(self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect']):
            for swear in self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['possible']:
                if re.search(swear, args, re.I):
                    for admin in self.chk_recipientonline(destination[0],self.conf['server'][destination[0]]['admininform']):
                        self.base_say(client + ' possibly just swore in ' + destination[1] + '. Check the context. The message was: ' + args,[destination[0],admin])
                    swears = True
                    break
            for swear in self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['inform']:
                if re.search(swear, args, re.I):
                    for admin in self.chk_recipientonline(destination[0],self.conf['server'][destination[0]]['admininform']):
                        self.base_say(client + ' just swore in ' + destination[1] + '. the message was: ' + args,[destination[0],admin])
                    swears = True
                    break
            for swear in self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['comment']:
                if re.search(swear, args, re.I):
                    if(self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['commentmsg']==''):
                        self.base_say("Please don't swear in the channel. This is a PG channel.",destination)
                    else:
                        self.base_say(self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['commentmsg'].replace('{swear}',re.search(swear, args, re.I).group(0)),destination)
                    swears = True
                    break
       # if(not swears and self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] and 'hallo speak' not in args.lower()):
       #     self.megahal.learn(args)
       #     self.core['server'][destination[0]]['channel'][destination[1]]['megahalcount'] = self.core['server'][destination[0]]['channel'][destination[1]]['megahalcount'] + 1
       #     if(self.core['server'][destination[0]]['channel'][destination[1]]['megahalcount'] >= 10):
       #         self.megahal.sync()
       #         self.core['server']['destination[0]]['channel'][destination[1]]['megahalcount'] = 0

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
        for server in self.conf['servers']:
            self.base_disconnect(server)
        pickle.dump(self.conf,open(self.configfile,"wb"))
        self.open = False

    def base_disconnect(self,server):
       # for channel in self.conf['server'][server]['channels']:
        #    self.base_say('Daisy daisy give me your answer do...',[server,channel])
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
                if(destination[1] != '#' or self.conf['server'][destination[0]]['channel'][destination[1]]['logging']):
                    self.base_addlog(self.base_timestamp() + ' <' + self.conf['server'][destination[0]]['nick'] + '>: ' + line, destination)
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
            # check for swears
            if msg_pub:
                self.fnn_sweardetect(message,client,[server,destination])
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
                self.on_ctcp(server,client,args)
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
                    functions = dir(self)
                    for module in self.modules:
                        functions = functions + dir(getattr(__import__(module),module))
                #    for fn in functions:
                #        if(fn.split('.')[-1] == ('fn_' + function.lower())):
                    privmsg = self.conf['function']['default']['privmsg']
                    if('fn_' + function in self.conf['function'] and 'privmsg' in self.conf['function']['fn_' + function]):
                        privmsg = self.conf['function']['fn_' + function]['privmsg']
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
                    self.on_pm(server,client,msg_pm and nick or destination,':'.join(data.split(':')[2:]).replace(endl,''))
            elif msg_pub:
                #passive functions
                if(self.conf['server'][server]['channel'][destination]['passivefunc']):
                    out = passive.passive.fnn_passive(self,message,client,[server,destination])
                    if(out is not None):
                        self.base_say(out,[server,destination])
        elif('JOIN' == data.split()[1]):
            # handle JOIN events
            channel = ':'.join(data.split(':')[2:]).replace(endl,'').lower()
            client = data.split('!')[0][1:]
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' joined ' + channel)
            self.on_join(server,client,channel)
        elif('PART' == data.split()[1]):
            # handle PART events
            channel = data.split()[2]
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' left ' + channel)
            self.on_part(server,client,channel,message)
        elif('QUIT' == data.split()[1]):
            #handle QUIT events
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] ' + client + ' quit: ' + message)
            self.on_quit(server,client,message)
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
            self.on_mode(server,client,channel,mode,args)
        elif('NOTICE' == data.split()[1]):
            # handle NOTICE messages
            channel = data.split()[2].replace(endl,'')
            client = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] Notice: ' + data)
            self.on_notice(server,client,channel,message)
        elif('NICK' == data.split()[1]):
            #handle nick changes
            client = data.split('!')[0][1:]
            if(data.count(':')>1):
                newnick = data.split(':')[2]
            else:
                newnick = data.split()[2]
            print(self.base_timestamp() + ' [' + server + '] Nick change: ' + client + ' -> ' + newnick)
            self.on_nickchange(server,client,newnick)
        elif('INVITE' == data.split()[1]):
            #handle invites
            client = data.split('!')[0][1:]
            channel = ':'.join(data.split(':')[2:]).replace(endl,'')
            print(self.base_timestamp() + ' [' + server + '] invite to ' + channel + ' from ' + client)
            self.on_invite(server,client,channel)
        elif('KICK' == data.split()[1]):
            #handle kicks
            channel = data.split()[2]
            client = data.split()[1]
            message = ':'.join(data.split(':')[2:]).replace(endl,'')
            self.on_kick(server,client,channel,message)
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
                self.core['server'][server]['check']['names'] = ':'.join(data.split(':')[2:])
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
        self.on_rawdata(server,data,unhandled)

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
        for channel in self.conf['server'][server]['channels']:
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
        for server in self.conf['servers']:
            if(self.conf['server'][server]['connected']):
                Thread(target=self.base_run, args=(server,)).start()
        time.sleep(2)
        while(self.open):
            servers = 0
            for server in self.conf['servers']:
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
                    for channel in self.conf['server'][server]['channels']:
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
        for channel in self.conf['server'][server]['channels']:
            self.core['server'][server]['channel'][channel] = {}
            self.core['server'][server]['channel'][channel]['last_message'] = 0
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
            self.conf['servers'].remove(server)
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
