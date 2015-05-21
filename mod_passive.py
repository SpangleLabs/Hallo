


import ircbot_chk   #for swear detect function
#import megahal_mod  #for recording messages into brains.
import mod_calc      #for auto calculation when calculations posted in channel.


endl = '\r\n'
class mod_passive():
    def fnn_passive(self,args,client,destination):
        # SPANGLE ADDED THIS, should run his extrayammering command, a command to say things (only) when not spoken to... oh god.
#        megahal_mod.megahal_mod.fnn_megahalrecord(self,args,client,destination)
#        if(len(args)>2 and args[:2].lower()=='_s' and '_s' not in [user.lower() for user in self.core['server'][destination[0]]['channel'][destination[1]]['user_list']]):
#            return megahal_mod.megahal_mod.fn_speak(self,args[2:],client,destination)
        ##check if passive functions are disabled.
        if(not self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc']):
            return None
        out = mod_passive.fnn_urldetect(self,args,client,destination)
        if(out is not None):
            return out
        if(ircbot_chk.ircbot_chk.chk_msg_calc(self,args) and not ircbot_chk.ircbot_chk.chk_msg_numbers(self,args)):
            return mod_calc.mod_calc.fn_calc(self,args,client,destination)
