import ircbot_chk
import collections

endl = '\r\n'
class hallobase_ctrl:

    def fn_say(self,args,client,destination):
        'Say a message into a channel or server/channel pair (in the format "{server,channel}"). Format: say <channel> <message>'
        if(not ircbot_chk.ircbot_chk.chk_op(self,destination[0],client)):
            return 'Insufficient privileges to speak as hallo.'
        dest = args.split()[0]
        message = ' '.join(args.split()[1:])
        destlist = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,dest)
        if(len(destlist)==1 and destlist[0][0] is None):
            return "Failed to find destination, error returned was: " + destlist[0][1]
        skipped = 0
        for destpair in destlist:
            if(ircbot_chk.ircbot_chk.chk_swear(self,destpair[0],destpair[1],message)!=['none','none']):
                skipped = skipped + 1
            else:
                if(self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']):
                    self.base_say(message,destpair)
        if(skipped==0):
            if(len(destlist)==1):
                return "Message sent."
            else:
                return "Messages sent to " + str(len([destpair for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])) + " channels: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])
        else:
            if(len(destlist)==1):
                return "That message contains a word which is on the swearlist for that channel."
            else:
                return "Messages sent to " + str(len([destpair for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])-skipped) + " channels: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']]) + " But not sent to " + str(skipped) + " channels, due to swearlist violation: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])

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
#                functions = functions + [ module + '.' + module + '.' + i for i in dir(getattr(__import__(module),module))]
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

