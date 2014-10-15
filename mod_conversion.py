import re
import pickle
import time
import datetime

import ircbot_chk
import mod_calc
import mod_lookup

class mod_conversion:

    def fn_convert(self,args,client,destination):
        'converts values from one unit to another. Format: convert <value> <old unit> to <new unit>'
        args = args.lower()
        from_to = re.compile(' into | to | in |->',re.IGNORECASE).split(args)
        if(len(from_to)>2):
            return "I'm confused by your input, are you trying to convert between three units? or not provided me something to convert to?"
        valuestr = ''
        for char in from_to[0]:
            if(char in [str(x) for x in range(10)] + ['.',"(",")","^","*","x","/","+","-"]):
                valuestr = valuestr + char
            else:
                break
        from_to[0] = from_to[0][len(valuestr):]
        if(valuestr==''):
            for char in from_to[0][::-1]:
                if(char in [str(x) for x in range(10)] + ['.',"(",")","^","*","x","/","+","-"]):
                    valuestr = char + valuestr
                else:
                    break
            from_to[0] = from_to[0][:len(from_to[0])-len(valuestr)]
            if(valuestr==''):
                valuestr = '1'
        unit_from = from_to[0]
        while(unit_from[0]==' '):
            unit_from = unit_from[1:]
        if(ircbot_chk.ircbot_chk.chk_msg_numbers(self,valuestr)):
            value = float(valuestr)
        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,valuestr)):
            valuestr = mod_calc.mod_calc.fn_calc(self,valuestr,client,destination)
            if(valuestr[-1]=='.'):
                valuestr = valuestr[:-1]
            value = float(valuestr)
        else:
            return "Invalid number."
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Failed to load conversion data."
        if(unit_from.replace(' ','') not in convert['units']):
            if(unit_from.replace(' ','') in convert['alias']):
                unit_from = convert['alias'][unit_from.replace(' ','')]
            else:
                return unit_from + ' is not a recognised unit.'
        unit_from = unit_from.replace(' ','')
        if(len(from_to)<2):
            unit_to = convert['types'][convert['units'][unit_from]['type']]['base_unit']
        else:
            unit_to = from_to[1]
        if(unit_to.replace(' ','') not in convert['units']):
            if(unit_to.replace(' ','') in convert['alias']):
                unit_to = convert['alias'][unit_to.replace(' ','')]
            else:
                return unit_to + ' is not a recognised unit.'
        unit_to = unit_to.replace(' ','')
        if(convert['units'][unit_to]['type'] != convert['units'][unit_from]['type']):
            return 'These units are not of the same type, a conversion cannot be made.'
        update_str = ''
        if('last_update' in convert['units'][unit_to] and 'last_update' in convert['units'][unit_from]):
            last_update = min(convert['units'][unit_to]['last_update'],convert['units'][unit_from]['last_update'])
            update_str = ' (Last updated: ' + datetime.datetime.fromtimestamp(last_update).strftime('%Y-%m-%d %H:%M:%S') + '.)'
        result = value*convert['units'][unit_from]['value']/convert['units'][unit_to]['value']
        if('decimals' in convert['types'][convert['units'][unit_to]['type']]):
            if(round(result,convert['types'][convert['units'][unit_to]['type']]['decimals'])!=0):
                result = round(result,convert['types'][convert['units'][unit_to]['type']]['decimals'])
        return str(value) + ' ' + unit_from + ' is ' + str(result) + ' ' + unit_to + "." + update_str

    def fn_convert_add_alias(self,args,client,destination):
        'Add a new alias for a conversion unit. Format: convert_add_alias <name> <unit>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            args = args.lower().split()
            name_a = args[0]
            name_b = ''.join(args[1:])
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            if(name_a in convert['units']):
                convert['alias'][name_b] = name_a
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Set " + name_b + " as an alias to " + name_a + "."
            elif(name_b in convert['units']):
                convert['alias'][name_a] = name_b
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Set " + name_a + " as an alias to " + name_b + "."
            else:
                return "Neither " + name_a + " nor " + name_b + " seem to be known units."
        else:
            return "You have insufficient privileges to add a conversion alias."

    def fn_convert_del_alias(self,args,client,destination):
        'Delete an alias for a conversion unit. Format: convert_del_alias <alias>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            if(args in convert['alias']):
                del convert['alias'][args]
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Deleted the " + args + " alias."
            else:
                return args + " is not a valid alias."
        else:
            return "You have insufficient privileges to delete a conversion alias."

    def fn_convert_list_alias(self,args,client,destination):
        'List all alaises, or all aliases of a given type if given. Format: convert_list_alias <type>'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args.replace(' ','') == ''):
