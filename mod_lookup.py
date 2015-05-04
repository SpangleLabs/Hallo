import urllib.request #, urllib.error, urllib.parse    #for urbandictionary function
import json         #for urbandictionary function
import xmltodict    #for ponyvillefm functionality
import random
import re      #for turning wikicode to plaintext

class mod_lookup:

    def fnn_loadjson(self,url,headers=[],jsonfix=False):
        'Takes a url to a json resource, pulls it and returns a dictionary.'
        pagerequest = urllib.request.Request(url)
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        for header in headers:
            pagerequest.add_header(header[0],header[1])
        pageopener = urllib.request.build_opener()
#        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read().decode('utf-8')
        if(jsonfix):
            code = re.sub(',+',',',code)
            code = code.replace('[,','[').replace(',]',']')
        returndict = json.loads(code)
        return returndict

    def fnn_loadxml(self,url,headers=[]):
        'Takes a url to an xml resource, pulls it and returns a dictionary.'
        pagerequest = urllib.request.Request(url)
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        for header in headers:
            pagerequest.add_header(header[0],header[1])
        pageopener = urllib.request.build_opener()
#        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read().decode('utf-8')
        returndict = xmltodict.parse(code)
        return returndict

    def fnn_weather(self,args,client,destination):
        'Random weather'
        weather = ['Rain.'] * 10 + ['Heavy rain.'] * 3 + ['Cloudy.'] * 20 + ['Windy.'] * 5 + ['Sunny.']
        return weather[random.randint(0,len(weather)-1)]
        