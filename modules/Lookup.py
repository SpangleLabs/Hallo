from Events import EventMessage
from Function import Function
from inc.Commons import Commons
from xml.dom import minidom
import difflib
import re
import urllib.parse
import urllib.request
import struct  # UrlDetect image size
import imghdr  # UrlDetect image size
import math
import datetime
import html
import html.parser

from modules.UserData import UserDataParser, WeatherLocationData


class UrbanDictionary(Function):
    """
    Urban Dictionary lookup function.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "urban dictionary"
        # Names which can be used to address the function
        self.names = {"urban dictionary", "urban", "urbandictionary", "ud"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Gives the top urban dictionary definition for a word. Format: urban dictionary <word>"

    def run(self, event):
        url_line = event.command_args.replace(' ', '+').lower()
        url = "http://api.urbandictionary.com/v0/define?term={}".format(url_line)
        urban_dict = Commons.load_url_json(url)
        if len(urban_dict['list']) > 0:
            definition = urban_dict['list'][0]['definition'].replace("\r", '').replace("\n", '')
            return event.create_response(definition)
        else:
            return event.create_response("Sorry, I cannot find a definition for {}.".format(event.command_args))


class RandomCocktail(Function):
    """
    Selects and outputs a random cocktail from store/cocktail_list.xml
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random cocktail"
        # Names which can be used to address the function
        self.names = {"random cocktail", "randomcocktail"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Delivers ingredients and recipes for a random cocktail. Format: random cocktail"

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/cocktail_list.xml")
        cocktail_list_elem = doc.getElementsByTagName("cocktail_list")[0]
        random_cocktail_elem = Commons.get_random_choice(cocktail_list_elem.getElementsByTagName("cocktail"))[0]
        random_cocktail_name = random_cocktail_elem.getElementsByTagName("name")[0].firstChild.data
        random_cocktail_instructions = random_cocktail_elem.getElementsByTagName("instructions")[0].firstChild.data
        output_string = "Randomly selected cocktail is: {}. The ingredients are: ".format(random_cocktail_name)
        ingredient_list = []
        for ingredient_elem in random_cocktail_elem.getElementsByTagName("ingredients"):
            ingredient_amount = ingredient_elem.getElementsByTagName("amount")[0].firstChild.data
            ingredient_name = ingredient_elem.getElementsByTagName("name")[0].firstChild.data
            ingredient_list.append(ingredient_amount + ingredient_name)
        output_string += ", ".join(ingredient_list) + ". The recipe is: " + random_cocktail_instructions
        if output_string[-1] != '.':
            output_string += "."
        return event.create_response(output_string)


class Cocktail(Function):
    """
    Cocktail lookup function.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "cocktail"
        # Names which can be used to address the function
        self.names = {"cocktail"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns ingredients and instructions for a given cocktail (or closest guess). " \
                         "Format: cocktail <name>"

    def run(self, event):
        """Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>"""
        doc = minidom.parse("store/cocktail_list.xml")
        cocktail_list_elem = doc.getElementsByTagName("cocktail_list")[0]
        cocktail_names = []
        # Loop through cocktails, adding names to list
        cocktail_elem = None
        for cocktail_elem in cocktail_list_elem.getElementsByTagName("cocktail"):
            cocktail_name = cocktail_elem.getElementsByTagName("name")[0].firstChild.data
            cocktail_names.append(cocktail_name)
        # Find the closest matching names
        closest_matches = difflib.get_close_matches(event.command_args.lower(), cocktail_names)
        # If there are no close matches, return error
        if len(closest_matches) == 0 or closest_matches[0] == '':
            return event.create_response("I haven't got anything close to that name.")
        # Get closest match XML
        closest_match_name = closest_matches[0]
        for cocktail_elem in cocktail_list_elem.getElementsByTagName("cocktail"):
            cocktail_name = cocktail_elem.getElementsByTagName("name")[0].firstChild.data
            if cocktail_name.lower() == closest_match_name.lower():
                break
        # Get instructions
        cocktail_instructions = cocktail_elem.getElementsByTagName("instructions")[0].firstChild.data
        # Get list of ingredients
        ingredient_list = []
        for ingredient_elem in cocktail_elem.getElementsByTagName("ingredients"):
            ingredient_amount = ingredient_elem.getElementsByTagName("amount")[0].firstChild.data
            ingredient_name = ingredient_elem.getElementsByTagName("name")[0].firstChild.data
            ingredient_list.append(ingredient_amount + ingredient_name)
        # Construct output
        output_string = "Closest I have is {}.".format(closest_match_name)
        output_string += "The ingredients are: {}.".format(", ".join(ingredient_list))
        output_string += "The recipe is: {}".format(cocktail_instructions)
        if output_string[-1] != ".":
            output_string += "."
        return event.create_response(output_string)


class InSpace(Function):
    """
    Looks up the current amount and names of people in space
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "in space"
        # Names which can be used to address the function
        self.names = {"in space", "inspace", "space"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the number of people in space right now, and their names. Format: in space"

    def run(self, event):
        space_dict = Commons.load_url_json("http://www.howmanypeopleareinspacerightnow.com/space.json")
        space_number = str(space_dict['number'])
        space_names = ", ".join(person['name'].strip() for person in space_dict['people'])
        output_string = "There are {} people in space right now. Their names are: {}.".format(space_number, space_names)
        return event.create_response(output_string)

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        clean_line = event.text.lower()
        if "in space" in clean_line and ("who" in clean_line or "how many" in clean_line):
            event.split_command_text("", clean_line)
            return self.run(event)


class TimestampToDate(Function):
    """
    Converts an unix timestamp to a date
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "date"
        # Names which can be used to address the function
        self.names = {"timestamp to date", "unix timestamp", "unix", "unix timestamp to date"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the date from a given unix timestamp. Format: date <timestamp>"

    def run(self, event):
        try:
            line = int(event.command_args)
        except ValueError:
            return event.create_response("Invalid timestamp")
        return event.create_response(Commons.format_unix_time(line) + ".")


class Wiki(Function):
    """
    Lookup wiki article and return the first paragraph or so.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "wiki"
        # Names which can be used to address the function
        self.names = {"wiki", "wikipedia"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Reads the first paragraph from a wikipedia article"

    def run(self, event):
        line_clean = event.command_args.strip().replace(" ", "_")
        url = "http://en.wikipedia.org/w/api.php?format=json&action=query&titles={}" \
              "&prop=revisions&rvprop=content&redirects=True".format(line_clean)
        article_dict = Commons.load_url_json(url)
        page_code = list(article_dict['query']['pages'])[0]
        article_text = article_dict['query']['pages'][page_code]['revisions'][0]['*']
        old_scan = article_text
        new_scan = re.sub('{{[^{^}]*}}', '', old_scan)  # Strip templates
        while new_scan != old_scan:
            old_scan = new_scan
            new_scan = re.sub('{{[^{^}]*}}', '', old_scan)  # Keep stripping templates until they're gone
        plain_text = new_scan.replace('\'\'', '')
        plain_text = re.sub(r'<ref[^<]*</ref>', '', plain_text)  # Strip out references
        old_scan = plain_text
        new_scan = re.sub(r'(\[\[File:[^\][]+)\[\[[^\]]+]]', r'\1',
                          old_scan)  # Repeatedly strip links from image descriptions
        while new_scan != old_scan:
            old_scan = new_scan
            new_scan = re.sub(r'(\[\[File:[^\][]+)\[\[[^\]]+]]', r'\1', old_scan)
        plain_text = new_scan
        plain_text = re.sub(r'\[\[File:[^\]]+]]', '', plain_text)  # Strip out images
        plain_text = re.sub(r'\[\[[^\]^|]*\|([^\]]*)]]', r'\1', plain_text)  # Strip out links with specified names
        plain_text = re.sub(r'\[\[([^\]]*)]]', r'\1', plain_text)  # Strip out links
        plain_text = re.sub(r'<!--[^>]*-->', '', plain_text)  # Strip out comments
        plain_text = re.sub(r'<ref[^>]*/>', '', plain_text)  # Strip out remaining references
        first_paragraph = plain_text.strip().split('\n')[0]
        return event.create_response(first_paragraph)


class Translate(Function):
    """
    Uses google translate to translate a phrase to english, or to any specified language
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "translate"
        # Names which can be used to address the function
        self.names = {"translate"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Translates a given block of text. Format: translate <from>-><to> <text>"

    def run(self, event):
        if len(event.command_args.split()) <= 1:
            lang_change = ''
            trans_string = event.command_args
        else:
            lang_change = event.command_args.split()[0]
            trans_string = ' '.join(event.command_args.split()[1:])
        if '->' not in lang_change:
            lang_from = "auto"
            lang_to = "en"
            trans_string = lang_change + ' ' + trans_string
        else:
            lang_from = lang_change.split('->')[0]
            lang_to = lang_change.split('->')[1]
        trans_safe = urllib.parse.quote(trans_string.strip(), '')
        # This uses google's secret translate API, it's not meant to be used by robots, and often it won't work
        url = "http://translate.google.com/translate_a/t?client=t&text={}&hl=en&sl={}&tl={}" \
              "&ie=UTF-8&oe=UTF-8&multires=1&otf=1&pc=1&trs=1&ssel=3&tsel=6&sc=1".format(trans_safe, lang_from, lang_to)
        trans_dict = Commons.load_url_json(url, [], True)
        translation_string = " ".join([x[0] for x in trans_dict[0]])
        return event.create_response("Translation: {}".format(translation_string))


class CurrentWeather(Function):
    """
    Returns the current weather in your location, or asks for your location.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "current weather"
        # Names which can be used to address the function
        self.names = {"current weather", "weather current", "current weather in"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the current weather in your location (if known) or in provided location."

    def run(self, event):
        user_data_parser = UserDataParser()
        line_clean = event.command_args.strip().lower()
        if line_clean == "":
            location_entry = user_data_parser.get_data_by_user_and_type(event.user, WeatherLocationData)
            if location_entry is None:
                return event.create_response("No location stored for this user. Please specify a location or " +
                                             "store one with the \"setup weather location data\" function.")
        else:
            # Check if a user was specified
            test_user = event.user.server.get_user_by_name(line_clean)
            if event.channel is not None and event.channel.is_user_in_channel(test_user):
                location_entry = user_data_parser.get_data_by_user_and_type(test_user, WeatherLocationData)
                if location_entry is None:
                    return event.create_response("No location stored for this user. Please specify a location or " +
                                                 "store one with the \"setup weather location data\" function.")
            else:
                location_entry = WeatherLocationData.create_from_input(event)
        api_key = event.server.hallo.get_api_key("openweathermap")
        if api_key is None:
            return event.create_response("No API key loaded for openweathermap.")
        url = "http://api.openweathermap.org/data/2.5/weather{}&APPID={}".format(self.build_query(location_entry),
                                                                                 api_key)
        response = Commons.load_url_json(url)
        if str(response['cod']) != "200":
            return event.create_response("Location not recognised.")
        city_name = response['name']
        weather_main = response['weather'][0]['main']
        weather_desc = response['weather'][0]['description']
        weather_temp = response['main']['temp'] - 273.15
        weather_humidity = response['main']['humidity']
        weather_wind_speed = response['wind']['speed']
        output = "Current weather in {} is {} ({}). " \
                 "Temp: {:.2f}C, Humidity: {}%, Wind speed: {}m/s".format(city_name, weather_main, weather_desc,
                                                                          weather_temp, weather_humidity,
                                                                          weather_wind_speed)
        return event.create_response(output)

    def build_query(self, weather_location):
        """
        Creates query parameters for API call.
        :type weather_location: WeatherLocationData
        :rtype: str
        """
        if isinstance(weather_location.location, WeatherLocationData.CityLocation):
            query = "?q={}".format(weather_location.location.city.replace(" ", "+"))
            if weather_location.country_code is not None:
                query += "," + weather_location.country_code
            return query
        if isinstance(weather_location.location, WeatherLocationData.CoordLocation):
            query = "?lat={}&lon={}".format(weather_location.location.latitude, weather_location.location.longitude)
            return query
        if isinstance(weather_location.location, WeatherLocationData.ZipLocation):
            query = "?zip={}".format(weather_location.location.zip_code)
            if weather_location.country_code is not None:
                query += "," + weather_location.country_code
            return query


class Weather(Function):
    """
    Currently returns a random weather phrase. In future perhaps nightvale weather?
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "weather"
        # Names which can be used to address the function
        self.names = {"weather", "weather in"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Random weather"

    def run(self, event):
        line_clean = event.command_args.strip().lower()
        regex_fluff = re.compile(r'\b(for|[io]n)\b')
        # Clear input fluff
        line_clean = regex_fluff.sub("", line_clean).strip()
        # Hunt for the days offset
        days_offset = 0
        regex_now = re.compile(r'(now|current(ly)?|today)')
        regex_tomorrow = re.compile(r'(to|the\s+)morrow')
        regex_weekday = re.compile(
            r'\b(this\s+|next\s+|)(mo(n(day)?)?|tu(e(s(day)?)?)?|we(d(nesday)?)?|th(u(r(sday)?)?)?|' +
            r'fr(i(day)?)?|sa(t(urday)?)?|su(n(day)?)?)\b')
        regex_days = re.compile(r'(([0-9]+)\s*d(ays?)?)')
        regex_weeks = re.compile(r'(([0-9]+)\s*w(eeks?)?)')
        if regex_now.search(line_clean):
            days_offset = 0
            line_clean = regex_now.sub("", line_clean).strip()
        elif regex_tomorrow.search(line_clean):
            days_offset = 1
            line_clean = regex_tomorrow.sub("", line_clean).strip()
        elif regex_weekday.search(line_clean):
            match = regex_weekday.search(line_clean)
            current_weekday = datetime.date.today().weekday()
            specified_weekday = self.weekday_to_number(match.group(2))
            days_offset = (specified_weekday - current_weekday) % 7
            line_clean = regex_weekday.sub("", line_clean).strip()
        elif regex_days.search(line_clean):
            match = regex_days.search(line_clean)
            days_offset = int(match.group(2))
            line_clean = regex_days.sub("", line_clean).strip()
        elif regex_weeks.search(line_clean):
            match = regex_weeks.search(line_clean)
            days_offset = 7 * int(match.group(2))
            line_clean = regex_weeks.sub("", line_clean).strip()
        # Figure out if a user or city was specified
        user_data_parser = UserDataParser()
        if line_clean == "":
            location_entry = user_data_parser.get_data_by_user_and_type(event.user, WeatherLocationData)
            if location_entry is None:
                return event.create_response("No location stored for this user. Please specify a location or " +
                                             "store one with the \"setup weather location data\" function.")
        else:
            test_user = event.server.get_user_by_name(line_clean)
            if event.channel is not None and event.channel.is_user_in_channel(test_user):
                location_entry = user_data_parser.get_data_by_user_and_type(test_user, WeatherLocationData)
                if location_entry is None:
                    return event.create_response("No location stored for this user. Please specify a location or " +
                                                 "store one with the \"setup weather location data\" function.")
            else:
                location_entry = WeatherLocationData.create_from_input(event)
        # Get API response
        api_key = event.server.hallo.get_api_key("openweathermap")
        if api_key is None:
            return event.create_response("No API key loaded for openweathermap.")
        url = "http://api.openweathermap.org/data/2.5/forecast/daily{}" \
              "&cnt=16&APPID={}".format(self.build_query(location_entry), api_key)
        response = Commons.load_url_json(url)
        # Check API responded well
        if str(response['cod']) != "200":
            return event.create_response("Location not recognised.")
        # Check that days is within bounds for API response
        days_available = len(response['list'])
        if days_offset > days_available:
            return event.create_response("I cannot predict the weather that far in the future. " +
                                         "I can't predict much further than 2 weeks.")
        # Format and return output
        city_name = response['city']['name']
        if days_offset == 0:
            today_main = response['list'][0]['weather'][0]['main']
            today_desc = response['list'][0]['weather'][0]['description']
            today_temp = response['list'][0]['temp']['day'] - 273.15
            today_humi = response['list'][0]['humidity']
            today_spee = response['list'][0]['speed']
            tomor_main = response['list'][1]['weather'][0]['main']
            tomor_desc = response['list'][1]['weather'][0]['description']
            tomor_temp = response['list'][1]['temp']['day'] - 273.15
            tomor_humi = response['list'][1]['humidity']
            tomor_spee = response['list'][1]['speed']
            dayaf_main = response['list'][2]['weather'][0]['main']
            dayaf_desc = response['list'][2]['weather'][0]['description']
            dayaf_temp = response['list'][2]['temp']['day'] - 273.15
            dayaf_humi = response['list'][2]['humidity']
            dayaf_spee = response['list'][2]['speed']
            output = "Weather in {} today will be {} ({}) " \
                     "Temp: {:.2f}C, Humidity: {}%, Wind speed: {}m/s. ".format(city_name, today_main, today_desc,
                                                                                today_temp, today_humi, today_spee)
            # Add tomorrow output
            output += "Tomorrow: {} ({}) {:.2f}C {}% {}m/s ".format(tomor_main, tomor_desc, tomor_temp,
                                                                    tomor_humi, tomor_spee)
            # Day after output
            output += "Day after: {} ({}) {:.2f}C {}% {}m/s.".format(dayaf_main, dayaf_desc, dayaf_temp,
                                                                     dayaf_humi, dayaf_spee)
            return event.create_response(output)
        response_weather = response['list'][days_offset]
        weather_main = response_weather['weather'][0]['main']
        weather_desc = response_weather['weather'][0]['description']
        weather_temp = response_weather['temp']['day'] - 273.15
        weather_humidity = response_weather['humidity']
        weather_wind_speed = response_weather['speed']
        output = "Weather in {} {} will be {} ({}). " \
                 "Temp: {:.2f}C, Humidity: {}%, Wind speed: {}m/s".format(city_name, self.number_days(days_offset),
                                                                          weather_main, weather_desc, weather_temp,
                                                                          weather_humidity, weather_wind_speed)
        return event.create_response(output)

    def build_query(self, weather_location):
        """
        Creates query parameters for API call.
        :type weather_location: WeatherLocationData
        :rtype: str
        """
        if isinstance(weather_location.location, WeatherLocationData.CityLocation):
            query = "?q={}".format(weather_location.location.city.replace(" ", "+"))
            if weather_location.country_code is not None:
                query += "," + weather_location.country_code
            return query
        if isinstance(weather_location.location, WeatherLocationData.CoordLocation):
            query = "?lat={}&lon={}".format(weather_location.location.latitude, weather_location.location.longitude)
            return query
        if isinstance(weather_location.location, WeatherLocationData.ZipLocation):
            query = "?zip={}".format(weather_location.location.zip_code)
            if weather_location.country_code is not None:
                query += "," + weather_location.country_code
            return query

    def weekday_to_number(self, weekday):
        """Converts weekday text to integer. Monday = 0"""
        weekday_clean = weekday.lower().strip()
        weekday_regex_list = [re.compile(r'mo(n(day)?)?'),
                              re.compile(r'tu(e(s(day)?)?)?'),
                              re.compile(r'we(d(nesday)?)?'),
                              re.compile(r'th(u(r(sday)?)?)?'),
                              re.compile(r'fr(i(day)?)?'),
                              re.compile(r'sa(t(urday)?)?'),
                              re.compile(r'su(n(day)?)?')]
        for weekday_int in range(len(weekday_regex_list)):
            weekday_regex = weekday_regex_list[weekday_int]
            if weekday_regex.match(weekday_clean):
                return weekday_int
        return None

    def number_days(self, days_offset):
        if days_offset == 0:
            return "today"
        if days_offset == 1:
            return "tomorrow"
        return "in {} days".format(days_offset)


class UrlDetect(Function):
    """
    URL detection and title printing.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "urldetect"
        # Names which can be used to address the function
        self.names = {"urldetect"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "URL detection."
        self.hallo_obj = None

    def run(self, event):
        return event.create_response("This function does not take input.")

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        # Get hallo object for stuff to use
        self.hallo_obj = hallo_obj
        # Search for a link
        url_regex = re.compile(r'\b((https?://|www.)[-A-Z0-9+&?%@#/=~_|$:,.]*[A-Z0-9+&@#/%=~_|$])', re.I)
        url_search = url_regex.search(event.text)
        if not url_search:
            return None
        # Get link address
        url_address = url_search.group(1)
        # Add protocol if missing
        if "://" not in url_address:
            url_address = "http://" + url_address
        # Ignore local links.
        if '127.0.0.1' in url_address or '192.168.' in url_address or '10.' in url_address or '172.' in url_address:
            return None
        # Get page info
        page_request = urllib.request.Request(url_address)
        page_request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        page_opener = urllib.request.build_opener()
        page_info = str(page_opener.open(page_request).info())
        if "Content-Type:" in page_info:
            page_type = page_info.split()[page_info.split().index('Content-Type:') + 1]
        else:
            page_type = ''
        # Get the website name
        url_site = Commons.get_domain_name(url_address).lower()
        # Get response if link is an image
        if "image" in page_type:
            return event.create_response(self.url_image(url_address, page_opener, page_request, page_type))
        # Get a response depending on the website
        if url_site == "amazon":
            return event.create_response(self.site_amazon(url_address, page_opener, page_request))
        if url_site == "e621":
            return event.create_response(self.site_e621(url_address, page_opener, page_request))
        if url_site == "ebay":
            return event.create_response(self.site_ebay(url_address, page_opener, page_request))
        if url_site == "f-list":
            return event.create_response(self.site_flist(url_address, page_opener, page_request))
        if url_site == "furaffinity" or url_site == "facdn":
            return event.create_response(self.site_furaffinity(url_address, page_opener, page_request))
        if url_site == "imdb":
            return event.create_response(self.site_imdb(url_address, page_opener, page_request))
        if url_site == "imgur":
            return event.create_response(self.site_imgur(url_address, page_opener, page_request))
        if url_site == "speedtest":
            return event.create_response(self.site_speedtest(url_address, page_opener, page_request))
        if url_site == "reddit" or url_site == "redd":
            return event.create_response(self.site_reddit(url_address, page_opener, page_request))
        if url_site == "wikipedia":
            return event.create_response(self.site_wikipedia(url_address, page_opener, page_request))
        if url_site == "youtube" or url_site == "youtu":
            return event.create_response(self.site_youtube(url_address, page_opener, page_request))
        # If other url, return generic URL response
        return event.create_response(self.url_generic(url_address, page_opener, page_request))

    def url_image(self, url_address, page_opener, page_request, page_type):
        """Handling direct image links"""
        # Get the website name
        url_site = Commons.get_domain_name(url_address).lower()
        # If website name is speedtest or imgur, hand over to those handlers
        if url_site == "speedtest":
            return self.site_speedtest(url_address, page_opener, page_type)
        if url_site == "imgur":
            return self.site_imgur(url_address, page_opener, page_type)
        # Image handling
        image_data = page_opener.open(page_request).read()
        image_width, image_height = self.get_image_size(image_data)
        image_size = len(image_data)
        image_size_str = self.file_size_to_string(image_size)
        return "Image: {} ({}px by {}px) {}.".format(page_type, image_width, image_height, image_size_str)

    def url_generic(self, url_address, page_opener, page_request):
        """Handling for generic links not caught by any other url handling function."""
        page_code = page_opener.open(page_request).read(4096).decode('utf-8', 'ignore')
        if page_code.count('</title>') == 0:
            return None
        title_search = re.search('<title[^>]*>([^<]*)</title>', page_code, re.I)
        if title_search is None:
            return None
        title_text = title_search.group(1)
        title_clean = self.html_unescape(title_text).replace("\n", "").strip()
        if title_clean != "":
            return "URL title: {}".format(title_clean.replace("\n", ""))
        return None

    def html_unescape(self, html_str):
        """
        :param html_str: HTML string to parse
        :type html_str: str
        :return: str
        """
        try:
            # noinspection PyUnresolvedReferences
            return html.unescape(html_str)
        except AttributeError:
            html_parser = html.parser.HTMLParser()
            # noinspection PyDeprecation
            return html_parser.unescape(html_str)

    def site_amazon(self, url_address, page_opener, page_request):
        """Handling for amazon links"""
        # I spent ages trying to figure out the amazon API, and I gave up.
        # TODO: write amazon link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_e621(self, url_address, page_opener, page_request):
        """Handling for e621 links"""
        # TODO: write e621 link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_ebay(self, url_address, page_opener, page_request):
        """Handling for ebay links"""
        # Get the ebay item id
        item_id = url_address.split("/")[-1]
        api_key = self.hallo_obj.get_api_key("ebay")
        if api_key is None:
            return None
        # Get API response
        api_url = "http://open.api.ebay.com/shopping?callname=GetSingleItem&responseencoding=JSON&appid={}" \
                  "&siteid=0&version=515&ItemID={}&IncludeSelector=Details".format(api_key, item_id)
        api_dict = Commons.load_url_json(api_url)
        # Get item data from api response
        item_title = api_dict["Item"]["Title"]
        item_price = "{} {}".format(api_dict["Item"]["CurrentPrice"]["Value"],
                                    api_dict["Item"]["CurrentPrice"]["CurrencyID"])
        item_end_time = api_dict["Item"]["EndTime"][:19].replace("T", " ")
        # Start building output
        output = "eBay> Title: {} | Price: {} | ".format(item_title, item_price)
        # Check listing type
        if api_dict["Item"]["ListingType"] == "Chinese":
            # Listing type: bidding
            item_bid_count = str(api_dict["Item"]["BidCount"])
            if item_bid_count == "1":
                output += "Auction, {} bid".format(item_bid_count)
            else:
                output += "Auction, {} bids".format(item_bid_count)
        elif api_dict["Item"]["ListingType"] == "FixedPriceItem":
            # Listing type: buy it now
            output += "Buy it now | "
        output += "Ends: {}".format(item_end_time)
        return output

    def site_flist(self, url_address, page_opener, page_request):
        """Handling for f-list links"""
        # TODO: write f-list link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_furaffinity(self, url_address, page_opener, page_request):
        """Handling for furaffinity links"""
        # TODO: write furaffinity link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_imdb(self, url_address, page_opener, page_request):
        """Handling for imdb links"""
        # If URL isn't to an imdb title, just do normal url handling.
        if 'imdb.com/title' not in url_address:
            return self.url_generic(url_address, page_opener, page_request)
        # Get the imdb movie ID
        movie_id_search = re.search('title/(tt[0-9]*)', url_address)
        if movie_id_search is None:
            return self.url_generic(url_address, page_opener, page_request)
        movie_id = movie_id_search.group(1)
        # Download API response
        api_url = "http://www.omdbapi.com/?i={}".format(movie_id)
        api_dict = Commons.load_url_json(api_url)
        # Get movie information from API response
        movie_title = api_dict['Title']
        movie_year = api_dict['Year']
        movie_genre = api_dict['Genre']
        movie_rating = api_dict['imdbRating']
        movie_votes = api_dict['imdbVotes']
        # Construct output
        output = "IMDB> Title: {} ({}) | Rating {}/10, {} votes. | Genres: {}.".format(movie_title, movie_year,
                                                                                       movie_rating, movie_votes,
                                                                                       movie_genre)
        return output

    def site_imgur(self, url_address, page_opener, page_request):
        """Handling imgur links"""
        # Hand off imgur album links to a different handler function.
        if "/a/" in url_address:
            return self.site_imgur_album(url_address, page_opener, page_request)
        # Handle individual imgur image links
        # Example imgur links: http://i.imgur.com/2XBqIIT.jpg http://imgur.com/2XBqIIT
        imgur_id = url_address.split('/')[-1].split('.')[0]
        api_url = "https://api.imgur.com/3/image/{}".format(imgur_id)
        # Load API response (in json) using Client-ID.
        api_key = self.hallo_obj.get_api_key("imgur")
        if api_key is None:
            return None
        api_dict = Commons.load_url_json(api_url, [['Authorization', api_key]])
        # Get title, width, height, size, and view count from API data
        image_title = str(api_dict['data']['title'])
        image_width = str(api_dict['data']['width'])
        image_height = str(api_dict['data']['height'])
        image_size = int(api_dict['data']['size'])
        image_size_string = self.file_size_to_string(image_size)
        image_views = api_dict['data']['views']
        # Create output and return
        output = "Imgur> Title: {} | Size: {}x{} | Filesize: {} | Views: {:,}.".format(image_title, image_width,
                                                                                       image_height, image_size_string,
                                                                                       image_views)
        return output

    def site_imgur_album(self, url_address, page_opener, page_request):
        """Handling imgur albums"""
        # http://imgur.com/a/qJctj#0 example imgur album
        imgur_id = url_address.split('/')[-1].split('#')[0]
        api_url = "https://api.imgur.com/3/album/{}".format(imgur_id)
        # Load API response (in json) using Client-ID.
        api_key = self.hallo_obj.get_api_key("imgur")
        if api_key is None:
            return None
        api_dict = Commons.load_url_json(api_url, [['Authorization', api_key]])
        # Get album title and view count from API data
        album_title = api_dict['data']['title']
        album_views = api_dict['data']['views']
        # Start on output
        output = "Imgur album> Album title: {} | Gallery views: {:,} | ".format(album_title, album_views)
        if 'section' in api_dict['data']:
            album_section = api_dict['data']['section']
            output += "Section: {} | ".format(album_section)
        album_count = api_dict['data']['images_count']
        # If an image was specified, show some information about that specific image
        if "#" in url_address:
            image_number = int(url_address.split('#')[-1])
            image_width = api_dict['data']['images'][image_number]['width']
            image_height = api_dict['data']['images'][image_number]['height']
            image_size = int(api_dict['data']['images'][image_number]['size'])
            image_size_string = self.file_size_to_string(image_size)
            output += "Image {} of {} | Current image: {}x{}, {}.".format(image_number+1, album_count, image_width,
                                                                          image_height, image_size_string)
            return output
        output += "{} images.".format(album_count)
        return output

    def site_pastebin(self, url_address, page_opener, page_request):
        """Handling pastebin links"""
        # TODO: write pastebin link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_reddit(self, url_address, page_opener, page_request):
        """Handling reddit links"""
        # TODO: write reddit link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_speedtest(self, url_address, page_opener, page_request):
        """Handling speedtest links"""
        if url_address[-4:] == '.png':
            url_number = url_address[32:-4]
            url_address = "http://www.speedtest.net/my-result/".format(url_number)
            page_request = urllib.request.Request(url_address)
            page_request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
            page_opener = urllib.request.build_opener()
        page_code = page_opener.open(page_request).read().decode('utf-8')
        page_code = re.sub(r'\s+', '', page_code)
        download = re.search('<h3>Download</h3><p>([0-9.]*)', page_code).group(1)
        upload = re.search('<h3>Upload</h3><p>([0-9.]*)', page_code).group(1)
        ping = re.search('<h3>Ping</h3><p>([0-9]*)', page_code).group(1)
        return "Speedtest> Download: {}Mb/s | Upload: {}Mb/s | Ping: {}ms".format(download, upload, ping)

    def site_wikipedia(self, url_address, page_opener, page_request):
        """Handling for wikipedia links"""
        # TODO: write wikipedia link handler
        return self.url_generic(url_address, page_opener, page_request)

    def site_youtube(self, url_address, page_opener, page_request):
        """Handling for youtube links"""
        # Find video id
        if "youtu.be" in url_address:
            video_id = url_address.split("/")[-1].split("?")[0]
        else:
            video_id = url_address.split("/")[-1].split("=")[1].split("&")[0]
        # Find API url
        api_key = self.hallo_obj.get_api_key("youtube")
        if api_key is None:
            return None
        api_url = "https://www.googleapis.com/youtube/v3/videos?id={}" \
                  "&part=snippet,contentDetails,statistics&key={}".format(video_id, api_key)
        # Load API response (in json).
        api_dict = Commons.load_url_json(api_url)
        # Get video data from API response.
        video_title = api_dict['items'][0]['snippet']['title']
        video_duration = api_dict['items'][0]['contentDetails']['duration'][2:].lower()
        video_views = api_dict['items'][0]['statistics']['viewCount']
        # Create output
        output = "Youtube video> Title: {} | Length {} | Views: {}.".format(video_title, video_duration, video_views)
        return output

    def get_image_size(self, image_data):
        """
        Determine the image type of fhandle and return its size.
        from draco
        """
        # This function is from here:
        # http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
        image_head = image_data[:24]
        if len(image_head) != 24:
            return
        if imghdr.what(None, image_data) == 'png':
            check = struct.unpack('>i', image_head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', image_head[16:24])
        elif imghdr.what(None, image_data) == 'gif':
            width, height = struct.unpack('<HH', image_head[6:10])
        elif imghdr.what(None, image_data) == 'jpeg':
            # try:
                byte_offset = 0
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    byte_offset += size
                    byte = image_data[byte_offset]
                    byte_offset += 1
                    while byte == 0xff:
                        byte = image_data[byte_offset]
                        byte_offset += 1
                    ftype = byte
                    size = struct.unpack('>H', image_data[byte_offset:byte_offset + 2])[0] - 2
                    byte_offset += 2
                # We are at a SOFn block
                byte_offset += 1  # Skip `precision' byte.
                height, width = struct.unpack('>HH', image_data[byte_offset:byte_offset + 4])
                byte_offset += 4
            # except Exception:  # IGNORE:W0703
                # return
        else:
            return
        return width, height

    def file_size_to_string(self, size):
        if size < 2048:
            size_string = "{}Bytes".format(size)
        elif size < (2048 * 1024):
            size_string = "{}KiB".format(math.floor(float(size) / 10.24) / 100)
        elif size < (2048 * 1024 * 1024):
            size_string = "{}MiB".format(math.floor(float(size) / (1024 * 10.24)) / 100)
        else:
            size_string = "{}GiB".format(math.floor(float(size) / (1024 * 1024 * 10.24)) / 100)
        return size_string
