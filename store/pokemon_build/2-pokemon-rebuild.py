import pickle
import urllib.request, urllib.parse
import time




def code_decode(code):
    try:
        text = code.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = code.decode('iso-8859-1')
        except UnicodeDecodeError:
            try:
                text = code.decode('cp1252')
            except UnicodeDecodeError:
                text = code.decode('utf-8','ignore')
    return text

def get_page(url):
    pagerequest = urllib.request.Request(url)
    pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
    pageopener = urllib.request.build_opener()
    #try:
    code = code_decode(pageopener.open(pagerequest).read())
    #except:
    #    return None
    return code

def get_dexes(num):
    url = "http://pokemondb.net/pokedex/"+str(num)
    code = get_page(url)
    try:
        dex_code = code.split('<div id="dex-flavor"></div>')[1].split('</table>')[0]
    except:
        print(num)
        print(code)
        print(1/0)
    dex_entries = dex_code.split('<tr>')
    del dex_entries[0]
    dex_data = {}
    for dex_entry in dex_entries:
        dex_name = dex_entry.split('<th>')[1].split('</th>')[0]
        dex_text = dex_entry.split('<td>')[1].split('</td>')[0]
        if(dex_name=='Red<br>Blue'):
            dex_data['Red'] = dex_text
            dex_data['Blue'] = dex_text
        elif(dex_name=='Yellow'):
            dex_data['Yellow'] = dex_text
        elif(dex_name=='Gold'):
            dex_data['Gold'] = dex_text
        elif(dex_name=='Silver'):
            dex_data['Silver'] = dex_text
        elif(dex_name=='Crystal'):
            dex_data['Crystal'] = dex_text
        elif(dex_name=='Ruby<br>Sapphire'):
            dex_data['Ruby'] = dex_text
            dex_data['Sapphire'] = dex_text
        elif(dex_name=='Emerald'):
            dex_data['Emerald'] = dex_text
        elif(dex_name=='Ruby'):
            dex_data['Ruby'] = dex_text
        elif(dex_name=='Sapphire'):
            dex_data['Sapphire'] = dex_text
        elif(dex_name=='Ruby<br>Sapphire<br>Emerald'):
            dex_data['Ruby'] = dex_text
            dex_data['Sapphire'] = dex_text
            dex_data['Emerald'] = dex_text
        elif(dex_name=='FireRed'):
            dex_data['Fire_Red'] = dex_text
        elif(dex_name=='LeafGreen'):
            dex_data['Leaf_Green'] = dex_text
        elif(dex_name=='Diamond'):
            dex_data['Diamond'] = dex_text
        elif(dex_name=='Platinum'):
            dex_data['Platinum'] = dex_text
        elif(dex_name=='Diamond<br>Platinum'):
            dex_data['Diamond'] = dex_text
            dex_data['Platinum'] = dex_text
        elif(dex_name=='Pearl'):
            dex_data['Pearl'] = dex_text
        elif(dex_name=='Diamond<br>Pearl'):
            dex_data['Diamond'] = dex_text
            dex_data['Pearl'] = dex_text
        elif(dex_name=='Diamond<br>Pearl<br>Platinum'):
            dex_data['Diamond'] = dex_text
            dex_data['Pearl'] = dex_text
            dex_data['Platinum'] = dex_text
        elif(dex_name=='HeartGold'):
            dex_data['Heart_Gold'] = dex_text
        elif(dex_name=='SoulSilver'):
            dex_data['Soul_Silver'] = dex_text
        elif(dex_name=='Black'):
            dex_data['Black'] = dex_text
        elif(dex_name=='White'):
            dex_data['White'] = dex_text
        elif(dex_name=='Black<br>White'):
            dex_data['Black'] = dex_text
            dex_data['White'] = dex_text
        elif(dex_name=='Black 2<br>White 2'):
            dex_data['Black_2'] = dex_text
            dex_data['White_2'] = dex_text
        elif(dex_name=='Black<br>White<br>Black 2<br>White 2'):
            dex_data['Black'] = dex_text
            dex_data['White'] = dex_text
            dex_data['Black_2'] = dex_text
            dex_data['White_2'] = dex_text
        elif(dex_name=='X'):
            dex_data['X'] = dex_text
        elif(dex_name=='Y'):
            dex_data['Y'] = dex_text
        elif(dex_name=='X<br>Y'):
            dex_data['X'] = dex_text
            dex_data['Y'] = dex_text
        elif(dex_name=='FireRed<br>LeafGreen'):
            dex_data['Fire_Red'] = dex_text
            dex_data['Leaf_Green'] = dex_text
        elif(dex_name=='HeartGold<br>SoulSilver'):
            dex_data['Heart_Gold'] = dex_text
            dex_data['Soul_Silver'] = dex_text
        else:
            print("UNSUPPORTED: "+dex_name)
    return dex_data

            

pokemondata = pickle.load(open('pokemon.p','rb'))

for dexnum in pokemondata:
    time.sleep(1)
    print(str(dexnum)+'.',end='')
    dex_data = get_dexes(dexnum)
    pokemondata[dexnum]['Dex_entries'] = {}
    pokemondata[dexnum]['Dex_entries']['Anime'] = {}
    pokemondata[dexnum]['Dex_entries']['Games'] = dex_data

pickle.dump(pokemondata,open('pokemon2.p','wb'))
