#from euler import eulerclass
#import euler
#from ircbot import ircbot
#import shelve
import random
#import bsddb3 as bsddb
import base64
import urllib.request, urllib.error, urllib.parse
import time
import re
import math
##from PIL import Image
import io
import pickle
import euler
import threading
import json
import difflib
##import psutil

import ircbot_chk


endl = '\r\n'
class hallobase():

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





