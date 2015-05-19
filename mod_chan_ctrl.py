import ircbot_chk

endl = '\r\n'
class mod_chan_ctrl:

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
        args = args.strip()
        if(ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            if(args==''):
                self.conf['server'][destination[0]]['channel'][destination[1]]['logging'] = not self.conf['server'][destination[0]]['channel'][destination[1]]['logging']
                return "Logging toggled."
            elif(' ' in args):
                args_split = args.split()
                destchk = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[0])
                command = args_split[1]
                if(destchk[0][0] is None):
                    destchk = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args_split[1])
                    command = args_split[0]
                    if(destchk[0][0] is None):
                        print(destchk[0][1])
                        return "Unrecognised destination."
                for destchk_chan in destchk:
                    if(command in ['toggle']):
                        self.conf['server'][destchk_chan[0]]['channel'][destchk_chan[1]]['logging'] = not self.conf['server'][destchk_chan[0]]['channel'][destchk_chan[1]]['logging']
                    elif(command in ['true','1','on']):
                        self.conf['server'][destchk_chan[0]]['channel'][destchk_chan[1]]['logging'] = True
                    elif(command in ['false','0','off','none']):
                        self.conf['server'][destchk_chan[0]]['channel'][destchk_chan[1]]['logging'] = False
                    else:
                        return "Unrecognised command."
                return "Logging status changed in: " + ', '.join(['{'+destchk_chan[0]+','+destchk_chan[1]+'}' for destchk_chan in destchk]) + '.'
            elif(args.lower() in ['true','1','on']):
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

