import urllib.request #, urllib.error, urllib.parse    #for urbandictionary function
import urllib.parse
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

    def fn_wiki(self,args,client,destination):
        'Reads the first paragraph from a wikipedia article'
        url = 'http://en.wikipedia.org/w/api.php?format=json&action=query&titles='+args.strip().replace(' ','_')+'&prop=revisions&rvprop=content&redirects=True'
        article = mod_lookup.fnn_loadjson(self,url)
        articletext = article['query']['pages'][list(article['query']['pages'])[0]]['revisions'][0]['*']
        oldscan = articletext
        newscan = re.sub('{{[^{^}]*}}','',oldscan)
        while(newscan!=oldscan):
            oldscan = newscan
            newscan = re.sub('{{[^{^}]*}}','',oldscan)
        plaintext = re.sub(r'<!--[^>]*-->','',re.sub(r'\[\[([^]]*)]]',r'\1',re.sub(r'\[\[[^]^|]*\|([^]]*)]]',r'\1',re.sub(r'<ref[^<]*</ref>','',newscan.replace('\'\'','')))))
        plaintext = re.sub(r'<ref[^>]*/>','',plaintext)
        firstparagraph = plaintext.lstrip().split('\n')[0]
        return firstparagraph

    def fn_translate(self,args,client,destination):
        'Translates a given block of text. Format: translate <from>-><to> <text>'
        if(len(args.split())<2):
            lang_change = ''
            trans_str = args
        else:
            lang_change = args.split()[0]
            trans_str = ' '.join(args.split()[1:])
        if('->' not in lang_change):
            lang_from = "auto"
            lang_to = "en"
            trans_str = lang_change+' '+trans_str
        else:
            lang_from = lang_change.split('->')[0]
            lang_to = lang_change.split('->')[1]
        trans_safe = urllib.parse.quote(trans_str.strip(),'')
        url = "http://translate.google.com/translate_a/t?client=t&text="+trans_safe+"&hl=en&sl="+lang_from+"&tl="+lang_to+"&ie=UTF-8&oe=UTF-8&multires=1&otf=1&pc=1&trs=1&ssel=3&tsel=6&sc=1"
        transdict = mod_lookup.fnn_loadjson(self,url,[],True)
        return "Translation: "+transdict[0][0][0]
        
    def fn_random_porn(self,args,client,destination):
        'Returns a random e621 result using the search you specify. Format: msg <tags>'
        args = args.replace(' ','%20')
        url = 'https://e621.net/post/index.json?tags='+args+'%20order:random%20score:%3E0&limit=1'
        returnlist = mod_lookup.fnn_loadjson(self,url)
        if(len(returnlist)==0):
            return "No results."
        else:
            result = returnlist[0]
            link = "http://e621.net/post/show/"+str(result['id'])
            if(result['rating']=='e'):
                rating = "(Explicit)"
            elif(result['rating']=="q"):
                rating = "(Questionable)"
            elif(result['rating']=="s"):
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            return "e621 search for \""+args+"\" returned: "+link+" "+rating
        
    def fn_butts(self,args,client,destination):
        'Returns a random image from e621 for the search "butt". Format: butts'
        return mod_lookup.fn_random_porn(self,"butt",client,destination)
        
        