import re
from xml.dom import minidom
import urllib.request
import codecs
import pickle

def downloadPage(url):
    #time.sleep(3)
    pagerequest = urllib.request.Request(url)
    pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
    pageopener = urllib.request.build_opener()
    code = pageopener.open(pagerequest).read().decode('utf-8')
    return code


###Create original XML from pickle list
tagRegex = re.compile('<[^>]*>')
animeDexRegex = re.compile('<h3><span[^>]*>[^<]*dex entries</span></h3>(.*?)<h3>',re.DOTALL|re.IGNORECASE)
animeDexEntryRegex = re.compile('<td> *<a[^>]*>([A-Z]+[0-9]+)</a>[^<]*</td>[^<]*<td> *<strong class="selflink">[^<]*</strong>[^<]*</td>[^<]*<td>[^<]*</td>[^<]*<td>(.*?)</td>',re.DOTALL|re.IGNORECASE)
gamesList = ['Red','Blue','Yellow','Gold','Silver','Crystal','Ruby','Sapphire','Emerald','Fire Red','Leaf Green','Diamond','Pearl','Platinum','Heart Gold','Soul Silver','Black','White','Black 2','White 2','X','Y','Omega Ruby','Alpha Sapphire']
p = pickle.load(open("pokemon.p","rb"))
b = pickle.load(open("pokelinklist.p","rb"))
doc = minidom.Document()
root = doc.createElement("pokemon_list")
doc.appendChild(root)
for x in p:
    print("Starting: "+p[x]['Name'])
    pokemonXml = doc.createElement("pokemon")
    nameXml = doc.createElement("name")
    nameXml.appendChild(doc.createTextNode(p[x]['Name']))
    pokemonXml.appendChild(nameXml)
    dexNumberXml = doc.createElement("dex_number")
    dexNumberXml.appendChild(doc.createTextNode(p[x]['Dex_National']))
    pokemonXml.appendChild(dexNumberXml)
    bulbaLink = "http://bulbapedia.bulbagarden.net"+b[x]
    bulbaLinkXml = doc.createElement("link_bulbapedia")
    bulbaLinkXml.appendChild(doc.createTextNode(bulbaLink))
    pokemonXml.appendChild(bulbaLinkXml)
    bulbaEditLink = bulbaLink.replace("/wiki/","/w/index.php?title=")+"&action=edit"
    bulbaEditLinkXml = doc.createElement("link_bulbapedia_edit")
    bulbaEditLinkXml.appendChild(doc.createTextNode(bulbaEditLink))
    pokemonXml.appendChild(bulbaEditLinkXml)
    pokemonDbXml = doc.createElement("link_pokemondb")
    pokemonDbXml.appendChild(doc.createTextNode("http://pokemondb.net/pokedex/"+str(x)))
    pokemonXml.appendChild(pokemonDbXml)
    serebiiLinkXml = doc.createElement("link_serebii")
    serebiiLinkXml.appendChild(doc.createTextNode("http://www.serebii.net/pokedex-xy/"+format(x,'03')+".shtml"))
    pokemonXml.appendChild(serebiiLinkXml)
    psypokeLinkXml = doc.createElement("link_psypokes")
    psypokeLinkXml.appendChild(doc.createTextNode("http://www.psypokes.com/dex/psydex/"+format(x,'03')+"/general"))
    pokemonXml.appendChild(psypokeLinkXml)
    if(p[x]['Evolve_From']!="0"):
        evolveFromXml = doc.createElement("evolve_from")
        evolveFromXml.appendChild(doc.createTextNode(p[x]['Evolve_From']))
        pokemonXml.appendChild(evolveFromXml)
    for evolveTo in p[x]['Evolve_To']:
        evolveToXml = doc.createElement("evolve_to")
        evolveToXml.appendChild(doc.createTextNode(evolveTo))
        pokemonXml.appendChild(evolveToXml)
    ##START WORK ON POKEDEX ENTRIES
    dexEntryListXml = doc.createElement("dex_entry_list")
    code = downloadPage(bulbaLink)
    animeDexSearch = re.search(animeDexRegex,code)
    if(animeDexSearch is None):
        print("no anime dex section")
        continue
    animeDexCode = animeDexSearch.group(1)
    for animeDexEntrySearch in re.finditer(animeDexEntryRegex,animeDexCode):
        animeDexEntryEpisode = animeDexEntrySearch.group(1)
        print(animeDexEntryEpisode)
        animeDexEntryEntry = animeDexEntrySearch.group(2)
        animeDexEntryEntryy = tagRegex.sub('',animeDexEntryEntry).strip()
        dexEntryXml = doc.createElement("dex_entry")
        typeXml = doc.createElement("type")
        typeXml.appendChild(doc.createTextNode("anime"))
        dexEntryXml.appendChild(typeXml)
        episodeXml = doc.createElement("episode")
        episodeXml.appendChild(doc.createTextNode(animeDexEntryEpisode))
        dexEntryXml.appendChild(episodeXml)
        entryXml = doc.createElement("entry")
        entryXml.appendChild(doc.createTextNode(animeDexEntryEntryy))
        dexEntryXml.appendChild(entryXml)
        dexEntryListXml.appendChild(dexEntryXml)
    #GAME POKEDEX ENTRIES
    for game in gamesList:
        gameName = game.replace(' ','_')
        if(gameName in p[x]['Dex_entries']['Games']):
            print(game,end=" ")
            dexEntryXml = doc.createElement("dex_entry")
            typeXml = doc.createElement("type")
            typeXml.appendChild(doc.createTextNode("game"))
            dexEntryXml.appendChild(typeXml)
            episodeXml = doc.createElement("game")
            episodeXml.appendChild(doc.createTextNode(game))
            dexEntryXml.appendChild(episodeXml)
            entryXml = doc.createElement("entry")
            entryXml.appendChild(doc.createTextNode(p[x]['Dex_entries']['Games'][gameName]))
            dexEntryXml.appendChild(entryXml)
            dexEntryListXml.appendChild(dexEntryXml)
    pokemonXml.appendChild(dexEntryListXml)
    print()
    root.appendChild(pokemonXml)
                
with codecs.open("pokemon.xml", "w", "utf-8") as out:
    doc.writexml(out)

#doc.writexml(open("C:/users/joshua/git/hallo/store/pokemon-3.xml","w"))
