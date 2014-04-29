import ircbot_chk
import sys
from threading import Thread
import collections

class hallobase_ctrl:

    def fn_say(self,args,client,destination):
        'Say a message into a channel or server/channel pair (in the format "{server,channel}"). Format: say <channel> <message>'
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
                return "Messages sent to " + str(len([destpair for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])-skipped) + " channels: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if sel.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']]) + " But not sent to " + str(skipped) + " channels, due to swearlist violation: " + ', '.join(["{" + destpair[0] + "," + destpair[1] + "}" for destpair in destlist if self.conf['server'][destpair[0]]['channel'][destpair[1]]['in_channel']])

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

