import random
#import base64
import urllib.request, urllib.error, urllib.parse
#import time
#import re
import math
from PIL import Image
import io
#import pickle
import euler
import hallobase
#import threading
#import json
#import difflib
import re



endl = '\r\n'
class passive():
    def init(self):
        self.longcat = False

    def fnn_passive(self,args,client,destination):
        # SPANGLE ADDED THIS, should run his extrayammering command, a command to say things (only) when not spoken to... oh god.
        out = passive.fnn_extrayammering(self,args,client,destination)
        if(out is not None):
            return out
       # if(message.lower().replace(' ','') == "foof"):
        if re.search(r'foo[o]*f',args,re.I):
            out = hallobase.hallobase.fn_foof(self,args,client,destination)
            return out
        out = passive.fnn_urldetect(self,args,client,destination)
        if(out is not None):
            return out
        if(args.lower()=='beep'):
            return passive.fnn_beep(self,args,client,destination)

    def fnn_urldetect(self, args, client, destination):
        'Detects URLs posted in channel, then returns the page title.'
        regex = r'\b((https?://|www.)[-A-Z0-9+&?%@#/=~_|$:,.]*[A-Z0-9+\&@#/%=~_|$])'
        if re.search(regex, args, re.I):
            url = re.search(regex, args, re.I).group(1)
            if("://" not in url):
                url = "http://" + url
            pagerequest = urllib.request.Request(url)
            pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
            pageopener = urllib.request.build_opener()
            pageinfo = str(pageopener.open(pagerequest).info())
            if("Content-Type:" in pageinfo):
                pagetype = pageinfo.split()[pageinfo.split().index('Content-Type:')+1]
                if("image" in pagetype):
                    code = pageopener.open(pagerequest).read()
                    image_file = io.BytesIO(code)
                    im = Image.open(image_file)
                    image_width, image_height = im.size
                    filesize = len(code)
                    if(filesize<2048):
                        filesizestr = str(filesize) + "Bytes"
                    elif(filesize<(2048*1024)):
                        filesizestr = str(math.floor(float(filesize)/10.24)/100) + "KiB"
                    elif(filesize<(2048*1024*1024)):
                        filesizestr = str(math.floor(float(filesize)/(1024*10.24))/100) + "MiB"
                    else:
                        filesizestr = str(math.floor(float(filesize)/(1024*1024*10.24))/100) + "GiB"
                    return "Image: " + pagetype + " (" + str(image_width) + "px by " + str(image_height) + "px) " + filesizestr
            if('youtube.com' in url or 'youtu.be' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8')
                length = re.search('length_seconds": ([0-9]*)', code).group(1)
                length_str = str(int(length)/60) + "m " + str(int(length)-(60*(int(length)/60))) + "s"
                views = re.search('<span class="watch-view-count " >[\n\r\s]*([0-9,]*)',code).group(1)
                title = ' '.join(re.search('<title[-A-Z0-9"=' + "'" + ' ]*>\b*([^<]*)\b*</title>',code).group(1)[:-10].split()).replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'").replace('&#039;',"'").replace('&quot;','"').replace('&amp;','&')
                return "Youtube video> Title: " + title + " | Length: " + length_str + " | Views: " + views
            code = pageopener.open(pagerequest).read(4096).decode('utf-8')
            if(code.count('</title>')>=1):
                title = code.split('</title>')[0]
                title = ' '.join(re.compile('<title[-A-Z0-9"=' + "'" + ' ]*>',re.IGNORECASE).split(title)[1].split()).replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'").replace('&039;',"'").replace('&quot;','"').replace('&amp;','&')
                if(title!=""):
                    return "URL title: " + title
            else:
                ircbot.say(self,'I saw a link, but no title? ' + url,[destination[0],'dr-spangle'])

    def fnn_extrayammering(self, args, client, destination):
        'Does some extra chatting, probably super buggy.'
        if((args.lower().find("who") >= 0) and (args.lower().find("best pony") >=0 or args.lower().find("bestpony".lower()) >=0)):
            message = client + ': ' + hallobase.hallobase.fn_bestpony(self,args,client,destination)
            return str(message)
        elif(args.lower().find("open") >= 0 and (args.lower().find("pod bay") >=0 or args.lower().find("podbay") >=0) and args.lower().find("door") >= 0):
            message = "I'm sorry " + client + ", but I'm afraid I can't do that"
            return message
        elif(("irc client" in args.lower() or "irc program" in args.lower() or "chat client" in args.lower()) and ("which" in args.lower() or "what" in args.lower()) and ("get" in args.lower() or "use" in args.lower())):
            message = "For windows: Hexchat is a good irc client. Try http://hexchat.org For mac: Colloquy is a good choice http://colloquy.info/ For linux: xchat (for a graphical interface) http://xchat.orgor for command line linux: irssi http://irssi.org Or for a web client, try http://mibbit.com"
            return message
        elif("when" in args.lower() and ("more pony" in args.lower() or "season 4" in args.lower() or "S04" in args.upper() or ("next season" in args.lower() and ("pony" in args.lower() or "mlp" in args.lower())))):
            message = "It's finally been announced! Season 4 of pony starts on the 23rd of November!"
            return message
        elif(("who is" in args.lower() or "what is" in args.lower()) and "hallo" in args.lower()):
            message = "I'm Hallo, I'm a bot built by dr-spangle, I do a couple of useful things like calculate things and choose options."
            return message
        elif(("who is" in args.lower() or "what is" in args.lower()) and "muffinmare" in args.lower()):
            message = "muffinmare is another bot, she was built by ripp_, and very kindly gives out free muffins to people."
            return message
        else:
            pass

    def fnn_beep(self,args,client,destination):
        return "boop"
