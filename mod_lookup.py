import urllib.request #, urllib.error, urllib.parse    #for urbandictionary function
import urllib.parse
import json         #for urbandictionary function
import xmltodict    #for ponyvillefm functionality
import pickle
import random
import difflib
import re      #for turning wikicode to plaintext

import ircbot_chk

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

    def fn_song(self,args,client,destination):
        'States the current song on ponyvillefm'
        url = 'http://ponyvillefm.com/inc/merge.php'
        songdict = mod_lookup.fnn_loadxml(self,url)
        return "Current song on ponyvillefm: " + songdict['SHOUTCASTSERVER']['SONGTITLE']

    def fn_nextsong(self,args,client,destination):
        'States the next song on ponyvillefm'
        url = 'http://ponyvillefm.com/inc/merge.php'
        songdict = mod_lookup.fnn_loadxml(self,url)
        if(songdict['SHOUTCASTSERVER']['NEXTTITLE'] is None):
            return "Next song data currently unavailable for ponyvillefm."
        return "Next song on ponyvillefm: " + songdict['SHOUTCASTSERVER']['NEXTTITLE']

    def fn_listeners(self,args,client,destination):
        'States the current number of listeners to ponyvillefm'
        url = 'http://ponyvillefm.com/inc/merge.php'
        songdict = mod_lookup.fnn_loadxml(self,url)
        return "Current number of listeners to ponyvillefm: " + songdict['SHOUTCASTSERVER']['CURRENTLISTENERS']

    def fn_random_cocktail(self,args,client,destination):
        'Delivers ingredients and recipes for a random cocktail. Format: random_cocktail'
        cocktails = pickle.load(open('store/cocktails.p','rb'))
        number = random.randint(0,len(cocktails))
        cocktail = cocktails[number]
        output = "Randomly selected cocktail is: " + cocktail['name'] + " (#" + str(number) + "). The ingredients are: "
        ingredients = []
        for ingredient in cocktail['ingredients']:
            ingredients.append(ingredient[0] + ingredient[1])
        output = output + ", ".join(ingredients) + ". The recipe is: " + cocktail['instructions']
        if(output[-1]!='.'):
            output = output + "."
        return output

    def fn_cocktail(self,args,client,destination):
        'Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>'
        cocktails = pickle.load(open('store/cocktails.p','rb'))
        cocktailnames = []
        for cocktail in cocktails:
            cocktailnames.append(cocktail['name'].lower())
        closest = difflib.get_close_matches(args.lower(),cocktailnames)
        if(len(closest)==0 or closest[0]==''):
            return "I haven't got anything close to that name."
        else:
            for cocktail in cocktails:
                if(cocktail['name'].lower()==closest[0].lower()):
                    break
            ingredients = []
            for ingredient in cocktail['ingredients']:
                ingredients.append(ingredient[0] + ingredient[1])
            if(cocktail['instructions'][-1]!='.'):
                cocktail['instructions'] = cocktail['instructions'] + "."
            return "Closest I have is " + closest[0] + ". The ingredients are: " + ", ".join(ingredients) + ". The recipe is: " + cocktail['instructions']

    def fn_in_space(self,args,client,destination):
        'Returns the number of people in space right now, and their names. Format: in_space'
        space = mod_lookup.fnn_loadjson(self,'http://www.howmanypeopleareinspacerightnow.com/space.json')
        return "There are " + str(space['number']) + " people in space right now. Their names are: " + ', '.join(x['name'] for x in space['people']) + "."

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
        
        