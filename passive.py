import random
#import base64
import urllib.request, urllib.error, urllib.parse
import time
#import re
import math
##from PIL import Image
import io
#import pickle
import euler
import hallobase
#import threading
import json
#import difflib
import re
import html.parser
from subprocess import call


import ircbot_chk   #for swear detect function
import hallobase    #for _S replies
import hallobase_silly  #for foof
import megahal_mod  #for recording messages into brains.
import games        #for higher or lower


endl = '\r\n'
class passive():
    def init(self):
        self.longcat = False

    def fnn_passive(self,args,client,destination):
        # SPANGLE ADDED THIS, should run his extrayammering command, a command to say things (only) when not spoken to... oh god.
        passive.fnn_sweardetect(self,args,client,destination)
        megahal_mod.megahal_mod.fnn_megahalrecord(self,args,client,destination)
        if(len(args)>2 and args[:2].lower()=='_s' and '_s' not in [user.lower() for user in self.core['server'][destination[0]]['channel'][destination[1]]['user_list']]):
            return megahal_mod.megahal_mod.fn_speak(self,args[2:],client,destination)
        if(args.lower()=='higher' or args.lower()=='lower'):
            try:
                self.games
            except NameError:
                self.games = {}
            if('server' in self.games and destination[0] in self.games['server'] and 'player' in self.games['server'][destination[0]] and client in self.games['server'][destination[0]]['player'] and 'higher_or_lower' in self.games['server'][destination[0]]['player'][client]):
                if(args.lower()=='higher'):
                    return games.games.fn_higher_or_lower(self,'higher',client,destination)
                if(args.lower()=='lower'):
                    return games.games.fn_higher_or_lower(self,'lower',client,destination)
        if(args.lower()=='hit' or args.lower()=='stick' or args.lower()=='stand'):
            try:
               self.games
            except NameError:
               self.games = {}
            if('server' in self.games and destination[0] in self.games['server'] and 'player' in self.games['server'][destination[0]] and client in self.games['server'][destination[0]]['player'] and 'blackjack' in self.games['server'][destination[0]]['player'][client]):
                return games.games.fn_blackjack(self,args,client,destination)
        if(not self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc']):
            return None
        out = passive.fnn_extrayammering(self,args,client,destination)
        if(out is not None):
            return out
       # if(message.lower().replace(' ','') == "foof"):
        if re.search(r'foo[o]*f[!]*',args,re.I):
            out = hallobase_silly.hallobase_silly.fn_foof(self,args,client,destination)
            return out
        if(re.search(r'(pew)+',args,re.I)):
            out = passive.fnn_pew(self,args,client,destination)
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
            if('127.0.0.1' in url or '192.168.' in url or '10.' in url or '172.' in url):
                return None
            if("://" not in url):
                url = "http://" + url
            pagerequest = urllib.request.Request(url)
            pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
            pageopener = urllib.request.build_opener()
            pageinfo = str(pageopener.open(pagerequest).info())
            if("Content-Type:" in pageinfo):
                pagetype = pageinfo.split()[pageinfo.split().index('Content-Type:')+1]
            if('speedtest.net' in url):
                if(url[-4:]=='.png'):
                    number = url[32:-4]
                    newurl = 'http://www.speedtest.net/my-result/' + number
                    print("New url: " + newurl)
                    pagerequest = urllib.request.Request(newurl)
                    pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
                    pageopener = urllib.request.build_opener()
                    pageinfo = str(pageopener.open(pagerequest).info())
                code = pageopener.open(pagerequest).read().decode('utf-8')
                code = re.sub(r'\s+','',code)
                code = ''.join(code.split())
                download = re.search('<h3>Download</h3><p>([0-9\.]*)',code).group(1)
                upload = re.search('<h3>Upload</h3><p>([0-9\.]*)',code).group(1)
                ping = re.search('<h3>Ping</h3><p>([0-9]*)',code).group(1)
                return "Speedtest> Download: " + download + "Mb/s | Upload: " + upload + "Mb/s | Ping: " + ping + "ms"
            elif('imgur.com' in url):
                if('/a/' in url):
                    code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                    title = re.search('<meta name="twitter:title" value="([^"]*)"/>',code).group(1)[:0-len(' - Imgur')]
                    if(title=='imgur: the simple imag'):
                        title = 'none.'
                    pic_number = '0'
                    if('#' in url):
                        pic_number = url.split('#')[-1]
                    album_count = re.search('<h2 id="thumbs-header">Album: ([0-9,]*) images',code).group(1)
                    views = re.search('<span class="stat">([0-9,]*)</span> views',code).group(1)
                    current_img_link = re.search('data-src="//i.imgur.com/([0-9A-Za-z]*).(jpg|gif|png)" data-index="' + pic_number + '"',code).group(1)
                    current_img_ext = re.search('data-src="//i.imgur.com/([0-9A-Za-z]*).(jpg|gif|png)" data-index="' + pic_number + '"',code).group(2)
                    imgpage_pagerequest = urllib.request.Request('http://imgur.com/' + current_img_link)
                    imgpage_pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
                    imgpage_pageopener = urllib.request.build_opener()
                    imgpage_code = imgpage_pageopener.open(imgpage_pagerequest).read().decode('utf-8','ignore')
                    img_width = re.search('<meta name="twitter:image:width" value="([0-9]*)"/>',imgpage_code).group(1)
                    img_height = re.search('<meta name="twitter:image:height" value="([0-9]*)"/>',imgpage_code).group(1)
                    img_pagerequest = urllib.request.Request('http://i.imgur.com/' + current_img_link + '.' + current_img_ext)
                    img_pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
                    img_pageopener = urllib.request.build_opener()
                    img_code = img_pageopener.open(img_pagerequest).read()
                    img_size = len(img_code)
                    if(img_size<2048):
                        img_sizestr = str(img_size) + "Bytes"
                    elif(img_size<(2048*1024)):
                        img_sizestr = str(math.floor(float(img_size)/10.24)/100) + "KiB"
                    else:
                        img_sizestr = str(math.floor(float(img_size)/(1024*10.24))/100) + "MiB"
                    return "Imgur album> Album title: " + title + " | Gallery views: " + views + " | Image " + pic_number + " of " + album_count + " | Current image: " + img_width + "x" + img_height + ", " + img_sizestr + "."
                else:
                    if(url[-4:] in ['.png','.jpg','.gif']):
                        code = url.split('/')[-1].split('.')[0]
                        newurl = 'http://www.imgur.com/' + code
                        print("New url: " + newurl)
                        pagerequest = urllib.request.Request(newurl)
                        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
                        pageopener = urllib.request.build_opener()
                    code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                    title = re.search('<meta name="twitter:title" value="([^"]*)"/>',code).group(1)[:0-len(' - Imgur')]
                    if(title=='imgur: the simple imag'):
                        title = 'none.'
                    img_width = re.search('<meta name="twitter:image:width" value="([0-9]*)"/>',code).group(1)
                    img_height = re.search('<meta name="twitter:image:height" value="([0-9]*)"/>',code).group(1)
                    img_link = re.search('<link rel="image_src" href="([^"]*)"/>',code).group(1)
                    img_pagerequest = urllib.request.Request(img_link)
                    img_pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
                    img_pageopener = urllib.request.build_opener()
                    img_code = img_pageopener.open(img_pagerequest).read()
                    img_size = len(img_code)
                    if(img_size<2048):
                        img_sizestr = str(img_size) + "Bytes"
                    elif(img_size<(2048*1024)):
                        img_sizestr = str(math.floor(float(img_size)/10.24)/100) + "KiB"
                    else:
                        img_sizestr = str(math.floor(float(img_size)/(1024*10.24))/100) + "MiB"
                    if('<span id="views">' in code):
                        views = re.search('<span id="views">([0-9,]*)</span>',code).group(1)
                    else:
                        views = re.search('"views":([0-9]*),',code).group(1)
                    return "Imgur> Title: " + title + " | Size: " + img_width + "x" + img_height + " | Filesize: " + img_sizestr + " | Views: " + views + "."
            elif("image" in pagetype):
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
                return "Image: " + pagetype + " (" + str(image_width) + "px by " + str(image_height) + "px) " + filesizestr + "."
            elif('youtube.com' in url or 'youtu.be' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                length = re.search('length_seconds": ([0-9]*)', code).group(1)
                length_str = str(int(int(length)/60)) + "m " + str(int(length)-(60*(int(int(length)/60)))) + "s"
                views = re.search('<span class="watch-view-count[^>]*>[\n\r\s]*([0-9,+]*)',code).group(1)
                #title = ' '.join(re.search('<title[-A-Z0-9"=' + "'" + ' ]*>\b*([^<]*)\b*</title>',code).group(1)[:-10].split()).replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'").replace('&#039;',"'").replace('&quot;','"').replace('&amp;','&')
                title = ' '.join(re.search('<title[-A-Z0-9"=' + "'" + ' ]*>\b*([^<]*)\b*</title>',code).group(1)[:-10].split())
                h = html.parser.HTMLParser()
                title = h.unescape(title)
                return "Youtube video> Title: " + title + " | Length: " + length_str + " | Views: " + views + "."
            elif('amazon.co.uk' in url or 'amazon.com' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                title = re.search('<title>([^<]*)</title>',code).group(1)
                price = re.search('<b class="priceLarge">([^<]*)</b>',code).group(1)
                if(code.count('There are no customer reviews yet.')!=0):
                    reviewstr = "No reviews yet."
                else:
                    stars = re.search('<span>([0-9.]*) out of 5 stars',code).group(1)
                    reviews = re.search('>([0-9]*) customer reviews',code).group(1)
                    reviewstr = stars + "/5 stars, from " + reviews + " reviews"
                return "Amazon> Title: " + title + " | Price: " + price + " | " + reviewstr + "."
            elif('ebay.co.uk' in url or 'ebay.com' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                title = re.search('<meta property="og:title" content="([^"]*)">',code).group(1)
                price = re.search('itemprop="price"([^>]*)>([^<]*)</span>',code).group(2)
                if(code.count('Current bid:')==1):
                    type = 'Buy it now.'
                    time_left = re.search('id="vi-cdown_timeLeft">([^<]*)<',code).group(1)
                else:
                    type = 'Auction'
                    bids = re.search('<span id="qty-test">([0-9]*)</span> <span>bids',code).group(1)
                    if(bids==1):
                        type = type + ", " + bids + "bid."
                    else:
                        type = type + ", " + bids + "bids."
                    time_left = re.search('id="vi-cdown_timeLeft">([^<]*)<',code).group(1)
                #time left
                return "eBay> Title: " + title + " | " + type + " | Time left: " + time_left + "."
            elif('imdb.com/title' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8')
                movie_code = re.search('title/(tt[0-9]*)',code).group(1)
                api_url = 'http://www.omdbapi.com/?i=' + movie_code
                api_pagerequest = urllib.request.Request(api_url)
                api_pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
                api_pageopener = urllib.request.build_opener()
                api_code = api_pageopener.open(api_pagerequest).read()
                api_dict = json.loads(api_code.decode('utf-8'))
                title = api_dict['Title']
                year = api_dict['Year']
                genre = api_dict['Genre']
                rating = api_dict['imdbRating']
                votes = api_dict['imdbVotes']
                return "IMDB> Title: " + title + " (" + year + ") | Rated " + rating + "/10, " + votes + " votes. | Genres: " + genre  + "."
            else:
                code = pageopener.open(pagerequest).read(4096).decode('utf-8','ignore')
                if(code.count('</title>')>=1):
                    title = re.search('<title([-A-Z0-9"=' + "'" + ' ]*)>([^<]*)</title>',code).group(2)
                    h = html.parser.HTMLParser()
                    title = h.unescape(title)
                    if(title!=""):
                        return "URL title: " + title.replace("\n","")
                else:
                    self.base_say('I saw a link, but no title? ' + url,[destination[0],'dr-spangle'])

    def fnn_sweardetect(self,args,client,destination):
        swearcheck = ircbot_chk.ircbot_chk.chk_swear(self,destination[0],destination[1],args)
        swearstatus = swearcheck[0]
        swearword = swearcheck[1]
        if(swearstatus=='comment'):
            if(self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['commentmsg']==''):
                self.base_say("Please don't swear in the channel. This is a PG channel.",destination)
            else:
                self.base_say(self.conf['server'][destination[0]]['channel'][destination[1]]['swearlist']['commentmsg'].replace('{swear}',re.search(swearword,args,re.I).group(0)),destination)
        elif(swearstatus=='inform'):
            for admin in ircbot_chk.ircbot_chk.chk_recipientonline(destination[0],self.conf['server'][destination[0]]['admininform']):
                self.base_say(client + ' just swore in ' + destination[1] + '. the message was: ' + args,[destination[0],admin])
        elif(swearstatus=='possible'):
            for admin in ircbot_chk.ircbot_chk.chk_recipientonline(destination[0],self.conf['server'][destination[0]]['admininform']):
                self.base_say(client + ' possibly just swore in ' + destination[1] + '. Check the context. The message was: ' + args,[destination[0],admin])

    def fnn_extrayammering(self, args, client, destination):
        'Does some extra chatting, probably super buggy.'
        if((args.lower().find("who") >= 0) and (args.lower().find("best pony") >=0 or args.lower().find("bestpony".lower()) >=0)):
            message = client + ': ' + hallobase_silly.hallobase_silly.fn_bestpony(self,args,client,destination)
            return str(message)
        elif(args.lower().find("open") >= 0 and (args.lower().find("pod bay") >=0 or args.lower().find("podbay") >=0) and args.lower().find("door") >= 0):
            message = "I'm sorry " + client + ", but I'm afraid I can't do that."
            return message
        elif(("irc client" in args.lower() or "irc program" in args.lower() or "chat client" in args.lower()) and ("which" in args.lower() or "what" in args.lower()) and ("get" in args.lower() or "use" in args.lower())):
            message = "For windows: Hexchat is a good irc client. Try http://hexchat.org For mac: Colloquy is a good choice http://colloquy.info/ For linux: xchat (for a graphical interface) http://xchat.org or for command line linux: irssi http://irssi.org Or for a web client, try http://mibbit.com"
            return message
     #   elif("when" in args.lower() and ("more pony" in args.lower() or "season 4" in args.lower() or "S04" in args.upper() or ("next season" in args.lower() and ("pony" in args.lower() or "mlp" in args.lower())))):
     #       message = "It's finally been announced! Season 4 of pony starts on the 23rd of November!"
     #       return message
        elif(("who is" in args.lower() or "what is" in args.lower()) and "hallo" in args.lower()):
            message = "I'm Hallo, I'm a bot built by dr-spangle, I do a couple of useful things like calculate things and choose options."
            return message
        elif(("who is" in args.lower() or "what is" in args.lower()) and "muffinmare" in args.lower()):
            message = "muffinmare is another bot, she was built by ripp_, and very kindly gives out free muffins to people."
            return message
        else:
            pass

    def fnn_beep(self,args,client,destination):
        #call(["beep"])
        return "boop"

    def fnn_pew(self,args,client,destination):
        return "pew pew."
