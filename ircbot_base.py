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

    def fn_kick(self, args, client, destination):
        'Kick given user in given channel, or current channel if no channel given.'
        check = ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)
        if(check):
            if(len(args.split())>=2):
                user = args.split()[0]
                channel = args.split()[1]
                message = ' '.join(args.split()[2:])
                self.core['server'][destination[0]]['socket'].send(('KICK ' + channel + ' ' + user + ' ' + message + endl).encode('utf-8'))
                return 'Kicked ' + user + ' from ' + channel + '.'
            elif(args.replace(' ','')!=''):
                args = args.replace(' ','')
                channel = destination[1]
                self.core['server'][destination[0]]['socket'].send(('KICK ' + channel + ' ' + args + endl).encode('utf-8'))
                return 'Kicked ' + args + '.'
            else:
                return 'Please, tell me who to kick.'
        else:
            return 'Insufficient privileges to kick.'

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
                self.conf['server'][title]['port'] = self.conf['server'][destination[0]]['port']
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

    def fn_voice_add(self,args,client,destination):
        'Adds a user to psuedoautovoice, format is "voice_add {user} {channel}"'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.lower()
            channel = destination[1]
            if(len(args.split())>1):
                channel = args.split()[1]
                args = args.split()[0]
            if(args not in self.conf['server'][destination[0]]['channel'][channel]['voice_list']):
                if(ircbot_chk.ircbot_chk.chk_nickregistered(self,destination[0],args)):
                    self.conf['server'][destination[0]]['channel'][channel]['voice_list'].append(args)
                    if(ircbot_chk.ircbot_chk.chk_userregistered(self,destination[0],args)):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' +v ' + args + endl).encode('utf-8'))
                    return "Added " + args + " to the pseudoautovoice list for " + channel + "."
                else:
                    return "It seems that " + args + " isn't a registered nick."
            else:
                return args + " is already on my pseudo-auto-voice list for " + channel + "."
        else:
            return "Sorry, this function is for ops only."

    def fn_voice_list(self,args,client,destination):
        'Lists users on pseudoautovoice, ops only. no arguments, or channel to list'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(args==''):
                args = destination[1]
            return "Users on pseudoautovoice list for " + args + ": " + ', '.join(self.conf['server'][destination[0]]['channel'][args]['voice_list']) + "."
        else:
            return "Sorry, this function is for ops only."

    def fn_voice_del(self,args,client,destination):
        'Remove a user from autovoice list, ops only. same arguments as voice_add'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.lower()
            channel = destination[1]
            if(len(args.split())>1):
                channel = args.split()[1]
                args = args.split()[0]
            if(args in self.conf['server'][destination[0]]['channel'][channel]['voice_list']):
                self.conf['server'][destination[0]]['channel'][channel]['voice_list'].remove(args)
                return "Removed " + args + " from pseudo-auto-voice list for " + channel + "."
            else:
                return args + " isn't even on the autovoice list for " + channel + "."
        else:
            return "Sorry, this function is for ops only."

    def fn_admin_inform_add(self,args,client,destination):
        'Add a user to the admin swear inform list, ops only.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if(args not in self.conf['server'][destination[0]]['admininform']):
                self.conf['server'][destination[0]]['admininform'].append(args)
                return "Added " + args + " to the admininform list."
            else:
                return "This person is already on the admininform list."
        else:
            return "Sorry, this function is for ops only."

    def fn_admin_inform_list(self,args,client,destination):
        'Lists users who are informed when sweardetect detects swearing.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return "Users on admininform for this server: " + ', '.join(self.conf['server'][destination[0]]['admininform']) + "."
        else:
            return "Sorry, this function is for ops only."

    def fn_admin_inform_del(self,args,client,destination):
        'Delete a user from being informed about swearing in selected channels'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if(args in self.conf['server'][destination[0]]['admininform']):
                self.conf['server'][destination[0]]['admininform'].remove(args)
                return "Removed " + args + " from admininform list."
            else:
                return args + " isn't even on the admininform list for " + destination[0] + "."
        else:
            return "Sorry, this function is for ops only."

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

    def fn_admininform_del(self,args,client,destination):
        'Delete a user from the ignore list for this channel. Ops only.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.lower().replace(' ','')
            if('ignore_list' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'] = []
            if(args in self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list']):
                self.conf['server'][destination[0]]['channel'][destination[1]]['ignore_list'].remove(args)
                return "Removed " + args + " from ignore list."
            else:
                return args + " isn't even on the ignore list for " + destination[1] + " on " + destination[0] + "."
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_add(self,args,client,destination):
        'Add a swear to a channel swear list, format is "swear_add <list> <channel> <swearregex>". List is either "possible", "inform" or "comment"'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=3):
                args = args.split()
                args[2] = ' '.join(args[2:])
                if(args[0].lower() in ['possible','inform','comment']):
                    list = args[0].lower()
                    del args[0]
                elif(args[1].lower() in ['possible','inform','comment']):
                    list = args[1].lower()
                    del args[1]
                elif(args[2].lower() in ['possible','inform','comment']):
                    list = args[2].lower()
                    del args[2]
                else:
                    return "No valid lists given. Valid lists are 'possible', 'inform' or 'comment'."
                if(args[0].lower() in self.conf['server'][destination[0]]['channel']):
                    channel = args[0].lower()
                    regex = args[1]
                elif(args[1].lower() in self.conf['server'][destination[0]]['channel']):
                    channel = args[1].lower()
                    regex = args[0]
                else:
                    return "I'm not in that channel."
                self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()].append(regex)
                return "Added " + regex + " to " + list + " swear list for " + channel + "."
            else:
                return "Not enough arguments, remember to provide me with a list, then channel, then the regex for the swear you want to add. Lists are either 'possible', 'inform' or 'comment'."
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_list(self,args,client,destination):
        'Lists swears in a given channel. Format is swear_list <list> <channel>. Please only ask for this in privmsg.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.lower().split()
                if(args[0] in ['possible','inform','comment']):
                    list = args[0]
                    channel = args[1]
                elif(args[1] in ['possible','inform','comment']):
                    list = args[1]
                    channel = args[0]
                else:
                return "That's not a valid list."
                if(channel in self.conf['server'][destination[0]]['channel']):
                    if(destination[1]!=channel):
                        return "Here is the " + list + " swear list for " + channel + ": " + ', '.join(self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()]) + "."
                    else:
                        return "I'm not printing a swear list in a channel."
                else:
                    return "I'm not even in that channel."
            else:
                return "That's not enough arguments, remember to provide me with a list, then a channel. Lists are either 'possible', 'inform' or 'comment'."
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_del(self,args,client,destination):
        'Deletes a swear from a swear list, format is "swear_del <list> <channel> <swearregex>". List is either "possible", "inform" or "comment"'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=3):
                args = args.lower().split()
                args[2] = ' '.join(args.split()[2:])
                if(args[0] in ['possible','inform','comment']):
                    list = args[0]
                    del args[0]
                elif(args[1] in ['possible','inform','comment']):
                    list = args[1]
                    del args[1]
                elif(args[2] in ['possible','inform','comment']):
                    list = args[2]
                    del args[2]
                else:
                    return "That's not a valid list. Valid lists are 'possible', 'inform' or 'comment'."
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    regex = args[1]
                elif(args[1] in self.conf['server'][destination[0]]['channel']):
                    channel = args[1]
                    regex = args[0]
                else:
                    return "I'm not in that channel."
                if(regex in self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()]):
                    self.conf['server'][destination[0]]['channel'][channel]['swearlist'][list.lower()].remove(regex)
                    return "Removed " + regex + " from " + list + " swear list for " + channel + "."
                else:
                    return "That's not in the " + list + " swear list for " + channel + "."
            else:
                return "Not enough arguments, remember to provide me with a list, then channel, then the regex for the swear you want to remove. Lists are either 'possible', 'inform' or 'comment'."
        else:
            return "Sorry, this function is for ops only."

    def fn_swear_comment_message(self,args,client,destination):
        'Set the message for comment swears, format is "swear_comment_message <channel> <message>" {swear} in the message will be replaced with the swear that was used.'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            channel = args.split()[0]
            message = ' '.join(args.split()[1:])
            if(channel in self.conf['server'][destination[0]]['channel']):
                self.conf['server'][destination[0]]['channel'][channel]['swearlist']['commentmsg'] = message
                return "Set swear comment message to: " + message + "."
            else:
                return "I'm not in that channel."
        else:
            return "Insufficient privileges to set swear comment message."

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

    def fn_channel_caps(self,args,client,destination):
        'Sets or toggles caps lock for channel, ops only'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['caps'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['caps']
                return "Caps lock toggled."
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['caps'] = True
                return "Caps lock on."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['caps'] = False
                return "Caps lock off."
        else:
            return "Insufficient privileges to set caps lock."

    def fn_channel_logging(self,args,client,destination):
        'Sets or toggles logging for channel, ops only'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['logging']
                return "Logging toggled."
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = True
                return "Logging on."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = False
                return "Logging off."
        else:
            return "Insufficient privileges to set logging."

    def fn_channel_megahal_record(self,args,client,destination):
        'Sets or toggles megahal recording for channel, gods only'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record']
                return "Megahal recording toggled."
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] = True
                return "Megahal recording on."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['megahal_record'] = False
                return "Megahal recording off."
        else:
            return "Insufficient privileges to set megahal recording."

    def fn_channel_swear_detect(self,args,client,destination):
        'Sets or toggles sweardetection for channel, ops only'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect']
                return "Swear detection toggled."
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect'] = True
                return "Swear detection on."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect'] = False
                return "Swear detection off."
        else:
            return "Insufficient privileges to set swear detection."

    def fn_channel_passive_func(self,args,client,destination):
        'Sets or toggles passive functions for channel, gods only'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc']
                return "Passive functions toggled."
            elif(args.lower()=='true' or args.lower()=='1' or args.lower()=='on'):
                self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc'] = True
                return "Passive functions on."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc'] = False
                return "Passive functions off."
        else:
            return "Insufficient privileges to set passive functions status."

    def fn_channel_idle_time(self,args,client,destination):
        'Sets the amount of time a channel can be idle before idle channel functions activate, gods only'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(args==''):
                return "Please provide a time, in seconds, before idle channel functions activate."
            else:
                self.conf['server'][destination[0]]['channel'][destination[1]]['idle_time'] = int(args)
                if('idle_args' not in self.conf['server'][destination[0]]['channel'][destination[1]]):
                    self.conf['server'][destination[0]]['channel'][destination[1]]['idle_args'] = ''
                return "Idle time set to " + args + " seconds."
        else:
            return "Insufficient privileges to set idle channel time."

    def fn_channel_idle_args(self,args,client,destination):
        'Sets the arguments to pass to the idle channel function, gods only'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            self.conf['server'][destination[0]]['channel'][destination[1]]['idle_args'] = args
            return "Idle channel arguments set to: " + args + "."
        else:
            return "Insufficient privileges to set idle channel arguments."

    def fn_channel_pass(self,args,client,destination):
        'Sets a password for a channel, use channel_pass {channel} {password}'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            channel = args.split()[0]
            password = args[len(channel):]
            while(len(password)>0 and password[0]==' '):
                password = password[1:]
            while(len(password)>0 and password[-1:]==' '):
                password = password[:-1]
            self.conf['server'][destination[0]]['channel'][destination[1]]['pass'] = password
            return "Stored password for " + destination[1] + "."
        else:
            return "Insufficient privileges to set channel password."

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
                link = "http://hallo.dr-spangle.com/" + filename
                file = open("../http/" + filename,'w')
                file.write(prettycore)
                file.close()
                self.base_say("Core written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../http/" + filename)
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
                link = "http://hallo.dr-spangle.com/" + filename
                file = open("../http/" + filename,'w')
                file.write(prettyconf)
                file.close()
                self.base_say("Config written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../http/" + filename)
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