#            return "All conversion aliases: " + ', '.join([alias + '->' + convert['alias'][alias] for alias in convert['alias']]) + "."
            return "There are too many conversion aliases to list, specify a unit or unit type. Valid unit types are: " + ', '.join([conv_type for conv_type in convert['types']]) + "."
        elif(args in convert['types']):
            return args + " conversion aliases: " + ', '.join([alias + '->' + convert['alias'][alias] for alias in convert['alias'] if convert['units'][convert['alias'][alias]]['type'] == args]) + "."
        elif(args in convert['units']):
            return args + " aliases: " + ', '.join([alias + '->' + args for alias in convert['alias'] if convert['alias'][alias] == args]) + "."
        else:
            return args + " is not a valid unit type."

    def fn_convert_add_unit(self,args,client,destination):
        'Add a conversion unit. value in the default for that type. Format: convert_add_unit <type> <name> <value>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            if(len(args.split()) < 3):
                return "Incorrect number of arguments, format is: convert_add_unit {type} {name} {value}."
            args = args.split()
            args[2] = ''.join(args[2:])
            if(args[0] in convert['types']):
                conv_type = args[0]
                del args[0]
            elif(args[1] in convert['types']):
                conv_type = args[1]
                del args[1]
            elif(args[2] in convert['types']):
                conv_type = args[2]
                del args[2]
            else:
                return "Unit type does not seem to be defined."
            try:
                value = float(args[0])
                del args[0]
            except:
                try:
                    value = float(args[1])
                    del args[1]
                except:
                    return "Value does not seem to be defined."
            name = args[0]
            convert['units'][name] = {}
            convert['units'][name]['type'] = conv_type
            convert['units'][name]['value'] = value
            convert['units'][name]['last_update'] = time.time()
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Added " + name + " as a " + conv_type + " unit, with a value of " + str(value) + " " + convert['types'][conv_type]['base_unit'] + "."
        else:
            return "You have insufficient privileges to add a conversion unit."

    def fn_convert_del_unit(self,args,client,destination):
        'Deletes a unit from conversion data, including all alises. Format: convert_del_unit <name>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            if(args in convert['units']):
                del convert['units'][args]
                for alias in convert['alias']:
                    if(convert['alias'][alias] == args):
                        del convert['alias'][alias]
                pickle.dump(convert,open('store/convert.p','wb'))
                return "Deleted " + args + " from conversion data."
            else:
                return args + " is not a valid unit."
        else:
            return "You have insufficient privileges to delete a conversion unit."

    def fn_convert_list_units(self,args,client,destination):
        'Lists all units in conversion data or all units of a type, if given. Format: convert_list_units <type>'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args.replace(' ','') == ''):
            return 'all available units: ' + ', '.join([unit + ' (' + convert['units'][unit]['type'] + ' unit, =' + str(convert['units'][unit]['value']) + convert['types'][convert['units'][unit]['type']]['base_unit'] + ')' for unit in convert['units']]) + "."
        elif(args.split()[0] in convert['types']):
            if(len(args.split())>1 and args.split()[1] == 'simple'):
                return 'Simplified list of ' + args.split()[0] + ' units: ' + ', '.join([unit for unit in convert['units'] if convert['units'][unit]['type'] == args.split()[0]]) + "."
            else:
                return 'List of' + args.split()[0] + ' units: ' + ', '.join([unit + ' (=' + str(convert['units'][unit]['value']) + convert['types'][convert['units'][unit]['type']]['base_unit'] + ')' for unit in convert['units'] if convert['units'][unit]['type'] == args.split()[0]]) + "."
        elif(args == 'simple'):
            return 'Simplified list of available units: ' + ', '.join([unit for unit in convert['units']]) + "."
        else:
            return "Invalid unit type."

    def fn_convert_add_type(self,args,client,destination):
        'Adds a new conversion unit type and base unit. Format: convert_add_type <name> <base_unit>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower().split()
            args[1] = ''.join(args[1:])
            convert['types'][args[0]] = {}
            convert['types'][args[0]]['base_unit'] = args[1]
            convert['units'][args[1]] = {}
            convert['units'][args[1]]['type'] = args[0]
            convert['units'][args[1]]['value'] = 1
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Added " + args[0] + " as a unit type, with " + args[1] + " as the base unit."
        else:
            return "You have insufficient privileges to add a new conversion unit type."

    def fn_convert_del_type(self,args,client,destination):
        'Delete a conversion unit type and all associated units and aliases. Format: convert_del_type <type>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower()
            del convert['types'][args]
            units_list = list(convert['units'])
            for unit in units_list:
                if(convert['units'][unit]['type'] == args):
                    del convert['units'][unit]
                    alias_list = list(convert['alias'])
                    for alias in alias_list:
                        if(convert['alias'][alias] == unit):
                            del convert['alias'][alias]
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Deleted " + type + " unit type and all associated units and aliases."
        else:
            return "You have insufficient privileges to delete a conversion unit type."

    def fn_convert_list_types(self,args,client,destination):
        'Lists conversion unit types. Format: convert_list_types'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args == 'simple'):
            return 'Conversion unit types: ' + ', '.join([conv_type for conv_type in convert['types']]) + "."
        else:
            return 'Conversion unit types: ' + ', '.join([type + ' ( base unit: ' + convert['types'][conv_type]['base_unit'] + ')' for conv_type in convert['types']]) + "."
 
    def fn_convert_default_unit(self,args,client,destination):
        'Returns the default unit for a given type. Format: convert_default_unit <type>'
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        args = args.lower()
        if(args not in convert['types']):
            return args + " is not a valid conversion unit type."
        return "The default unit for " + args + " is " + convert['types'][args]['base_unit'] + "."

    def fn_convert_unit_update(self,args,client,destination):
        'Update the value of a conversion unit. Format: convert_unit_update <name> <value>'
        if(ircbot_chk.ircbot_chk.chk_god(self,destination[0],client)):
            try:
                convert = pickle.load(open('store/convert.p','rb'))
            except:
                return "Could not load conversion data."
            args = args.lower().split()
            if(args[0] in convert['units']):
                unit = args[0]
                valuestr = args[1]
            elif(args[1] in convert['units']):
                unit = args[1]
                valuestr = args[0]
            else:
                return "No valid unit given."
            try:
                value = float(valuestr)
            except:
                return "No valid value given."
            convert['units'][unit]['value'] = value
            convert['units'][unit]['last_update'] = time.time()
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Value for " + unit + " set to " + str(value) + " " + convert['types'][convert['units'][unit]['type']]['base_unit'] + "."
        else:
            return "You have insufficient privileges to update the value of a conversion unit."

    def fnn_convert_update_1_eurobank(self,args,client,destination):
        'Updates the value of conversion currency units using the European Central Bank xml info.'
        url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        eurobankdict = mod_lookup.mod_lookup.fnn_loadxml(self,url)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        update_datestr = eurobankdict['gesmes:Envelope']['Cube']['Cube']['@time']
        update_date = datetime.date(int(update_datestr.split('-')[0]),int(update_datestr.split('-')[1]),int(update_datestr.split('-')[2]))
        update_timestamp = (update_date-datetime.date(1970,1,1)).total_seconds()
        for item in eurobankdict['gesmes:Envelope']['Cube']['Cube']['Cube']:
            unit = item['@currency'].lower()
            value = 1/float(item['@rate'].replace(',',''))
            if('last_update' in convert['units'][unit] and convert['units'][unit]['last_update'] > update_timestamp):
                continue
            if(unit not in convert['units']):
                convert['units'][unit] = {}
                convert['units'][unit]['type'] = 'currency'
            convert['units'][unit]['value'] = value
            convert['units'][unit]['last_update'] = update_timestamp
        convert['units']['eur']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Currency values updated using European Central bank data."

    def fnn_convert_update_2_moneyconvertor(self,args,client,destination):
        'Updates the value of conversion currency units using The Money Convertor data.'
        url = 'http://themoneyconverter.com/rss-feed/EUR/rss.xml'
        moneyconvdict = mod_lookup.mod_lookup.fnn_loadxml(self,url)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        for item in moneyconvdict['rss']['channel']['item']:
            unit = item['title'].split('/')[0].lower()
            value = 1/float(item['description'].split('=')[1].split()[0].replace(',',''))
            update_datestr = item['pubDate']
            update_date = time.strptime(update_datestr,'%a, %d %b %Y %H:%M:%S %Z')
            update_time = time.mktime(update_date)
            if('last_update' in convert['units'][unit] and convert['units'][unit]['last_update'] > update_time):
                continue
            if(unit=='eur'):
                continue
            if(unit not in convert['units']):
                convert['units'][unit] = {}
                convert['units'][unit]['type'] = 'currency'
            convert['units'][unit]['value'] = value
            convert['units'][unit]['last_update'] = update_time
        convert['units']['eur']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Currency values updated using TheMoneyConvertor data."

    def fnn_convert_update_3_forex(self,args,client,destination):
        'Updates the value of conversion currency units using FOREX data.'
        url = 'http://rates.fxcm.com/RatesXML3'
        forexdict = mod_lookup.mod_lookup.fnn_loadxml(self,url)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        for item in forexdict['Rates']['Rate']:
            if('EUR' not in item['Symbol']):
                continue
            unit = item['Symbol'].lower().replace('eur','')
            value = 1/(0.5*(float(item['Bid'])+float(item['Ask'])))
            update_datestr = item['Time']
            update_date = time.strptime(update_datestr,'%Y-%m-%d %H:%M:%S')
            update_time = time.mktime(update_date) + 5*3600
            if('last_update' in convert['units'][unit] and convert['units'][unit]['last_update'] > update_time):
                continue
            if(unit not in convert['units']):
                convert['units'][unit] = {}
                convert['units'][unit]['type'] = 'currency'
            convert['units'][unit]['value'] = value
            convert['units'][unit]['last_update'] = update_time
        convert['units']['eur']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Currency values updated using Forex data."

    def fnn_convert_update_crypto(self,url,currcode,convert):
        'Gets current value of a cryptocurrency.'
        crypt_dict = mod_lookup.mod_lookup.fnn_loadjson(self,url)
        crypt_dest = list(crypt_dict[currcode])[0]
        crypt_vol = 0
        crypt_tot = 0
        for crypt_source in crypt_dict[currcode][crypt_dest]:
            if(crypt_dict[currcode][crypt_dest][crypt_source] is not None):
                crypt_vol = crypt_vol + float(crypt_dict[currcode][crypt_dest][crypt_source]['volume'])
                crypt_tot = crypt_tot + (float(crypt_dict[currcode][crypt_dest][crypt_source]['last'])*float(crypt_dict[currcode][crypt_dest][crypt_source]['volume']))
        if(crypt_vol==0):
            return False
        crypt_value = (crypt_tot/crypt_vol)*convert['units'][crypt_dest]['value']
        return crypt_value

    def fnn_convert_update_4_crypto(self,args,client,destination):
        'Updates values for 4 cryptocurrencies, using preev.org data.'
        convert = pickle.load(open('store/convert.p','rb'))
        ltc_url = 'http://preev.com/pulse/units:ltc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken'
        ltc_val = mod_conversion.fnn_convert_update_crypto(self,ltc_url,'ltc',convert)
        if(ltc_val):
            if('ltc' not in convert['units']):
                convert['units']['ltc'] = {}
                convert['units']['ltc']['type'] = 'currency'
            convert['units']['ltc']['value'] = ltc_val
            convert['units']['ltc']['last_update'] = time.time()
        ppc_url = 'http://preev.com/pulse/units:ppc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken'
        ppc_val = mod_conversion.fnn_convert_update_crypto(self,ppc_url,'ppc',convert)
        if(ppc_val):
            if('ppc' not in convert['units']):
                convert['units']['ppc'] = {}
                convert['units']['ppc']['type'] = 'currency'
            convert['units']['ppc']['value'] = ppc_val
            convert['units']['ppc']['last_update'] = time.time()
        btc_url = 'http://preev.com/pulse/units:btc+eur/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken'
        btc_val = mod_conversion.fnn_convert_update_crypto(self,btc_url,'btc',convert)
        if(btc_val):
            if('btc' not in convert['units']):
                convert['units']['btc'] = {}
                convert['units']['btc']['type'] = 'currency'
            convert['units']['btc']['value'] = btc_val
            convert['units']['btc']['last_update'] = time.time()
        xdg_url = 'http://preev.com/pulse/units:xdg+btc/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken'
        xdg_val = mod_conversion.fnn_convert_update_crypto(self,xdg_url,'xdg',convert)
        if(xdg_val):
            if('xdg' not in convert['units']):
                convert['units']['xdg'] = {}
                convert['units']['xdg']['type'] = 'currency'
            convert['units']['xdg']['value'] = xdg_val
            convert['units']['xdg']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Updated cryptocurrencies from preev.org data."

    def fn_convert_currency_update(self,args,client,destination):
        'Update currency conversion figures, using data from the money convertor and the european central bank.'
        line1 = mod_conversion.fnn_convert_update_2_moneyconvertor(self,args,client,destination)
        line2 = mod_conversion.fnn_convert_update_1_eurobank(self,args,client,destination)
        line3 = mod_conversion.fnn_convert_update_3_forex(self,args,client,destination)
        line4 = mod_conversion.fnn_convert_update_4_crypto(self,args,client,destination)
        return line1 + "\n" + line2 + "\n" + line3 + "\n" + line4 + "\n" + "Completed update."

    def fn_protein(self,args,client,destination):
        'Convert a set of neucleobases to a string of amino acids'
        codon_table = {}
        codon_table['Ala'] = ['GCU','GCC','GCA','GCG']
        codon_table['Arg'] = ['CGU','CGC','CGA','CGG','AGA','AGG']
        codon_table['Asn'] = ['AAU','AAC']
        codon_table['Cys'] = ['UGU','UGC']
        codon_table['Gln'] = ['CAA','CAG']
        codon_table['Glu'] = ['GAA','GAG']
        codon_table['Gly'] = ['GGU','GGC','GGA','GGG']
        codon_table['His'] = ['CAU','CAC']
        codon_table['Ile'] = ['AUU','AUC','AUA']
        codon_table['START'] = ['AUG']
        codon_table['Leu'] = ['UUA','UUG','CUU','CUC','CUA','CUG']
        codon_table['Lys'] = ['AAA','AAG']
        codon_table['Met'] = ['AUG']
        codon_table['Phe'] = ['UUU','UUC']
        codon_table['Pro'] = ['CCU','CCC','CCA','CCG']
        codon_table['Ser'] = ['UCU','UCC','UCA','UCG','AGU','AGC']
        codon_table['Thr'] = ['ACU','ACC','ACA','ACG']
        codon_table['Trp'] = ['UGG']
        codon_table['Tyr'] = ['UAU','UAC']
        codon_table['Val'] = ['GUU','GUC','GUA','GUG']
        codon_table['STOP'] = ['UAA','UGA','UAG']
        args = args.upper().replace('T','U')
        if(0 in [c in 'ACGU' for c in args]):
            return "error, invalid neucleotides."
        strand = ["..."]
        if(codon_table['START'][0] in args):
            strand = ["START"]
            args = args.split(codon_table['START'][0])[-1]
        stop = False
        while(len(args)>=3 and not stop):
            codon = args[:3]
            args = args[3:]
            for protein in codon_table :
                if(codon in codon_table[protein]):
                    strand += [protein]
                    if(protein=="STOP"):
                        stop = True
                    break
        if(not stop):
            strand += ["..."]
        return "-".join(strand)
    

    def fnn_convert_list_types(self,convert,unit1=None,unit2=None):
        'Lists possible unit types for given units.'
        if(unit1 is None):
            return list(convert['types'])
        if(unit2 is None):
            returnlist = []
            for unittype in convert['types']:
                if(unit1 in convert['types'][unittype]['units']):
                    returnlist.add(unittype)
            return returnlist
        returnlist = []
        for unittype in convert['types']:
            if(unit1 in convert['types'][unittype]['units'] and unit2 in convert['types'][unittype]['units']):
                returnlist.add(unittype)
        return returnlist
        
    def fnn_convert_process_string(self,convert,args,client,destination):
        'Processes the convert input into a dictionary of types and values'
        args = args.lower()
        from_to = re.compile(' into | to | in |->',re.IGNORECASE).split(args)
        if(len(from_to)>2):
            raise ValueError("Converting between three units")
        from_to[0] = from_to[0].strip()
        #find the section of the first part which is a number or simple mathematical formula
        valuesearch = re.split(r'^([0-9.()*+/^-]+)',from_to[0])
        if(len(valuesearch)==1):
            valuesearch = re.split(r'([0-9.()*+/^-]+)$',from_to[0])
            if(len(valuesearch)==1):
                valuesearch = ['','1',from_to[0]]
            else:
                valuesearch = valuesearch[::-1]
        valuestr = valuesearch[1]
        unit_from = valuesearch[2].strip()
        #process valuestr into a number or calculate
        if(ircbot_chk.ircbot_chk.chk_msg_numbers(self,valuestr)):
            try:
                value = float(valuestr)
            except ValueError:
                raise ValueError("Invalid number")
        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,valuestr)):
            valuestr = mod_calc.mod_calc.fn_calc(self,valuestr,client,destination)
            valuestr = valuestr.strip('.')
            try:
                value = float(valuestr)
            except ValueError:
                raise ValueError("Invalid number")
        else:
            raise ValueError("Invalid number.")
        if(len(from_to)==1):
            unit_types = self.fnn_convert_list_types(unit_from)
            if(len(unit_types)!=1):
                raise ValueError("Undefined unit type")
            else:
                unit_to = convert['units'][unit_types[0]]['base_unit']
        else:
            unit_to = from_to[1]
        return [value,unit_from,unit_to]
        
