import re
from abc import ABCMeta

from function import Function


class UserDataException(Exception):
    pass


class UserDataParser:
    def __init__(self):
        pass

    def get_data_by_user(self, user):
        """
        :type user: User
        :rtype: dict[str, UserDatum]
        """
        user_data_dict = user.extra_data_dict
        user_data = dict()
        for key in user_data_dict:
            user_data[key] = UserDataFactory.from_dict(key, user_data_dict[key])
        return user_data

    def get_data_by_user_and_type(self, user, data_class):
        """
        :type user: User
        :type data_class: class
        :rtype: UserDatum
        """
        type_name = data_class.type_name
        user_data_dict = user.extra_data_dict
        if type_name in user_data_dict:
            return UserDataFactory.from_dict(type_name, user_data_dict[type_name])
        return None

    def set_user_data(self, user, data):
        """
        Adds a data object to a user, or overrides if one already exists.
        :type user: User
        :type data: UserDatum
        """
        user.extra_data_dict[data.type_name] = data.to_json()
        user.server.hallo.save_json()

    def remove_data_by_user_and_type(self, user, data_class):
        """
        :type user: User
        :type data_class: class
        :rtype: UserDatum
        """
        type_name = data_class.type_name
        if type_name in user.extra_data_dict:
            del user.extra_data_dict.type_name


class UserDatum(metaclass=ABCMeta):
    type_name = ""
    names = []

    @staticmethod
    def create_from_input(event):
        raise NotImplementedError()

    def get_name(self, event):
        raise NotImplementedError()

    def to_json(self):
        """
        :rtype: dict
        """
        raise NotImplementedError()

    @staticmethod
    def from_json(json_dict):
        """
        :type json_dict: dict
        """
        raise NotImplementedError()


class FAKeyData(UserDatum):
    type_name = "fa_key"
    names = [
        "furaffinity key",
        "fa key",
        "fa cookies",
        "furaffinity cookies",
        "fa",
        "furaffinity",
    ]

    def __init__(self, cookie_a, cookie_b):
        self.cookie_a = cookie_a
        self.cookie_b = cookie_b

    @staticmethod
    def create_from_input(event):
        input_clean = event.command_args.strip().lower().replace(";", " ").split()
        if len(input_clean) != 2:
            raise UserDataException(
                "Input must include cookie a and cookie b, in the format a=value;b=value"
            )
        if input_clean[0].startswith("b="):
            input_clean = list(reversed(input_clean))
        cookie_a = input_clean[0][2:]
        cookie_b = input_clean[1][2:]
        new_data = FAKeyData(cookie_a, cookie_b)
        return new_data

    def get_name(self, event):
        return event.user.name + " FA login"

    def to_json(self):
        json_obj = dict()
        json_obj["cookie_a"] = self.cookie_a
        json_obj["cookie_b"] = self.cookie_b
        return json_obj

    @staticmethod
    def from_json(json_dict):
        cookie_a = json_dict["cookie_a"]
        cookie_b = json_dict["cookie_b"]
        return FAKeyData(cookie_a, cookie_b)


class WeatherLocationData(UserDatum):
    type_name = "weather_location"
    names = ["weather location"]

    TYPE_CITY = "city"
    TYPE_COORDS = "coords"
    TYPE_ZIP = "zip"

    def __init__(self, location):
        self.location = location
        """ :type : Location"""
        self.country_code = None
        """ :type : str"""

    @staticmethod
    def create_from_input(event):
        input_line = event.command_args
        # Check if zip code is given
        if re.match(r"^\d{5}(?:[-\s]\d{4})?$", input_line):
            return WeatherLocationData(WeatherLocationData.ZipLocation(input_line))
        # Check if coordinates are given
        coord_match = re.match(r"^(-?\d+(\.\d+)?)[ ,]*(-?\d+(\.\d+)?)$", input_line)
        if coord_match:
            new_lat = coord_match.group(1)
            new_long = coord_match.group(3)
            return WeatherLocationData(
                WeatherLocationData.CoordLocation(new_lat, new_long)
            )
        # Otherwise, assume it's a city
        new_city = input_line
        return WeatherLocationData(WeatherLocationData.CityLocation(new_city))

    def get_name(self, event):
        return event.user.name + " weather location"

    def to_json(self):
        return self.location.to_json()

    @staticmethod
    def from_json(json_dict):
        if json_dict["type"] == WeatherLocationData.TYPE_CITY:
            return WeatherLocationData(
                WeatherLocationData.CityLocation.from_json(json_dict)
            )
        if json_dict["type"] == WeatherLocationData.TYPE_COORDS:
            return WeatherLocationData(
                WeatherLocationData.CoordLocation.from_json(json_dict)
            )
        if json_dict["type"] == WeatherLocationData.TYPE_ZIP:
            return WeatherLocationData(
                WeatherLocationData.ZipLocation.from_json(json_dict)
            )
        raise UserDataException("Unrecognised weather location type.")

    class Location(metaclass=ABCMeta):
        def to_json(self):
            raise NotImplementedError()

        @staticmethod
        def from_json(json_obj):
            raise NotImplementedError()

    class CityLocation(Location):
        def __init__(self, city):
            self.city = city

        def to_json(self):
            return {"type": WeatherLocationData.TYPE_CITY, "city": self.city}

        @staticmethod
        def from_json(json_obj):
            return WeatherLocationData.CityLocation(json_obj["city"])

    class ZipLocation(Location):
        def __init__(self, zip_code):
            self.zip_code = zip_code

        def to_json(self):
            return {"type": WeatherLocationData.TYPE_ZIP, "zip_code": self.zip_code}

        @staticmethod
        def from_json(json_obj):
            return WeatherLocationData.ZipLocation(json_obj["zip_code"])

    class CoordLocation(Location):
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude

        def to_json(self):
            return {
                "type": WeatherLocationData.TYPE_COORDS,
                "latitude": self.latitude,
                "longitude": self.longitude,
            }

        @staticmethod
        def from_json(json_obj):
            return WeatherLocationData.CoordLocation(
                json_obj["coord_x"], json_obj["coord_y"]
            )


