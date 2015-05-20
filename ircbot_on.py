
endl = '\r\n'

class ircbot_on:

    def on_mode(self,server,client,channel,mode,args):
        #pass # override this method to handle MODE changes
        if(mode=='-k'):
            self.conf['server'][server]['channel'][channel]['pass'] = ''
        elif(mode=='+k'):
            self.conf['server'][server]['channel'][channel]['pass'] = args


