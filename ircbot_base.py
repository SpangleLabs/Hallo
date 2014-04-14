import time
import sys
import importlib
import imp
import pprint
import pickle
import hashlib
import random
import os
import collections
from threading import Thread

import ircbot_chk

endl = '\r\n'

class ircbot_base:

    def fn_join(self,args,client,destination):
        'Join a channel.  Use "join <channel>".  Requires op'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            channel = args.split()[0].lower()
            password = args[len(channel):]
            while(len(password)>0 and password[0]==' '):
                password = password[1:]
            while(len(password)>0 and password[-1:]==' '):
                password = password[:-1]
            if(channel not in self.conf['server'][destination[0]]['channel']):
            #    self.conf['server'][destination[0]]['channels'].append(channel)
                self.conf['server'][destination[0]]['channel'][channel] = {}
                self.core['server'][destination[0]]['channel'][channel] = {}
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
                self.core['server'][destination[0]]['channel'][channel]['last_message'] = int(time.time())
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
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
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
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
      #      self.megahal.sync()
            self.base_close()
            sys.exit(0)
        else:
            return 'Insufficient privileges to quit.'

    def fn_connect(self,args,client,destination):
        'Connects to a new server. Requires godmode'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.lower()
            if(':' in args):
                argsplit = args.split(':')
                port = int(argsplit[1])
                args = argsplit[0]
            else:
                port = 6667
            argsplit = args.split('.')
            title = max(argsplit,key=len)
            if(title not in self.conf['server']):
         #       self.conf['servers'].append(title)
                self.conf['server'][title] = {}
                self.conf['server'][title]['ops'] = list(self.conf['server'][destination[0]]['ops'])
                self.conf['server'][title]['gods'] = list(self.conf['server'][destination[0]]['gods'])
                self.conf['server'][title]['address'] = args
          #      self.conf['server'][title]['channels'] = []
                self.conf['server'][title]['nick'] = self.conf['server'][destination[0]]['nick']
                self.conf['server'][title]['full_name'] = self.conf['server'][destination[0]]['full_name']
                self.conf['server'][title]['pass'] = False
                self.conf['server'][title]['port'] = port
                self.conf['server'][title]['channel'] = {}
                self.conf['server'][title]['admininform'] = []
                self.conf['server'][title]['pingdiff'] = 600
                self.conf['server'][title]['connected'] = False
            Thread(target=self.base_run, args=(title,)).start()
            return "Connected to " + args + " [" + title + "]."
        else:
            return "Insufficient privileges to connect to a new server."

    def fn_disconnect(self,args,client,destination):
        'Disconnects from server. Requires godmode.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(args.replace(' ','')==''):
                self.base_say('Disconnecting...',destination)
                args = args.lower()
  #               self.core['server'][destination[0]]['open'] = False
                self.conf['server'][destination[0]]['connected'] = False
                self.base_disconnect(destination[0])
                return "Disconnected."
            else:
                if(args.lower() in self.core['server']):
                    self.base_say('Disconnecting from ' + args,destination)
                    self.conf['server'][args.lower()]['connected'] = False
                    self.base_disconnect(args.lower())
                    return "Disconnected from " + args + "."
                else:
                    return "I'm not on any server by that id."
        else:
            return "Insufficient privileges to disconnect from server."

    def fn_god_add(self,args,client,destination):
        'Adds a member to godlist. Requires godmode.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.replace(' ','').lower()
            if(ircbot_chk.ircbot_chk.chk_nickregistered(self,destination[0],args)):
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
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Godlist for this server: " + ', '.join(self.conf['server'][destination[0]]['gods']) + "."
        else:
            return "Insufficient privileges to list godlist."

    def fn_god_del(self,args,client,destination):
        'Removes someone from the godlist. Requires godmode'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.replace(' ','').lower()
            if(args in self.conf['server'][destination[0]]['gods']):
                self.conf['server'][destination[0]]['gods'].remove(args)
                return "Removed " + args + " from godlist."
            else:
                return "That person isn't even in the godlist."
        else:
            return "Insufficient privileges to remove someone from godlist."

    def fn_ops_add(self,args,client,destination):
        'Adds a member to the ops list. Requires godmode.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.replace(' ','').lower()
            if(ircbot_chk.ircbot_chk.chk_nickregistered(self,destination[0],args)):
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
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Ops list for this server: " + ', '.join(self.conf['server'][destination[0]]['ops']) + "."
        else:
            return "Insufficient privileges list ops for this server."

    def fn_ops_del(self,args,client,destination):
        'Removes someone from the ops list. Requires godmode.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.replace(' ','').lower()
            if(args in self.conf['server'][destination[0]]['ops']):
                self.conf['server'][destination[0]]['ops'].remove(args)
                return "Removed " + args + " from ops list."
            else:
                return "That person isn't even in the ops list."
        else:
            return "Insufficient privileges to remove someone from ops list."

    def fn_ignore_list_add(self,args,client,destination):
        'Adds a user to the ignore list, ops only.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
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

    def fn_ignore_list_list(self,args,client,destination):
        'List users on the ignore list for this channel. Ops only.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if('ignore_list' in self.conf['server'][destination[0]]['channel'][destination[1]]):
                return "Users on ignore list for this channel: " + ', '.join(self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']) + "."
            else:
                return "There is no ignore list for this channel."
        else:
            return "Sorry, this function is for ops only."

    def fn_ignore_list_del(self,args,client,destination):
        'Delete a user from the ignore list for a channel, ops only.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if('ignore_list' in self.conf['server'][destination[0]]['channel'][destination[1]]):
                if(args in self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']):
                    self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'].remove(args)
                    return "Removed " + args + " from the ignore list."
                else:
                    return args + " isn't even on the ignore list for " + destination[0] + "."
            else:
                return "There isn't even an ignore list for this channel."
        else:
            return "Sorry, this function is for ops only."

    def fn_nickserv_registered_add(self,args,client,destination):
        'Add a string to the list of nickserv messages to look for when checking if a nick is registered'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if(args not in self.conf['nickserv']['registered']):
                self.conf['nickserv']['registered'].append(args)
                return "Added " + args + " to the nickserv registered list."
            else:
                return "This message is already on the nickserv registered list."
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_registered_list(self,args,client,destination):
        'Lists all the nickserv messages to look for when checking if a nick is registered.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Nick registered nickserv messages: " + ', '.join(self.conf['nickserv']['registered']) + "."
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_registered_del(self,args,client,destination):
        'Deletes a string from the list of nickserv messages to look for when checking is a nick is registered'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
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
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if(args not in self.conf['nickserv']['online']):
                self.conf['nickserv']['online'].append(args)
                return "Added " + args + " to the nickserv online list."
            else:
                return "This message is already on the nickserv online list."
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_online_list(self,args,client,destination):
        'Lists all the nickserv messages to look for when checking if a nick is online.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Nick online nickserv messages: " + ', '.join(self.conf['nickserv']['online']) + "."
        else:
            return "Sorry, this function is for gods only."

    def fn_nickserv_online_del(self,args,client,destination):
        'Deletes a string from the list of nickserv messages to look for when checking is a nick is online'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if(args in self.conf['nickserv']['online']):
                self.conf['nickserv']['online'].remove(args)
                return "Removed " + args + " from nickserv online list."
            else:
                return "This message isn't even on the nickserv online list."
        else:
            return "Sorry, this function is for gods only."

    def fn_server_address(self,args,client,destination):
        'Sets address for a given server. Requires godmode.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(len(args.split())!=2):
                return "Please give two inputs, the server name first, then the server's address."
            else:
                if(args.split()[0] in self.conf['server']):
                    self.base_say("Changed " + args.split()[0] + " address to: " + args.split()[1],destination)
                    self.core['server'][args.split()[0]]['lastping'] = 1
                    return "Changed " + args.split()[0] + " address to: " + args.split()[1]
                else:
                    return "I don't have a server in config called " + args.split()[0] + "."
        else:
            return "Insufficient privileges to change a server address."

    def fn_server_port(self,args,client,destination):
        'Sets port for a given server. Requires godmode.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(len(args.split())!=2):
                return "Please give two inputs, the server name first, then the server's port."
            else:
                if(args.split()[0] in self.conf['server']):
                    self.conf['server'][args.split()[0]]['port'] = int(args.split()[1])
                    self.base_say("Changed " + args.split()[0] + " port to: " + args.split()[1],destination)
                    self.core['server'][args.split()[0]]['lastping'] = 1
                    return "Changed " + args.split()[0] + " port to: " + args.split()[1] + "."
                else:
                    return "I don't have a server in config called " + args.split()[0] + "."
        else:
            return "Insufficient privileges to change a server port."

    def fn_change_nick(self,args,client,destination):
        'Tells hallo to change his nick, godmode only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.replace(' ','')
            oldnick = self.conf['server'][destination[0]]['nick']
         #   self.conf['server'][destination[0]]['nick'] = args
            self.core['server'][destination[0]]['socket'].send(('NICK ' + args + endl).encode('utf-8'))
            if(self.conf['server'][destination[0]]['pass'] != False):
                self.base_say('identify ' + self.conf['server'][destination[0]]['pass'],[destination[0],'nickserv'])
            return "Changed nick from " + oldnick + " to " + args + "."
        else:
            return "Insufficient privileges to change nickname."

    def fn_server_pass(self,args,client,destination):
        'Changes nickserv password, godmode only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.replace(' ','')
            self.base_say('identify ' + args,[destination[0],'nickserv'])
            self.conf['server'][destination[0]]['pass'] = args
            return "Changed password."
        else:
            return "Insufficient privileges to change password."

    def fn_function_conf(self,args,client,destination):
        'Set a function config variable, Format: function_conf <function> <variable> <value>, functionname should include "fn_" and variable can be "listed_to", "disabled", "repair", "privmsg", "max_run_time", "time_delay" or "return_to"'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
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
                return "Not enough arguments given, please provide me with a function name, variable and value. Function names should include preceeding fn_ and variables can be 'listed_to', 'disabled', 'repair','privmsg', 'max_run_time', 'time_delay' or 'return_to'."
        else:
            return "Insufficient privileges to change function variables."

    def fn_core_view(self,args,client,destination):
        'View the core variable, privmsg only. gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole core variable here, that would be rude."
            else:
          #      return "erm, really? my core variable... erm, if you insist. Here goes:\n" + pprint.pformat(self.core)
                prettycore = pprint.pformat(self.core)
                filename = "core_" + hashlib.md5(str(random.randint(1,1000)*time.time()).encode('utf-8')).hexdigest() + ".txt"
                link = "http://sucs.org/~drspangle/" + filename
                file = open("../public_html/" + filename,'w')
                file.write(prettycore)
                file.close()
                self.base_say("Core written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../public_html/" + filename)
                return "File removed."
        else:
            return "Insufficient privileges to view core variable."

    def fn_core_set(self,args,client,destination):
        'Set core variables, gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.split()
            if(args[0] in self.core and args[1] in self.core[args[0]] and args[2] in self.core[args[0]][args[1]]):
                if(args[3].lower()=='false'):
                    self.core[args[0]][args[1]][args[2]] = False
                    return "Set self.core['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to False."
                elif(args[3].lower()=='true'):
                    self.core[args[0]][args[1]][args[2]] = True
                    return "Set self.core['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to True."
                else:
                    self.core[args[0]][args[1]][args[2]] = args[3]
                    return "Set self.core['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to " + args[3] + "."

    def fn_megahal_view(self,args,client,destination):
        'View the megahal variable, privmsg only. gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole megahal variable here, that would be rude."
            else:
                prettymegahal = pprint.pformat(self.megahal)
                filename = "megahal_" + hashlib.md5(str(random.randint(1,1000)*time.time()).encode("utf-8")).hexdigest() + ".txt"
                link = "http://hallo.dr-spangle.com/" + filename
                file = open("../http/" + filename,'w')
                file.write(prettymegahal)
                file.close()
                self.base_say("Megahal variable written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../http/" + filename)
                return "File removed."
        else:
            return "Insufficient privileges to view megahal variable."

    def fn_config_view(self,args,client,destination):
        'View the config, privmsg only. gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole config here, that would be rude."
            else:
                #return "erm.. the config file... one sec. here it is:\n" + pprint.pformat(self.conf)
                prettyconf = pprint.pformat(self.conf)
                filename = "conf_" + hashlib.md5(str(random.randint(1,1000)*time.time()).encode('utf-8')).hexdigest() + ".txt"
                link = "http://sucs.org/~drspangle/" + filename
                file = open("../public_html/" + filename,'w')
                file.write(prettyconf)
                file.close()
                self.base_say("Config written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../public_html/" + filename)
                return "File removed."
        else:
            return "Insufficient privileges to view config file."

    def fn_config_set(self,args,client,destination):
        'Set config variables, gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.split()
            if(args[0] in self.conf and args[1] in self.conf[args[0]] and args[2] in self.conf[args[0]][args[1]]):
                if(args[3].lower()=='false'):
                    self.conf[args[0]][args[1]][args[2]] = False
                    return "Set self.conf['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to False."
                elif(args[3].lower()=='true'):
                    self.conf[args[0]][args[1]][args[2]] = True
                    return "Set self.conf['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to True."
                elif(args[3].isdigit()):
                    self.conf[args[0]][args[1]][args[2]] = int(args[3])
                    return "Set self.conff['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to " + args[3] + "."
                else:
                    self.conf[args[0]][args[1]][args[2]] = args[3]
                    return "Set self.conf['" + args[0] + "']['" + args[1] + "']['" + args[2] + "'] to: '" + args[3] + "'"

    def fn_config_save(self,args,client,destination):
        'Save the config and pickle it. godmod only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            pickle.dump(self.conf,open(self.configfile,"wb"))
            return "config file saved."
        else:
            return "Insufficient privileges to save config file."

    def fn_help(self,args,client,destination):
        'Gives information about commands.  Use "help commands" for a list of commands, or "help <command>" for help on a specific command.'
        if(args.lower() == 'commands'):
            access_level = ['user']
            if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                access_level.append('op')
                if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
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
            return ', '.join(cmd[3:] for cmd in commands) + "."
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

    def fn_module_reload(self,args,client,destination):
        'reloads a specified module. Godmode only.'
        try:
            allowedmodules = pickle.load(open('store/allowedmodules.p','rb'))
        except IOError:
            allowedmodules = []
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
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
            return "Insufficient privileges."

    def fn_chan_alias_add(self,args,client,destination):
        'Adds a channel alias, for use with chk_destination, gods only.'
        args = args.split()
        if(args[0][0]=='#'):
            channel = args[0].lower()
            del args[0]
        elif(args[1][0]=='#'):
            channel = args[1].lower()
            del args[1]
        elif(args[2][0]=='#'):
            channel = args[2].lower()
            del args[2]
        else:
            return "No channel specified."
        if(args[0] in self.conf['server']):
            server = args[0].lower()
            del args[0]
        elif(args[1] in self.conf['server']):
            server = args[1].lower()
            del args[1]
        else:
            return "No server specified."
        alias = args[0]
        if('alias_chan' not in self.conf):
            self.conf['alias_chan'] = {}
        if(alias in self.conf['alias_chan']):
            return "Alias by this name already exists."
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            self.conf['alias_chan'][alias] = {}
            self.conf['alias_chan'][alias]['server'] = server
            self.conf['alias_chan'][alias]['channel'] = channel
            return "Added channel alias for " + alias + " pointing to {" + server + "," + channel + "}"
        else:
            return "Only gods can add channel aliases."

    def fn_chan_alias_list(self,args,client,destination):
        'Lists all channel aliases.'
        if('alias_chan' not in self.conf):
            return "There are no aliases."
        else:
            return "Channel aliases: " + ', '.join([item + "->{" + self.conf['alias_chan'][item]['server'] + "," + self.conf['alias_chan'][item]['channel'] + "}" for item in self.conf['alias_chan']])

    def fn_chan_alias_del(self,args,client,destination):
        'Delete channel alias. Gods only. format: chan_alias_del <alias>'
        if('alias_chan' not in self.conf):
            return "There are no aliases."
        if(args in self.conf['alias_chan']):
            return "That isn't a valid alias."
        if(ircbot_chk.ircbot_chk.chk_god(self,server,client)):
            del self.conf['alias_chan'][args]
            return "Removed " + args + " channel alias."
        else:
            return "Only gods can delete channel aliases."





