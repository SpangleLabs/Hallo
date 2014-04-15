import ircbot_chk
import time
import math
import threading

class hallobase_view:

    def fn_channels(self,args,client,destination):
        'Hallo will tell you which channels he is in, ops only. Format: "channels" for channels on current server, "channels all" for all channels on all servers.'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            if(args.lower()=='all'):
                return "On all servers, I am on these channels: " + ', '.join(server + "-" + channel for server in self.conf['server'] for channel in self.conf['server'][server]['channel'] if self.conf['server'][server]['channel'][channel]['in_channel']) + "."
            else:
                return "On this server, I'm in these channels: " + ', '.join(channel for channel in self.conf['server'][destination[0]]['channel'] if self.conf['server'][destination[0]]['channel'][channel]['in_channel']) + "."
        else:
            return "Sorry, this function is for gods only."

    def fn_active_threads(self,args,client,destination):
        'Returns current number of active threads.. should probably be gods only, but it is not. Format: active_thread'
        return "I think I have " + str(threading.active_count()) + " active threads right now."

    def fn_uptime(self,args,client,destination):
        'Returns hardware uptime. Format: uptime'
        uptime = time.time()-psutil.get_boot_time()
        days = math.floor(uptime/86400)
        hours = math.floor((uptime-86400*days)/3600)
        minutes = math.floor((uptime-86400*days-3600*hours)/60)
        seconds = uptime-86400*days-3600*hours-minutes*60
        return "My current (hardware) uptime is " + str(days) + " days, " + str(hours) + " hours, " + str(minutes) + " minutes and " + str(seconds) + " seconds."

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

