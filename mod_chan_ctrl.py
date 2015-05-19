import ircbot_chk

endl = '\r\n'
class mod_chan_ctrl:

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

