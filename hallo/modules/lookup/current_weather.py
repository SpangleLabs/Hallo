import hallo.modules
from hallo.function import Function
from hallo.inc.commons import Commons


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
        user_data_parser = hallo.modules.user_data.UserDataParser()
        line_clean = event.command_args.strip().lower()
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
            # Check if a user was specified
            test_user = event.user.server.get_user_by_name(line_clean)
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
        api_key = event.server.hallo.get_api_key("openweathermap")
        if api_key is None:
            return event.create_response("No API key loaded for openweathermap.")
        url = "https://api.openweathermap.org/data/2.5/weather{}&APPID={}".format(
            self.build_query(location_entry), api_key
        )
        response = Commons.load_url_json(url)
        if str(response["cod"]) != "200":
            return event.create_response("Location not recognised.")
        city_name = response["name"]
        weather_main = response["weather"][0]["main"]
        weather_desc = response["weather"][0]["description"]
        weather_temp = response["main"]["temp"] - 273.15
        weather_humidity = response["main"]["humidity"]
        weather_wind_speed = response["wind"]["speed"]
        output = (
            "Current weather in {} is {} ({}). "
            "Temp: {:.2f}C, Humidity: {}%, Wind speed: {}m/s".format(
                city_name,
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