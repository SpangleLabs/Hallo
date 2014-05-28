import ircbot_chk

endl = '\r\n'
class mod_chan_ctrl:
    
    def fn_op(self, args, client, destination):
        'Op member in given channel, or current channel if no channel given. Or command user if no member given. Format: op <name> <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.split()
                args[1] = ''.join(args[1:])
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    nick = args[1]
                elif(args[1] in self.comf['server'][destination[0]]['channel']):
                    channel = args[1]
                    nick = args[0]
                else:
                    return 'Multiple arguments given, but neither are a valid channel.'
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' +o ' + nick + endl).encode('utf-8'))
                return 'Op status given to ' + nick + ' in ' + channel + '.'
            elif(args.replace(' ','')!=''):
                if(args[0]=='#'):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +o ' + client + endl).encode('utf-8'))
                    return 'Op status given to you in ' + args + '.'
                else:
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +o ' + args + endl).encode('utf-8'))
                    return 'Op status given to ' + args + '.'
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +o ' + client + endl).encode('utf-8'))
                return 'Op status given.'
        else:
            return 'Insufficient privileges to add op status.'
    
    def fn_deop(self, args, client, destination):
        'Deop member in given channel, or current channel if no channel given. Or command user if no member given. Format: deop <name> <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.split()
                args[1] = ''.join(args[1:])
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    nick = args[1]
                elif(args[1] in self.comf['server'][destination[0]]['channel']):
                    channel = args[1]
                    nick = args[0]
                else:
                    return 'Multiple arguments given, but neither are a valid channel.'
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -o ' + nick + endl).encode('utf-8'))
                return 'Op status taken from ' + nick + ' in ' + channel + '.'
            elif(args.replace(' ','')!=''):
                if(args[0]=='#'):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' -o ' + client + endl).encode('utf-8'))
                    return 'Op status taken from you in ' + args + '.'
                else:
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -o ' + args + endl).encode('utf-8'))
                    return 'Op status taken from ' + args + '.'
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -o ' + client + endl).encode('utf-8'))
                return 'Op status taken.'
        else:
            return 'Insufficient privileges to take op status.'

    def fn_voice(self,args,client,destination):
        'Voice member in given channel, or current channel if no channel given, or command user if no member given. Format: voice <name> <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(len(args.split())>=2):
                args = args.split()
                args[1] = ''.join(args[1:])
                if(args[0] in self.conf['server'][destination[0]]['channel']):
                    channel = args[0]
                    nick = args[1]
                elif(args[1] in self.comf['server'][destination[0]]['channel']):
                    channel = args[1]
                    nick = args[0]
                else:
                    return 'Multiple arguments given, but neither are a valid channel.'
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' +v ' + nick + endl).encode('utf-8'))
                return 'Voice status given to ' + nick + ' in ' + channel + '.'
            elif(args.replace(' ','')!=''):
                if(args[0]=='#'):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +v ' + client + endl).encode('utf-8'))
                    return 'Voice status given to you in ' + args + '.'
                else:
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v ' + args + endl).encode('utf-8'))
                    return 'Voice status given to ' + args + '.'
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +v ' + client + endl).encode('utf-8'))
                return 'Voice status given.'
        else:
            return 'Insufficient privileges to add voice status.'

    def fn_devoice(self,args,client,destination):
        'Voice member in given channel, or current channel if no channel given, or command user if no member given. Format: voice <name> <channel>'
        if(len(args.split())>=2):
            args = args.split()
            args[1] = ''.join(args[1:])
            if(args[0] in self.conf['server'][destination[0]]['channel']):
                channel = args[0]
                nick = args[1]
            elif(args[1] in self.comf['server'][destination[0]]['channel']):
                channel = args[1]
                nick = args[0]
            else:
                return 'Multiple arguments given, but neither are a valid channel.'
            if(nick.lower() == client.lower()):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -v ' + nick + endl).encode('utf-8'))
                return 'Voice status remove from ' + nick + ' in ' + channel + '.'
            else:
                if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + channel + ' -v ' + nick + endl).encode('utf-8'))
                    return 'Voice status removed from ' + nick + ' in ' + channel + '.'
                else:
                    return 'Insufficient privileges to remove voice status.'
        elif(args.replace(' ','')!=''):
            if(args[0]=='#'):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' -v ' + client + endl).encode('utf-8'))
                return 'Voice status taken from you in ' + args + '.'
            else:
                if(args.lower() == client.lower()):
                    self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + args + endl).encode('utf-8'))
                    return 'Voice status taken from ' + args + '.'
                else:
                    if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
                        self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + args + endl).encode('utf-8'))
                        return 'Voice status taken from ' + args + '.'
                    else:
                        return 'Insufficient privileges to remove voice status.'
        else:
            self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -v ' + client + endl).encode('utf-8'))
            return 'Voice status taken.'

    def fn_invite(self,args,client,destination):
        'Invite someone to a channel'
        args_split = args.split()
        if(not ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return "This function is for ops only."
        if(len(args_split) == 1):
            if(ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])[0][0] is not None):
                nick = client
                channel = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])
            else:
                nick = args_split[0]
                channel = [destination]
        else:
            if(ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])[0][0] is not None):
                nick = args_split[1]
                channel = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])
            elif(ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[1])[0][0] is not None):
                nick = args_split[0]
                channel = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[1])
            else:
                return "Invalid channel."
        channels = []
        for destpair in channel:
            if(destpair[0]==destination[0]):
                channels.append(destpair[1])
        for chan in channels:
            self.core['server'][destination[0]]['socket'].send(('INVITE '  + nick + ' ' + chan + endl).encode('utf-8'))
        return "Invited " + nick + " to " + ', '.join(channels) + "."

    def fn_mute(self,args,client,destination):
        'Mutes a given channel or current channel. Format: mute <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.replace(' ','')
            if(args==''):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' +m ' + endl).encode('utf-8'))
                return "Muted the channel."
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' +m ' + endl).encode('utf-8'))
                return "Muted " + args + "."
        else:
            return "You have insufficient privileges to use this function."

    def fn_unmute(self,args,client,destination):
        'Unmutes a given channel or current channel if none is given. Format: unmute <channel>'
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            args = args.replace(' ','')
            if(args==''):
                self.core['server'][destination[0]]['socket'].send(('MODE ' + destination[1] + ' -m ' + endl).encode('utf-8'))
                return "Unmuted channel."
            else:
                self.core['server'][destination[0]]['socket'].send(('MODE ' + args + ' -m ' + endl).encode('utf-8'))
                return "Unmuted " + args + "."
        else:
            return "You have insufficient privileges to use this function."

    def fn_staff(self,args,client,destination):
        'Sends a message to all online staff members, and posts a message in the staff channel. Format: staff <message>'
        if(not ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if('admininform' in self.conf['server'][destination[0]]):
                for admin in ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],self.conf['server'][destination[0]]['admininform']):
                    self.base_say(client + ' has sent a message to all staff members. The message is as follows: ' + args,[destination[0],admin])
            if('admininform_chan' in self.conf['server'][destination[0]]):
                for adminchan in self.conf['server'][destination[0]]['admininform_chan']:
                    self.base_say(client + ' has sent a message to all staff members. The message is as follows: ' + args,[destination[0],adminchan])
            return "Message delivered. A staff member will be in contact with you shortly. :)"

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

    def fn_auto(self,args,client,destination):
        'Automatically apply flags to a user when they join a channel. Format: auto add {user} {flags} {channel}, auto list {channel}, or auto del {user} {channel}'
        args = args.split()
        cmd = ''
        user = ''
        chan = ''
        flags = ''
        if(not ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return "This function is for ops only."
        for arg in args:
            if(cmd=='' and arg.lower() in ['add','list','del','delete','remove']):
                if(arg in ['add']):
                    cmd = 'add'
                elif(arg in ['list']):
                    cmd = 'list'
                elif(arg in ['del','delete','remove']):
                    cmd = 'del'
                else:
                    cmd = 'list'
            elif(flags=='' and len(arg)==2 and arg[0] in ['-','+']):
                flags = arg
            elif(chan=='' and ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,arg.lower())[0][0] is not None):
                chan = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,arg.lower())
            elif(user==''):
                user = arg.lower()
            else:
                return "I do not understand your inputs. Please input a command and its required data. add commands requires user and flags (channel optional.) list command requires channel (optional). del command requires user (channel optional.)"
        if(cmd==''):
            return "Please specify a command. Either add, list or delete."
        if(chan==''):
            chan = [destination]
        if(cmd=='add'):
            if(user=='' or flags==''):
                return "You must specify a user and flags to apply to that user."
            chandone = []
            output = []
            for channel in chan:
                if(channel[0] not in [channeldone[0] for channeldone in chandone] and not ircbot_chk.ircbot_chk.chk_op(self,channel[0],client)):
                    output.append('You are not in op list for ' + channel[0])
                    continue
                if(channel[0] not in [channeldone[0] for channeldone in chandone] and not ircbot_chk.ircbot_chk.chk_nickregistered(self,channel[0],user)):
                    output.append('User ' + user + " is not registered on " + channel[0])
                    continue
                if('auto_list' not in self.conf['server'][channel[0]]['channel'][channel[1]]):
                    self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list'] = []
                if({'user':user,'flag':'+'+flags[1]} in self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list'] or {'user':user,'flag':'-'+flags[1]} in self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list']):
                    output.append("User " + user + " already has that flag or an opposing flag in " + channel[0] + ":" + channel[1])
                    continue
                if(channel[0] not in [channeldone[0] for channeldone in chandone] and ircbot_chk.ircbot_chk.chk_userregistered(self,channel[0],user)):
                    self.core['server'][channel[0]]['socket'].send(('MODE ' + channel[1] + ' ' + flags + ' ' + user + endl).encode('utf-8'))
                chandone.append(channel)
                self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list'].append({'user': user,'flag': flags})
            return "".join([outputline + "\n" for outputline in output]) + "I will automatically add the " + flags + " flag to " + user + " whenever they join " + ', '.join([channel[0] + ':' + channel[1] for channel in chandone]) + "."
        if(cmd=='list'):
            output = []
            for channel in chan:
                if('auto_list' in self.conf['server'][channel[0]]['channel'][channel[1]]):
                    output.append(channel[0] + ":" + channel[1] + "> " + ', '.join([entry['flag'] + ' ' + entry['user'] for entry in self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list']]))
            if(len(output)==0):
                return "There are no autoflags set for that channel"
            return "\n".join(output)
        if(cmd=='del'):
            if(user==''):
                return "Please specify a user to remove flags from."
            chandone = []
            output = []
            for channel in chan:
                if(channel[0] not in [channeldone[0] for channeldone in chandone] and not ircbot_chk.ircbot_chk.chk_op(self,channel[0],client)):
                    output.append('You are not in op list for ' + channel[0])
                    continue
                if('auto_list' not in self.conf['server'][channel[0]]['channel'][channel[1]]):
                    continue
                if(user not in [entry['user'] for entry in self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list']]):
                    continue
                for userentry in [entry for entry in self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list'] if entry['user'] == user]:
                    self.conf['server'][channel[0]]['channel'][channel[1]]['auto_list'].remove(userentry)
                    output.append('Removed ' + userentry['flag'] + ' flag from ' + user + ' in ' + channel[0] + ':' + channel[1])
            if(len(output)==0):
                return "There are no autoflags set for that user in that channel."
            return "Removed all auto flags for " + user + " on " + ', '.join([channel[0] + ':' + channel[1] for channel in chan]) + "."

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
            channel = args.split()[0].lower()
            message = ' '.join(args.split()[1:])
            if(channel in self.conf['server'][destination[0]]['channel']):
                self.conf['server'][destination[0]]['channel'][channel]['swearlist']['commentmsg'] = message
                return "Set swear comment message to: " + message + "."
            else:
                return "I'm not in that channel."
        else:
            return "Insufficient privileges to set swear comment message."

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

