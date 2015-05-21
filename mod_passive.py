import urllib.request #, urllib.error, urllib.parse
import math
##from PIL import Image
##import io
import re
import html.parser


import ircbot_chk   #for swear detect function
import mod_lookup
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
            else:
                pagetype = ''
            if('speedtest.net' in url):
                return
            elif('imgur.com' in url):
                return
            elif("image" in pagetype):
                return
            elif('youtube.com' in url or 'youtu.be' in url):
                return
            elif('amazon.co.uk' in url or 'amazon.com' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                title = re.search('<title>([^<]*)</title>',code,re.I).group(1)
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
                    page_type = 'Buy it now.'
                    time_left = re.search('id="vi-cdown_timeLeft">([^<]*)<',code).group(1)
                else:
                    page_type = 'Auction'
                    bids = re.search('<span id="qty-test">([0-9]*)</span> <span>bids',code).group(1)
                    if(bids==1):
                        page_type = page_type + ", " + bids + "bid."
                    else:
                        page_type = page_type + ", " + bids + "bids."
                    time_left = re.search('id="vi-cdown_timeLeft">([^<]*)<',code).group(1)
                #time left
                return "eBay> Title: " + title + " | " + page_type + " | Time left: " + time_left + "."
            elif('imdb.com/title' in url):
                return
            else:
                return

    def fnn_sizestr(self,size):
        if(size<2048):
            sizestr = str(size) + "Bytes"
        elif(size<(2048*1024)):
            sizestr = str(math.floor(float(size)/10.24)/100) + "KiB"
        elif(size<(2048*1024*1024)):
            sizestr = str(math.floor(float(size)/(1024*10.24))/100) + "MiB"
        else:
            sizestr = str(math.floor(float(size)/(1024*1024*10.24))/100) + "GiB"
        return sizestr

