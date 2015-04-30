import re
from xml.dom import minidom
import codecs

regexSpace = re.compile(">[\s]*<")
with codecs.open("pokemon.xml", "r", "utf-8") as inp:
    xmlString = inp.read()
xmlString = xmlString.replace("\n","").replace("\r","")
xmlString = regexSpace.sub("><",xmlString)
with codecs.open("pokemon2.xml", "w", "utf-8") as out:
    out.write(xmlString)

regexTag = re.compile("<[^>]*>")

doc = minidom.parse("pokemon2.xml")

for pokemonXml in doc.getElementsByTagName("pokemon"):
    dexNum = int(pokemonXml.getElementsByTagName("dex_number")[0].firstChild.data)
    with codecs.open("cache/bulbapedia_edit/"+format(dexNum,'03')+".html","r","utf-8") as inp:
        code = inp.read()
    nameJapaneseS = re.search('jname=([^|]*)\|',code)
    if(nameJapaneseS is not None):
        nameJapanese = nameJapaneseS.group(1).strip()
        nameJapaneseXml = doc.createElement("name_japanese")
        nameJapaneseXml.appendChild(doc.createTextNode(nameJapanese))
        pokemonXml.appendChild(nameJapaneseXml)
    nameJapaneseRomS = re.search('tmname=([^|]*)\|',code)
    if(nameJapaneseRomS is not None):
        nameJapaneseRom = nameJapaneseRomS.group(1).strip()
        nameJapaneseRomXml = doc.createElement("name_japanese_romanised")
        nameJapaneseRomXml.appendChild(doc.createTextNode(nameJapaneseRom))
        pokemonXml.appendChild(nameJapaneseRomXml)
    nameJapaneseTraS = re.search('jtranslit=([^|]*)\|',code)
    if(nameJapaneseTraS is not None):
        nameJapaneseTra = nameJapaneseTraS.group(1).strip()
        nameJapaneseTraXml = doc.createElement("name_japanese_transliterated")
        nameJapaneseTraXml.appendChild(doc.createTextNode(nameJapaneseTra))
        pokemonXml.appendChild(nameJapaneseTraXml)
    speciesNameS = re.search('^[\s|]*species=([^|]*)\|',code,re.MULTILINE)
    if(speciesNameS is not None):
        speciesName = speciesNameS.group(1).strip()+" Pokémon"
        speciesName = regexTag.sub("",speciesName)
        speciesNameXml = doc.createElement("species_name")
        speciesNameXml.appendChild(doc.createTextNode(speciesName))
        pokemonXml.appendChild(speciesNameXml)
    generationS = re.search('generation=([^|]*)\|',code)
    if(generationS is not None):
        generation = generationS.group(1).strip()
        generationXml = doc.createElement("generation")
        generationXml.appendChild(doc.createTextNode(generation))
        pokemonXml.appendChild(generationXml)
    type1S = re.search('type1=([^|]*)\|',code)
    if(type1S is not None):
        type1 = type1S.group(1).strip()
        type1Xml = doc.createElement("type1")
        type1Xml.appendChild(doc.createTextNode(type1))
        pokemonXml.appendChild(type1Xml)
    type2S = re.search('type2=([^|]*)\|',code)
    if(type2S is not None):
        type2 = type2S.group(1).strip()
        type2Xml = doc.createElement("type2")
        type2Xml.appendChild(doc.createTextNode(type2))
        pokemonXml.appendChild(type2Xml)
    ability1S = re.search('ability1=([^|]*)\|',code)
    if(ability1S is not None):
        ability1 = ability1S.group(1).strip()
        ability1Xml = doc.createElement("ability1")
        ability1Xml.appendChild(doc.createTextNode(ability1))
        pokemonXml.appendChild(ability1Xml)
    ability2S = re.search('ability2=([^|]*)\|',code)
    if(ability2S is not None):
        ability2 = ability2S.group(1).strip()
        ability2Xml = doc.createElement("ability2")
        ability2Xml.appendChild(doc.createTextNode(ability2))
        pokemonXml.appendChild(ability2Xml)
    abilityHiddenS = re.search('abilityd=([^|]*)\|',code)
    if(abilityHiddenS is not None):
        abilityHidden = abilityHiddenS.group(1).strip()
        abilityHiddenXml = doc.createElement("ability_hidden")
        abilityHiddenXml.appendChild(doc.createTextNode(abilityHidden))
        pokemonXml.appendChild(abilityHiddenXml)
    genderCodeS = re.search('gendercode=([^|]*)\|',code)
    if(genderCodeS is not None):
        genderCode = genderCodeS.group(1).strip()
        genderDistribution = "???"
        if(genderCode=="256"):
            genderDistribution = "unknown"
        elif(genderCode=="255"):
            genderDistribution = "genderless"
        elif(genderCode=="254"):
            genderDistribution = "all female"
        elif(genderCode=="223"):
            genderDistribution = "1:7 male:female"
        elif(genderCode=="191"):
            genderDistribution = "1:3 male:female"
        elif(genderCode=="127"):
            genderDistribution = "1:1 male:female"
        elif(genderCode=="63"):
            genderDistribution = "3:1 male:female"
        elif(genderCode=="31"):
            genderDistribution = "7:1 male:female"
        elif(genderCode=="0"):
            genderDistribution = "all male"
        genderDistributionXml = doc.createElement("gender_distribution")
        genderDistributionXml.appendChild(doc.createTextNode(genderDistribution))
        pokemonXml.appendChild(genderDistributionXml)


with codecs.open("pokemon3.xml", "w", "utf-8") as out:
    doc.writexml(out,addindent="\t",newl="\r\n")
