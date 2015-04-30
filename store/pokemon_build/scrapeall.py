from xml.dom import minidom
import urllib.request
import os
import time
import codecs

doc = minidom.parse("pokemon.xml")

try:
    os.mkdir("cache")
    os.mkdir("cache/bulbapedia")
    os.mkdir("cache/bulbapedia_edit")
    os.mkdir("cache/pokemondb")
    os.mkdir("cache/serebii")
    os.mkdir("cache/psypokes")
except:
    pass

def downloadPage(url):
    #time.sleep(3)
    pagerequest = urllib.request.Request(url)
    pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
    pageopener = urllib.request.build_opener()
    code = pageopener.open(pagerequest).read()
    return code

for pokemonXml in doc.getElementsByTagName("pokemon"):
    print("downloading "+pokemonXml.getElementsByTagName("name")[0].firstChild.data)
    dexNum = int(pokemonXml.getElementsByTagName("dex_number")[0].firstChild.data)
    #Get bulbapedia code
    bulbaLink = pokemonXml.getElementsByTagName("link_bulbapedia")[0].firstChild.data
    bulbaCode = downloadPage(bulbaLink)
    open("cache/bulbapedia/"+format(dexNum,'03')+".html","wb").write(bulbaCode)
    #Get bulbapedia edit page code
    bulbaEditLink = pokemonXml.getElementsByTagName("link_bulbapedia_edit")[0].firstChild.data
    bulbaEditCode = downloadPage(bulbaEditLink)
    open("cache/bulbapedia_edit/"+format(dexNum,'03')+".html","wb").write(bulbaEditCode)
    #Get pokemon DB page code
    pokemonDbLink = pokemonXml.getElementsByTagName("link_pokemondb")[0].firstChild.data
    pokemonDbCode = downloadPage(pokemonDbLink)
    open("cache/pokemondb/"+format(dexNum,'03')+".html","wb").write(pokemonDbCode)
    #Get serebii page code
    serebiiLink = pokemonXml.getElementsByTagName("link_serebii")[0].firstChild.data
    serebiiCode = downloadPage(serebiiLink)
    open("cache/serebii/"+format(dexNum,'03')+".html","wb").write(serebiiCode)
    #Get psypokes code
    psypokesLink = pokemonXml.getElementsByTagName("link_psypokes")[0].firstChild.data
    psypokesCode = downloadPage(psypokesLink)
    open("cache/psypokes/"+format(dexNum,'03')+".html","wb").write(psypokesCode)
    #Sleep 3, to stop them all banning me
    time.sleep(3)


