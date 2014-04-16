import re
import pickle
import urllib.request, urllib.error, urllib.parse
import xmltodict
import time

import ircbot_chk
import mod_calc

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
            value = float(mod_calc.mod_calc.fn_calc(self,valuestr,client,destination))
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
        result = value*convert['units'][unit_from]['value']/convert['units'][unit_to]['value']
        return str(value) + ' ' + unit_from + ' is ' + str(result) + ' ' + unit_to + "."

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
            return "All conversion aliases: " + ', '.join([alias + '->' + convert['alias'][alias] for alias in convert['alias']]) + "."
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
                type = args[0]
                del args[0]
            elif(args[1] in convert['types']):
                type = args[1]
                del args[1]
            elif(args[2] in convert['types']):
                type = args[2]
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
            convert['units'][name]['type'] = type
            convert['units'][name]['value'] = value
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Added " + name + " as a " + type + " unit, with a value of " + str(value) + " " + convert['types'][type]['base_unit'] + "."
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
            return 'Conversion unit types: ' + ', '.join([type for type in convert['types']]) + "."
        else:
            return 'Conversion unit types: ' + ', '.join([type + ' ( base unit: ' + convert['types'][type]['base_unit'] + ')' for type in convert['types']]) + "."
 
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
            pickle.dump(convert,open('store/convert.p','wb'))
            return "Value for " + unit + " set to " + str(value) + " " + convert['types'][convert['units'][unit]['type']]['base_unit'] + "."
        else:
            return "You have insufficient privileges to update the value of a conversion unit."

    def fnn_convert_update_1_eurobank(self,args,client,destination):
        'Updates the value of conversion currency units using the European Central Bank xml info.'
        url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        pagerequest = urllib.request.Request(url)
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageopener = urllib.request.build_opener()
        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read().decode('utf-8')
        eurobankdict = xmltodict.parse(code)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        for item in eurobankdict['gesmes:Envelope']['Cube']['Cube']['Cube']:
            unit = item['@currency'].lower()
            value = 1/float(item['@rate'].replace(',',''))
            if(unit not in convert['units']):
                convert['units'][unit] = {}
                convert['units'][unit]['type'] = 'currency'
            convert['units'][unit]['value'] = value
        convert['units']['eur']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Currency values updated using European Central bank data."

    def fnn_convert_update_2_moneyconvertor(self,args,client,destination):
        'Updates the value of conversion currency units using The Money Convertor data.'
        url = 'http://themoneyconverter.com/rss-feed/EUR/rss.xml'
        pagerequest = urllib.request.Request(url)
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageopener = urllib.request.build_opener()
        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read().decode('utf-8')
        moneyconvdict = xmltodict.parse(code)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        for item in moneyconvdict['rss']['channel']['item']:
            unit = item['title'].split('/')[0].lower()
            value = 1/float(item['description'].split('=')[1].split()[0].replace(',',''))
            if(unit=='eur'):
                continue
            if(unit not in convert['units']):
                convert['units'][unit] = {}
                convert['units'][unit]['type'] = 'currency'
            convert['units'][unit]['value'] = value
        convert['units']['eur']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Currency values updated using TheMoneyConvertor data."

    def fnn_convert_update_3_forex(self,args,client,destination):
        'Updates the value of conversion currency units using FOREX data.'
        url = 'http://rates.fxcm.com/RatesXML3'
        pagerequest = urllib.request.Request(url)
        pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageopener = urllib.request.build_opener()
        pageinfo = str(pageopener.open(pagerequest).info())
        code = pageopener.open(pagerequest).read().decode('utf-8')
        forexdict = xmltodict.parse(code)
        try:
            convert = pickle.load(open('store/convert.p','rb'))
        except:
            return "Could not load conversion data."
        for item in forexdict['Rates']['Rate']:
            if('EUR' not in item['Symbol']):
                continue
            unit = item['Symbol'].lower().replace('eur','')
            value = 1/(0.5*(float(item['Bid'])+float(item['Ask'])))
            if(unit not in convert['units']):
                convert['units'][unit] = {}
                convert['units'][unit]['type'] = 'currency'
            convert['units'][unit]['value'] = value
        convert['units']['eur']['last_update'] = time.time()
        pickle.dump(convert,open('store/convert.p','wb'))
        return "Currency values updated using Forex data."


    def fn_convert_currency_update(self,args,client,destination):
        'Update currency conversion figures, using data from the money convertor and the european central bank.'
        line1 = mod_conversion.fnn_convert_update_2_moneyconvertor(self,args,client,destination)
        line2 = mod_conversion.fnn_convert_update_1_eurobank(self,args,client,destination)
        line3 = mod_conversion.fnn_convert_update_3_forex(self,args,client,destination)
        return line1 + "\n" + line2 + "\n" + line3 + "\n" + "Completed update."



