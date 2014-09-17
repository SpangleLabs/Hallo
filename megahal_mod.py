import time

import megahal
import ircbot_chk


class megahal_mod():

    def fn_speak(self,args,client,destination):
        'He can talk!'
#        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
        if(True):
            chan_filename = 'store/brains/megahal_' + destination[0] + '_' + destination[1] + '.jar'
            diffchannel = False
            if(args.split()[0][0]=='{' and args.split()[0][-1]=='}'):
                diffchannel = True
                chancode = args.split()[0][1:-1]
                if(',' in chancode):
                    if(chancode[0]=='#'):
                        chan_filename = 'store/brains/megahal_' + destination[0] + '_' + chancode.split(',')[0] + '_' + chancode.split(',')[1] + '.jar'
                    elif(len(chancode.split(','))==2):
                        chan_filename = 'store/brains/megahal_' + chancode.split(',')[0] + '_' + chancode.split(',')[1] + '.jar'
                    else:
                        chan_filename = 'store/brains/megahal_' + chancode.split(',')[0] + '_' + chancode.split(',')[1] + '_' + chancode.split(',')[2] + '.jar'
                elif(chancode[0]=='#'):
                    chan_filename = 'store/brains/megahal_' + destination[0] + '_' + chancode + '.jar'
                else:
                    chan_filename = 'store/brains/megahal_' + destination[0] + '_' + destination[1] + '_' + chancode + '.jar'
                args = ' '.join(args.split()[1:])
            if(chan_filename in self.megahal):
                self.megahal[chan_filename]['last_used'] = int(time.time())
                if(diffchannel):
                    reply = self.megahal[chan_filename]['brain'].get_reply_nolearn(args)
                else:
                    reply = self.megahal[chan_filename]['brain'].get_reply_nolearn(args)
            else:
                self.megahal[chan_filename] = {}
                self.megahal[chan_filename]['last_used'] = int(time.time())
                self.megahal[chan_filename]['brain'] = megahal.MegaHAL(4,chan_filename)
                if(diffchannel):
                    reply = self.megahal[chan_filename]['brain'].get_reply_nolearn(args)
                else:
                    reply = self.megahal[chan_filename]['brain'].get_reply_nolearn(args)
            return client + ": " + reply

    def fn_speak_learn(self,args,client,destination):
        'Teach him a file, gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            chan_filename = 'store/brains/megahal_' + destination[0] + '_' + destination[1] + '.jar'
            if(chan_filename in self.megahal):
                self.megahal[chan_filename]['last_used'] = int(time.time())
                self.megahal[chan_filename]['brain'].train(args)
                self.megahal[chan_filename]['last_used'] = int(time.time())
            else:
                self.megahal[chan_filename] = {}
                self.megahal[chan_filename]['last_used'] = int(time.time())
                self.megahal[chan_filename]['brain'] = megahal.MegaHAL(4,chan_filename)
                self.megahal[chan_filename]['brain'].train(args)
                self.megahal[chan_filename]['last_used'] = int(time.time())
            return "Learnt the file " + args + " ... hopefully."
        else:
            return "You're not spangle."

    def fn_megahal_close(self,args,client,destination):
        'sync and close all open megahal brains.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            for filename in self.megahal:
                self.megahal[filename]['brain'].sync()
                self.megahal[filename]['brain'].close()
                print("Closed megahal brain: " + filename)
            del self.megahal
            self.megahal = {}
            return "Closed all active brains."
        else:
            return "Insufficient privileges to close all brains."

    def fn_megahal_clear(self,args,client,destination):
        'close all brains without syncing'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            for filename in self.megahal:
                if('brain' in self.megahal[filename]):
                    self.megahal[filename]['brain'].close()
                    print("Closed megahal brain: " + filename)
            del self.megahal
            self.megahal = {}
            return "Shut down all active brains."
        else:
            return "Insufficient privileges to shut down all brains."

    def fn__s(self,args,client,destination):
        'redirects to speak function'
        return self.fn_speak(args,client,destination)

    def fnn_megahalrecord(self,args,client,destination):
        'Record a line into the brains.'
        pass
#        chan_filename = 'store/brains/megahal_' + destination[0] + '_' + destination[1] + '.jar'
#        if(chan_filename in self.megahal):
#            if('brain' in self.megahal[chan_filename]):
#                self.megahal[chan_filename]['brain'].learn(args)
#                self.megahal[chan_filename]['last_used'] = int(time.time())
#        else:
#            self.megahal[chan_filename] = {}
#            self.megahal[chan_filename]['last_used'] = int(time.time())
#            self.megahal[chan_filename]['brain'] = megahal.MegaHAL(4,chan_filename)
#            self.megahal[chan_filename]['brain'].learn(args)
#            self.megahal[chan_filename]['last_used'] = int(time.time())
#        user_filename = 'store/brains/megahal_' + destination[0] + '_' + destination[1] + '_' + client + '.jar'
#        if(user_filename in self.megahal):
#            if('brain' in self.megahal[user_filename]):
#                self.megahal[user_filename]['brain'].learn(args)
#                self.megahal[user_filename]['last_used'] = int(time.time())
#        else:
#            self.megahal[user_filename] = {}
#            self.megahal[user_filename]['last_used'] = int(time.time())
#            self.megahal[user_filename]['brain'] = megahal.MegaHAL(4,user_filename)
#            self.megahal[user_filename]['brain'].learn(args)
#            self.megahal[user_filename]['last_used'] = int(time.time())