class UserDataFactory:
    data_classes = [FAKeyData]

    @staticmethod
    def get_data_type_names():
        return [
            name
            for common_class in UserDataFactory.data_classes
            for name in common_class.names
        ]

    @staticmethod
    def get_data_class_by_name(name):
        classes = [
            data_class
            for data_class in UserDataFactory.data_classes
            if name in data_class.names
        ]
        if len(classes) != 1:
            raise UserDataException(
                "Failed to find a common configuration type matching the name {}".format(
                    name
                )
            )
        return classes[0]

    @staticmethod
    def from_dict(type_name, data_dict):
        for data_class in UserDataFactory.data_classes:
            if data_class.type_name == type_name:
                return data_class.from_json(data_dict)
        raise UserDataException("Could not load user data of type {}".format(type_name))


class UserDataSetup(Function):
    """
    Sets up a user's common configuration in the subscription repository
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "setup user data"
        # Names which can be used to address the function
        name_templates = {
            "setup {} user data",
            "setup user data {}",
            "setup user data for {}",
            "{} user data setup",
        }
        self.names = set(
            [
                template.format(name)
                for name in UserDataFactory.get_data_type_names()
                for template in name_templates
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Sets up user data which other functions may require. "
            "Format: setup user data <type> <parameters>"
        )
        self.user_data_parser = UserDataParser()
        """ :type : UserDataParser"""

    def run(self, event):
        # Construct type name
        data_type_name = " ".join(
            [
                w
                for w in event.command_name.lower().split()
                if w not in ["setup", "user", "data", "for"]
            ]
        ).strip()
        # Get class from type name
        data_class = UserDataFactory.get_data_class_by_name(
            data_type_name
        )  # type: UserDatum
        if data_class is None:
            return event.create_response(
                "Could not find a user data type called {}. "
                "Available types are: {}".format(
                    data_type_name,
                    ", ".join(
                        [
                            data_class.names[0]
                            for data_class in UserDataFactory.data_classes
                        ]
                    ),
                )
            )
        # Create user data object
        data_obj = data_class.create_from_input(event)
        # Save user data
        self.user_data_parser.set_user_data(event.user, data_obj)
        # Send response
        return event.create_response(
            "Set up a new user data for {}".format(data_obj.get_name(event))
        )


class UserDataTeardown(Function):
    """
    Tears down a user's user data of a given type
    """

    tear_down_words = ["tear down", "teardown", "remove"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "tear down user data"
        # Names which can be used to address the function
        name_templates = {
            "{1} {0} user data",
            "{1} user data {0}",
            "{1} user data for {0}",
            "{0} user data {1}",
        }
        self.names = set(
            [
                template.format(name, tearDown)
                for name in UserDataFactory.get_data_type_names()
                for template in name_templates
                for tearDown in self.tear_down_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Removes user data of a specified type. "
            "Format: tear down user data <type> <parameters>"
        )

    def run(self, event):
        # Construct type name
        data_type_name = " ".join(
            [
                w
                for w in event.command_name.split()
                if w not in ["user", "data", "for", "teardown", "tear", "down"]
            ]
        ).strip()
        # Get class from type name
        data_class = UserDataFactory.get_data_class_by_name(data_type_name)
        # Get a user data parser
        user_data_parser = UserDataParser()
        # Remove user data
        common_obj = user_data_parser.get_data_by_user_and_type(event.user, data_class)
        user_data_parser.remove_data_by_user_and_type(event.user, data_class)
        # Send response
        return event.create_response(
            "Removed user data for {}".format(common_obj.get_name(event))
        )
