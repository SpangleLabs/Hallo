import ircbot_chk
import time
#import psutil   used in fn_uptime
import pprint
import random
import hashlib
import os

class hallobase_view:

#####DISABLED UNTIL PSUTIL CAN BE NOT USED
#    def fn_uptime(self,args,client,destination):
#        'Returns hardware uptime. Format: uptime'
#        uptime = time.time()-psutil.get_boot_time()
#        days = math.floor(uptime/86400)
#        hours = math.floor((uptime-86400*days)/3600)
#        minutes = math.floor((uptime-86400*days-3600*hours)/60)
#        seconds = uptime-86400*days-3600*hours-minutes*60
#        return "My current (hardware) uptime is " + str(days) + " days, " + str(hours) + " hours, " + str(minutes) + " minutes and " + str(seconds) + " seconds."

    def fn_megahal_view(self,args,client,destination):
        'View the megahal variable, privmsg only. gods only.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(destination[1][0] == '#'):
                return "I'm not posting my whole megahal variable here, that would be rude."
            else:
                prettymegahal = pprint.pformat(self.megahal)
                filename = "megahal_" + hashlib.md5(str(random.randint(1,1000)*time.time()).encode("utf-8")).hexdigest() + ".txt"
                link = "http://hallo.dr-spangle.com/" + filename
                file = open("../http/" + filename,'w')
                file.write(prettymegahal)
                file.close()
                self.base_say("Megahal variable written to " + link + " it will be deleted in 30 seconds. Act fast.",destination)
                time.sleep(30)
                os.remove("../http/" + filename)
                return "File removed."
        else:
            return "Insufficient privileges to view megahal variable."

