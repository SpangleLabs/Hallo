import datetime
import re

import hallo.modules.user_data
from hallo.function import Function
from hallo.inc.commons import Commons


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
        regex_fluff = re.compile(r"\b(for|[io]n)\b")
        # Clear input fluff
        line_clean = regex_fluff.sub("", line_clean).strip()
        # Hunt for the days offset
        days_offset = 0
        regex_now = re.compile(r"(now|current(ly)?|today)")
        regex_tomorrow = re.compile(r"(to|the\s+)morrow")
        regex_weekday = re.compile(
            r"\b(this\s+|next\s+|)(mo(n(day)?)?|tu(e(s(day)?)?)?|we(d(nesday)?)?|th(u(r(sday)?)?)?|"
            + r"fr(i(day)?)?|sa(t(urday)?)?|su(n(day)?)?)\b"
        )
        regex_days = re.compile(r"(([0-9]+)\s*d(ays?)?)")
        regex_weeks = re.compile(r"(([0-9]+)\s*w(eeks?)?)")
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
        user_data_parser = hallo.modules.user_data.UserDataParser()
        if line_clean == "":
            location_entry = user_data_parser.get_data_by_user_and_type(
                event.user, hallo.modules.user_data.WeatherLocationData
            )
            if location_entry is None:
                return event.create_response(
                    "No location stored for this user. Please specify a location or "
                    + 'store one with the "setup weather location data" function.'
                )
        else:
            test_user = event.server.get_user_by_name(line_clean)
            if event.channel is not None and event.channel.is_user_in_channel(
                test_user
            ):
                location_entry = user_data_parser.get_data_by_user_and_type(
                    test_user, hallo.modules.user_data.WeatherLocationData
                )
                if location_entry is None:
                    return event.create_response(
                        "No location stored for this user. Please specify a location or "
                        + 'store one with the "setup weather location data" function.'
                    )
            else:
                location_entry = hallo.modules.user_data.WeatherLocationData.create_from_input(event)
        # Get API response
        api_key = event.server.hallo.get_api_key("openweathermap")
        if api_key is None:
            return event.create_response("No API key loaded for openweathermap.")
        url = (
            "https://api.openweathermap.org/data/2.5/forecast/daily{}"
            "&cnt=16&APPID={}".format(self.build_query(location_entry), api_key)
        )
        response = Commons.load_url_json(url)
        # Check API responded well
        if str(response["cod"]) != "200":
            return event.create_response("Location not recognised.")
        # Check that days is within bounds for API response
        days_available = len(response["list"])
        if days_offset > days_available:
            return event.create_response(
                "I cannot predict the weather that far in the future. "
                + "I can't predict much further than 2 weeks."
            )
        # Format and return output
        city_name = response["city"]["name"]
        if days_offset == 0:
            today_main = response["list"][0]["weather"][0]["main"]
            today_desc = response["list"][0]["weather"][0]["description"]
            today_temp = response["list"][0]["temp"]["day"] - 273.15
            today_humi = response["list"][0]["humidity"]
            today_spee = response["list"][0]["speed"]
            tomor_main = response["list"][1]["weather"][0]["main"]
            tomor_desc = response["list"][1]["weather"][0]["description"]
            tomor_temp = response["list"][1]["temp"]["day"] - 273.15
            tomor_humi = response["list"][1]["humidity"]
            tomor_spee = response["list"][1]["speed"]
            dayaf_main = response["list"][2]["weather"][0]["main"]
            dayaf_desc = response["list"][2]["weather"][0]["description"]
            dayaf_temp = response["list"][2]["temp"]["day"] - 273.15
            dayaf_humi = response["list"][2]["humidity"]
            dayaf_spee = response["list"][2]["speed"]
            output = (
                "Weather in {} today will be {} ({}) "
                "Temp: {:.2f}C, Humidity: {}%, Wind speed: {}m/s. ".format(
                    city_name,
                    today_main,
                    today_desc,
                    today_temp,
                    today_humi,
                    today_spee,
                )
            )
            # Add tomorrow output
            output += "Tomorrow: {} ({}) {:.2f}C {}% {}m/s ".format(
                tomor_main, tomor_desc, tomor_temp, tomor_humi, tomor_spee
            )
            # Day after output
            output += "Day after: {} ({}) {:.2f}C {}% {}m/s.".format(
                dayaf_main, dayaf_desc, dayaf_temp, dayaf_humi, dayaf_spee
            )
            return event.create_response(output)
        response_weather = response["list"][days_offset]
        weather_main = response_weather["weather"][0]["main"]
        weather_desc = response_weather["weather"][0]["description"]
        weather_temp = response_weather["temp"]["day"] - 273.15
        weather_humidity = response_weather["humidity"]
        weather_wind_speed = response_weather["speed"]
        output = (
            "Weather in {} {} will be {} ({}). "
            "Temp: {:.2f}C, Humidity: {}%, Wind speed: {}m/s".format(
                city_name,
                self.number_days(days_offset),
                weather_main,
                weather_desc,
                weather_temp,
                weather_humidity,
                weather_wind_speed,
            )
        )
        return event.create_response(output)

    def build_query(self, weather_location):
        """
        Creates query parameters for API call.
        :type weather_location: WeatherLocationData
        :rtype: str
        """
        if isinstance(weather_location.location, hallo.modules.user_data.WeatherLocationData.CityLocation):
            query = "?q={}".format(weather_location.location.city.replace(" ", "+"))
            if weather_location.country_code is not None:
                query += "," + weather_location.country_code
            return query
        if isinstance(weather_location.location, hallo.modules.user_data.WeatherLocationData.CoordLocation):
            query = "?lat={}&lon={}".format(
                weather_location.location.latitude, weather_location.location.longitude
            )
            return query
        if isinstance(weather_location.location, hallo.modules.user_data.WeatherLocationData.ZipLocation):
            query = "?zip={}".format(weather_location.location.zip_code)
            if weather_location.country_code is not None:
                query += "," + weather_location.country_code
            return query

    def weekday_to_number(self, weekday):
        """Converts weekday text to integer. Monday = 0"""
        weekday_clean = weekday.lower().strip()
        weekday_regex_list = [
            re.compile(r"mo(n(day)?)?"),
            re.compile(r"tu(e(s(day)?)?)?"),
            re.compile(r"we(d(nesday)?)?"),
            re.compile(r"th(u(r(sday)?)?)?"),
            re.compile(r"fr(i(day)?)?"),
            re.compile(r"sa(t(urday)?)?"),
            re.compile(r"su(n(day)?)?"),
        ]
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
