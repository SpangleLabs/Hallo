import ircbot_chk


endl = '\r\n'
class hallobase_oper:

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

    def fn_nickserv_online(self,args,client,destination):
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
#            self.conf['server'][destination[0]]['nick'] = args
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

    def fn_nicklist(self,args,client,destination):
        'Returns a user list for a given channel. format: nicklist <channel>'
        channels = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args)
        if(channels[0][0] is None):
            return "This is not a valid channel, or one I am not part of. Error returned was: " + channels[0][1]
        output = []
        for channel in channels:
            userlist = self.core['server'][channel[0]]['channel'][channel[1]]['user_list']
            output.append("Users in " + channel[0] + ":" + channel[1] + "> (" + str(len(userlist)) + ") " + ', '.join(userlist) + ".")
        return "\n".join(output)

    def fn_nicklist_fix(self,args,client,destination):
        'fixing user lists. temp function. lowercases everyone.'
        for server in self.core['server']:
            if(not self.conf['server'][server]['connected']):
                continue
            for channel in self.core['server'][server]['channel']:
                if(not self.conf['server'][server]['channel'][channel]['in_channel']):
                    continue
                names = ircbot_chk.ircbot_chk.chk_names(self,server,channel)
                namesprocessed = []
                for name in names:
                    name = name.lower()
                    if(name[0] in ['+','%','@','~','&']):
                        name = name[1:]
                    namesprocessed.append(name)
                self.core['server'][server]['channel'][channel]['user_list'] = namesprocessed
        return "Success?"




