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

