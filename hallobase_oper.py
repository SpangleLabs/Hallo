import ircbot_chk
import pprint
import time
import os
import pickle
import sys
import importlib
import imp
import random
import hashlib


endl = '\r\n'
class hallobase_oper:

    def fn_god(self,args,client,destination):
        'Modify godlist, add, list or delete. Format: god <add/list/del> <username>'
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Insufficient privileges to modify godlist."
        args_split = args.lower().split()
        if(len(args_split)<2 and args_split[0]!='list'):
            return "Invalid number of arguments, please provide a username or a function."
        if(args_split[0] in ['add','list','del','delete','remove']):
            rawfunc = args_split[0]
            if(len(args_split)>1):
                nick = args_split[1]
        elif(args_split[1] in ['add','del','delete','remove']):
            rawfunc = args_split[1]
            nick = args_split[0]
        else:
            return "Please specify a function. Valid functions are: add, list and delete."
        if(rawfunc == 'add'):
            if(not ircbot_chk.ircbot_chk.chk_nickregistered(self,destination[0],nick)):
                return "This person's not registered, so I can't add them to the godlist."
            if(nick in self.conf['server'][destination[0]]['gods']):
                return "This person is already in the god list."
            self.conf['server'][destination[0]]['gods'].append(nick)
            return "Added " + nick + " to the godlist for this server."
        elif(rawfunc == 'list'):
            return "Godlist for this server: " + ', '.join(self.conf['server'][destination[0]]['gods']) + '.'
        elif(rawfunc in ['del','delete','remove']):
            if(args not in self.conf['server'][destination[0]]['gods']):
                return "That person isn't even in the godlist."
            self.conf['server'][destination[0]]['gods'].remove(nick)
            return "Removed " + args + " from the godlist."
        else:
            return "Function not recognised."

    def fn_ops(self,args,client,destination):
        'Modify ops list. Add, list or delete. Format: ops <add/list/del> <username>'
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Insufficient privileges to modify ops list."
        args_split = args.lower().split()
        if(len(args_split)<2 and args_split[0]!='list'):
            return "Invalid number of arguments, please provide a username and a function."
        if(args_split[0] in ['add','list','del','delete','remove']):
            rawfunc = args_split[0]
            if(len(args_split)>1):
                nick = args_split[1]
        elif(args_split[1] in ['add','del','delete','remove']):
            rawfunc = args_split[1]
            nick = args_split[0]
        else:
            return "Please specify a function. Valid functions are: add, list and delete."
        if(rawfunc == 'add'):
            if(not ircbot_chk.ircbot_chk.chk_nickregistered(self,destination[0],nick)):
                return "This person's not registered, so I can't add them to the ops list."
            if(nick in self.conf['server'][destination[0]]['ops']):
                return "This person is already in the ops list."
            self.conf['server'][destination[0]]['ops'].append(nick)
            return "Added " + nick + " to the ops list for this server."
        elif(rawfunc == 'list'):
            return "Ops list for this server: " + ', '.join(self.conf['server'][destination[0]]['ops']) + '.'
        elif(rawfunc in ['del','delete','remove']):
           if(args not in self.conf['server'][destination[0]]['ops']):
               return "That person isn't even in the ops list."
           self.conf['server'][destination[0]]['ops'].remove(nick)
           return "Removed " + args + " from the ops list."
        else:
           return "Function not recognised."

    def fn_ignore_list(self,args,client,destination):
        'Modify ignore list. Add, list or delete. Format: ignore_list <add/list/del> <username>'
        if(not ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return "Insufficient privileges to modify ignore list."
        args_split = args.lower().split()
        if(len(args_split)<2 and args_split[0]!='list'):
            return "Invalid number of arguments, please provide a username and a function."
        if(args_split[0] in ['add','list','del','delete','remove']):
            rawfunc = args_split[0]
            if(len(args_split)>1):
                nick = args_split[1]
        elif(args_split[1] in ['add','del','delete','remove']):
            rawfunc = args_split[1]
            nick = args_split[0]
        else:
            return "Please specify a function. Valid functions are: add, list and delete."
        if(rawfunc == 'add'):
            if('ignore_list' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'] = []
            if(nick in self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']):
                return "This person is already on the ignore list."
            self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'].append(nick)
            return "Added " + args + " to the ignore list."
        elif(rawfunc == 'list'):
            if('ignore_list' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                return "There is no ignore list for this channel."
            return "Users on ignore list for this channel: " + ', '.join(self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']) + "."
        elif(rawfunc in ['del','delete','remove']):
            if('ignore_list' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                return "There isn't an ignore list for this channel."
            if(nick not in self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']):
                return nick + " isn't even on the ignore list for " + destination[1] + "."
            self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'].remove(nick)
            return "Removed " + nick + " from the ignore list."
        else:
            return "Function not recognised."

    def fn_nickserv_registered(self,args,client,destination):
        'Modify nickserv registered list. Add, list or delete. Format: nickserv_registered <add/list/del> <message>'
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Insufficient privileges to modify nickserv_registered list."
        args_split = args.lower().split()
        if(len(args_split)<2 and args_split[0]!='list'):
            return "Invalid number of arguments, please provide a message and a function."
        if(args_split[0] in ['add','list','del','delete','remove']):
            rawfunc = args_split[0]
            if(len(args_split)>1):
                message = ''.join(args_split[1:])
        elif(args_split[-1] in ['add','del','delete','remove']):
            rawfunc = args_split[-1]
            message = ''.join(args_split[:-1])
        else:
            return "Please specify a function. Valid functions are: add, list and delete."
        if(rawfunc == 'add'):
            if(message in self.conf['nickserv']['registered']):
                return "This message is already on the nickserv registered list."
            self.conf['nickserv']['registered'].append(message)
            return "Added " + message + " to the nickserv registered list."
        elif(rawfunc == 'list'):
            return "Nick registered nickserv messages: " + ', '.join(self.conf['nickserv']['registered']) + "."
        elif(rawfunc in ['del','delete','remove']):
            if(message not in self.conf['nickserv']['registered']):
                return "This message isn't even on the nickserv registered list."
            self.conf['nickserv']['registered'].remove(message)
            return "Removed " + message + " from nickserv registered list."
        else:
            return "Function not recognised."

    def fn_nickserv_online(Self,args,client,destination):
        'Modify nickserv online list. Add, list or delete. Format: nickserv_online <add/list/del> <message>'
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            return "Insufficient privileges to modify nickserv_online list."
        args_split = args.lower().split()
        if(len(args_split)<2 and args_split[0]!='list'):
            return "Invalid number of arguments, please provide a message and a function."
        if(args_split[0] in ['add','list','del','delete','remove']):
            rawfunc = args_split[0]
            if(len(args_split)>1):
                message = ''.join(args_split[1:])
        elif(args_split[-1] in ['add','del','delete','remove']):
            rawfunc = args_split[-1]
            message = ''.join(args_split[:-1])
        else:
            return "Please specify a function. Valid functions are: add, list and delete."
        if(rawfunc == 'add'):
            if(message in self.conf['nickserv']['online']):
                return "This message is already on the nickserv online list."
            self.conf['nickserv']['online'].append(message)
            return "Added " + message + " to the nickserv registered list."
        elif(rawfunc == 'list'):
            return "Nick online nickserv messages: " + ', '.join(self.conf['nickserv']['online']) + "."
        elif(rawfunc in ['del','delete','remove']):
            if(message not in self.conf['nickserv']['online']):
                return "This message isn't even on the nickserv online list."
            self.conf['nickserv']['online'].remove(message)
            return "Removed " + message + " from nickserv online list."
        else:
            return "Function not recognised."

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
        args = args.lower().split()
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

    def fn_nicklist(self,args,client,destination):
        'Returns a user list for a given channel. format: nicklist <channel>'
        channels = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args)
        if(channels[0][0] is None):
            return "This is not a valid channel, or one I am not part of."
        output = []
        for channel in channels:
            userlist = self.core['server'][channel[0]]['channel'][channel[1]]['user_list']
            output.append("Users in " + channel[0] + ":" + channel[1] + "> (" + str(len(userlist)) + ") " + ', '.join(userlist) + ".")
        return "\n".join(output)

    def fn_nicklist_fix(self,args,client,destination):
        'fixing user lists. temp function. lowercases everyone.'
        for server in self.core['server']:
            for channel in self.core['server'][server]['channel']:
                names = ircbot_chk.ircbot_chk.chk_names(self,server,channel)
                namesprocessed = []
                for name in names:
                    name = name.lower()
                    if(name[0] in ['+','@','~','&']):
                        name = name[1:]
                    namesprocessed.append(name)
                self.core['server'][server]['channel'][channel]['user_list'] = namesprocessed
        return "Success?"




