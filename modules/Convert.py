import datetime
import json
from xml.dom import minidom

import dateutil.parser

from Events import EventHour, EventMessage
from inc.Commons import Commons
from Function import Function
import re


class ConvertException(Exception):
    pass


class ConvertInputParser:

    def __init__(self, raw_input):
        """
        :type raw_input: str
        """
        self.args_dict = dict()
        self.remaining_text = raw_input
        self.number_words = []
        self.string_words = []
        self.parse_args()
        self.parse_words()

    def parse_args(self):
        regexes = [re.compile(r"([\"'])(?P<key>[^=]+?)\1=([\"'])(?P<value>.*?)\3"),  # quoted key, quoted args
                   re.compile(r"(?P<key>[^\s]+)=([\"'])(?P<value>.*?)\2"),  # unquoted key, quoted args
                   re.compile(r"([\"'])(?P<key>[^=]+?)\1=(?P<value>[^\s]*)"),  # quoted key, unquoted args
                   re.compile(r"(?P<key>[^\s]+)=(?P<value>[^\s]*)")]  # unquoted key, unquoted args
        for regex in regexes:
            for match in regex.finditer(self.remaining_text):
                self.args_dict[match.group("key")] = match.group("value")
                self.remaining_text = self.remaining_text.replace(match.group(0), "")
        # Clean double spaces and trailing spaces.
        self.remaining_text = " ".join(self.remaining_text.split())

    def parse_words(self):
        for word in self.remaining_text.split():
            if Commons.is_float_string(word):
                self.number_words.append(float(word))
            else:
                self.string_words.append(word)

    def get_arg_by_names(self, names_list):
        for name in names_list:
            if name in self.args_dict:
                return self.args_dict[name]
        return None


class ConvertRepo:
    """
    Configuration repository. Stores list of ConvertTypes, ConvertPrefixGroups, etc
    """

    def __init__(self):
        """
        Constructor
        """
        self.type_list = []
        """:type : list[ConvertType]"""
        self.prefix_group_list = []
        """:type : list[ConvertPrefixGroup]"""

    def add_type(self, new_type):
        """
        Adds a new ConvertType object to the type list
        :param new_type: Conversion type to add to repo
        :type new_type: ConvertType
        """
        self.type_list.append(new_type)

    def remove_type(self, del_type):
        """
        Removes a ConvertType object from the type list
        :param del_type: Conversion type to remove from repo
        :type del_type: ConvertType
        """
        if del_type in self.type_list:
            self.type_list.remove(del_type)

    def get_type_by_name(self, name):
        """
        Gets a ConvertType object with the matching name.
        :param name: Name of the conversion type
        :type name: str
        """
        for type_obj in self.type_list:
            if type_obj.name == name:
                return type_obj
        for type_obj in self.type_list:
            if type_obj.name.lower() == name.lower():
                return type_obj
        return None

    def get_full_unit_list(self):
        """
        Returns the full list of ConvertUnit objects, in every ConvertType object.
        :rtype: list[ConvertUnit]
        """
        convert_unit_list = []
        for type_obj in self.type_list:
            convert_unit_list += type_obj.get_full_unit_list()
        return convert_unit_list

    def add_prefix_group(self, prefix_group):
        """
        Adds a new ConvertPrefixGroup object to the prefix group list.
        :param prefix_group: Prefix group to add to repo
        :type prefix_group: ConvertPrefixGroup
        """
        self.prefix_group_list.append(prefix_group)

    def remove_prefix_group(self, prefix_group):
        """
        Removes a ConvertPrefixGroup object from the prefix group list
        :param prefix_group: Prefix group to remove from repo
        :type prefix_group: ConvertPrefixGroup
        """
        if prefix_group in self.prefix_group_list:
            self.prefix_group_list.remove(prefix_group)

    def get_prefix_group_by_name(self, name):
        """
        Gets a ConvertPrefixGroup object with the matching name.
        :type name: str
        :rtype: ConvertPrefixGroup
        """
        for prefix_group_obj in self.prefix_group_list:
            if prefix_group_obj.name.lower() == name.lower():
                return prefix_group_obj
        return None

    @staticmethod
    def load_json():
        """
        Loads a new conversion repository from json file.
        :rtype: ConvertRepo
        """
        try:
            with open("store/convert.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            with open("store/convert-default.json", "r") as f:
                json_obj = json.load(f)
        new_repo = ConvertRepo()
        for prefix_group in json_obj["prefix_groups"]:
            new_repo.add_prefix_group(ConvertPrefixGroup.from_json(new_repo, prefix_group))
        for unit_type in json_obj["unit_types"]:
            new_repo.add_type(ConvertType.from_json(new_repo, unit_type))
        return new_repo

    def save_json(self):
        """
        Saves the convert unit repository to json.
        :return: None
        """
        # Create json object
        json_obj = dict()
        json_obj["prefix_groups"] = []
        for prefix_group in self.prefix_group_list:
            json_obj["prefix_groups"].append(prefix_group.to_json())
        json_obj["unit_types"] = []
        for unit_type in self.type_list:
            json_obj["unit_types"].append(unit_type.to_json())
        # Save json to file
        with open("store/convert.json", "w") as f:
            json.dump(json_obj, f, indent=2)


class ConvertType:
    """
    Conversion unit type object.
    """

    def __init__(self, repo, name):
        """
        :param repo: Repository this type belongs to
        :type repo: ConvertRepo
        :param name: Name of conversion type
        :type name: str
        """
        self.unit_list = []  # Contains all units of this type except base_unit
        """:type : list[ConvertUnit]"""
        self.repo = repo
        """:type : ConvertRepo"""
        self.name = name
        """:type : str"""
        self.decimals = 2
        """:type : int"""
        self.base_unit = None
        """:type : ConvertUnit"""

    def get_full_unit_list(self):
        """
        Returns the full list of ConvertUnit objects
        :rtype: list[ConvertUnit]
        """
        return [self.base_unit] + self.unit_list

    def add_unit(self, unit):
        """
        Adds a new ConvertUnit object to unit list
        :type unit: ConvertUnit
        """
        self.unit_list.append(unit)

    def remove_unit(self, unit):
        """
        Removes a ConvertUnit object to unit list
        :type unit: ConvertUnit
        """
        if unit in self.unit_list:
            self.unit_list.remove(unit)

    def get_unit_by_name(self, name):
        """
        Get a unit by a specified name or abbreviation
        :type name: str
        :rtype: ConvertUnit | None
        """
        full_unit_list = [self.base_unit] + self.unit_list
        for unit_obj in full_unit_list:
            if name in unit_obj.name_list:
                return unit_obj
        for unit_obj in full_unit_list:
            if name.lower() in [unit_name.lower() for unit_name in unit_obj.name_list]:
                return unit_obj
        for unit_obj in full_unit_list:
            if name in unit_obj.abbr_list:
                return unit_obj
        for unit_obj in full_unit_list:
            if name.lower() in [unit_name.lower() for unit_name in unit_obj.abbr_list]:
                return unit_obj
        return None

    @staticmethod
    def from_json(repo, json_obj):
        """
        Loads a new ConvertType from json dict
        :type repo: ConvertRepo
        :type json_obj: dict
        :rtype: ConvertType
        """
        name = json_obj["name"]
        new_type = ConvertType(repo, name)
        if "decimals" in json_obj:
            new_type.decimals = json_obj["decimals"]
        # Get base unit
        new_type.base_unit = ConvertUnit.from_json(new_type, json_obj["base_unit"])
        # Add unit elements
        for unit in json_obj["units"]:
            new_type.add_unit(ConvertUnit.from_json(new_type, unit))
        return new_type

    def to_json(self):
        """
        Outputs a conversion type in a dict, for serialisation into json
        :return: dict
        """
        json_obj = dict()
        json_obj["name"] = self.name
        json_obj["decimals"] = self.decimals
        json_obj["base_unit"] = self.base_unit.to_json()
        json_obj["units"] = []
        for unit in self.unit_list:
            json_obj["units"].append(unit.to_json())
        return json_obj


class ConvertUnit:
    """
    Conversion unit object.
    """

    def __init__(self, convert_type, names, value):
        """
        :param convert_type: Type this unit belongs to
        :type convert_type: ConvertType
        :param names: List of names for unit
        :type names: list
        :param value: Value of unit against base unit for type
        :type value: float
        """
        self.abbr_list = []
        """:type : list[str]"""
        self.type = convert_type
        """:type : ConvertType"""
        self.name_list = names
        """:type : list[str]"""
        self.value = value
        """:type : float"""
        self.offset = 0
        """:type : float"""
        self.last_updated_date = None
        """ :type : datetime.datetime"""
        self.valid_prefix_group = None
        """ :type : ConvertPrefixGroup"""

    def add_name(self, name):
        """
        Adds a name to the list of names for a unit.
        :type name: str
        """
        self.name_list.append(name)

    def remove_name(self, name):
        """
        Removes a name from the list of names for a unit.
        :type name: str
        """
        if name in self.name_list:
            self.name_list.remove(name)

    def add_abbr(self, abbreviation):
        """
        Adds an abbreviation to the list of abbreviations for a unit.
        :type abbreviation: str
        """
        self.abbr_list.append(abbreviation)

    def remove_abbr(self, abbreviation):
        """
        Removes an abbreviation from the list of abbreviations for a unit.
        :type abbreviation: str
        """
        if abbreviation in self.abbr_list:
            self.abbr_list.remove(abbreviation)

    def update_value(self, value):
        """
        Changes the value of the unit.
        :type value: float
        """
        self.last_updated_date = datetime.datetime.now()
        self.value = value

    def update_offset(self, offset):
        """
        Changes the offset of the unit.
        :type offset: float
        """
        self.last_updated_date = datetime.datetime.now()
        self.offset = offset

    def has_name(self, input_name):
        """
        Checks if a specified name is a valid name or abbreviation for this unit.
        :type input_name: str
        :rtype bool
        """
        if input_name.lower() in [name.lower() for name in self.name_list]:
            return True
        if input_name.lower() in [abbr.lower() for abbr in self.abbr_list]:
            return True
        return False

    def get_prefix_from_user_input(self, user_input):
        """
        Returns the _prefix_ matching the user inputted unit name.
        Note: Not the value!
        None if no prefix.
        False if the input does not match this unit at all.
        :param user_input: The user input
        :type user_input: str
        :rtype: ConvertPrefix | None | Bool
        """
        for name in self.name_list:
            # If {X} is in the name, it means prefix goes in the middle.
            if "{X}" in name:
                name_start = name.split("{X}")[0].lower()
                name_end = name.split("{X}")[1].lower()
                # Ensure that userinput starts with first half and ends with second half.
                if not user_input.lower().startswith(name_start) or not user_input.lower().endswith(name_end):
                    continue
                user_prefix = user_input[len(name_start):-len(name_end)]
                # If user prefix is blank, return None
                if user_prefix == "":
                    return None
                # If no prefix group is valid, accept blank string, reject anything else.
                if self.valid_prefix_group is None:
                    continue
                # Get the prefix in the group whose name matches the user input
                prefix_obj = self.valid_prefix_group.get_prefix_by_name(user_prefix)
                if prefix_obj is None:
                    continue
                return prefix_obj
            # So, {X} isn't in the name, so it's a standard name.
            if not user_input.lower().endswith(name.lower()):
                continue
            # Find out what the user said was the prefix
            user_prefix = user_input[:-len(name)]
            if user_prefix == "":
                return None
            # If no prefix group is valid and user didn't input a blank string, reject
            if self.valid_prefix_group is None:
                continue
            # Get group's prefix that matches name
            prefix_obj = self.valid_prefix_group.get_prefix_by_name(user_prefix)
            if prefix_obj is None:
                continue
            return prefix_obj
        # Do the same as above, but with abbreviations
        for abbreviation in self.abbr_list:
            # If {X} is in the abbreviation, it means prefix goes in the middle.
            if "{X}" in abbreviation:
                abbreviation_start = abbreviation.split("{X}")[0].lower()
                abbreviation_end = abbreviation.split("{X}")[1].lower()
                # Ensure that userinput starts with first half and ends with second half.
                if (not user_input.lower().startswith(abbreviation_start) or not user_input.lower().endswith(
                        abbreviation_end)):
                    continue
                user_prefix = user_input[len(abbreviation_start):-len(abbreviation_end)]
                # If user prefix is blank, return None
                if user_prefix == "":
                    return None
                # If no prefix group is valid, accept blank string, reject anything else.
                if self.valid_prefix_group is None:
                    continue
                # Get the prefix in the group whose abbreviation matches the user input
                prefix_obj = self.valid_prefix_group.get_prefix_by_abbr(user_prefix)
                if prefix_obj is None:
                    continue
                return prefix_obj
            # So, {X} isn't in the abbreviation, so it's a standard abbreviation.
            if not user_input.lower().endswith(abbreviation.lower()):
                continue
            # Find out what the user said was the prefix
            user_prefix = user_input[:-len(abbreviation)]
            if user_prefix == "":
                return None
            # If no prefix group is valid and user didn't input a blank string, reject
            if self.valid_prefix_group is None:
                continue
            # Get group's prefix that matches abbreviation
            prefix_obj = self.valid_prefix_group.get_prefix_by_abbr(user_prefix)
            if prefix_obj is None:
                continue
            return prefix_obj
        return False

    @staticmethod
    def from_json(convert_type, json_obj):
        """
        Loads a ConvertUnit object from json dict
        :type convert_type: ConvertType
        :type json_obj: dict
        :rtype: ConvertUnit
        """
        names = []
        for name in json_obj["names"]:
            names.append(name)
        value = json_obj["value"]
        new_unit = ConvertUnit(convert_type, names, value)
        if "abbrs" in json_obj:
            for abbr in json_obj["abbrs"]:
                new_unit.add_abbr(abbr)
        if "valid_prefix_group" in json_obj:
            prefix_group = convert_type.repo.get_prefix_group_by_name(json_obj["valid_prefix_group"])
            new_unit.valid_prefix_group = prefix_group
        if "offset" in json_obj:
            new_unit.offset = json_obj["offset"]
        if "last_updated" in json_obj:
            new_unit.last_updated_date = dateutil.parser.parse(json_obj["last_updated"])
        return new_unit

    def to_json(self):
        """
        Outputs a ConvertUnit as a dict which can be serialised into a json object
        :return: dict
        """
        json_obj = dict()
        json_obj["names"] = []
        for name in self.name_list:
            json_obj["names"].append(name)
        json_obj["value"] = self.value
        if len(self.abbr_list) != 0:
            json_obj["abbrs"] = []
            for abbr in self.abbr_list:
                json_obj["abbrs"].append(abbr)
        if self.offset != 0:
            json_obj["offset"] = self.offset
        if self.last_updated_date is not None:
            json_obj["last_updated"] = self.last_updated_date.isoformat()
        if self.valid_prefix_group is not None:
            json_obj["valid_prefix_group"] = self.valid_prefix_group.name
        return json_obj


class ConvertPrefixGroup:
    """
    Group of Conversion Prefixes.
    """

    def __init__(self, repo, name):
        """
        :type repo: ConvertRepo
        :type name: str
        """
        self.prefix_list = []
        """:type : list[ConvertPrefix]"""
        self.repo = repo
        """:type : ConvertRepo"""
        self.name = name
        """:type : str"""

    def add_prefix(self, prefix):
        """
        Adds a new prefix to the prefix list
        :type prefix: ConvertPrefix
        """
        self.prefix_list.append(prefix)

    def remove_prefix(self, prefix):
        """
        Removes a prefix from the prefix list
        :type prefix: ConvertPrefix
        """
        if prefix in self.prefix_list:
            self.prefix_list.remove(prefix)

    def get_prefix_by_name(self, name):
        """
        Gets the prefix with the specified name
        :type name: str
        :rtype: ConvertPrefix | None
        """
        for prefix_obj in self.prefix_list:
            if prefix_obj.prefix == name:
                return prefix_obj
        for prefix_obj in self.prefix_list:
            if prefix_obj.prefix.lower() == name.lower():
                return prefix_obj
        return None

    def get_prefix_by_abbr(self, abbreviation):
        """
        Gets the prefix with the specified abbreviation
        :type abbreviation: str
        :rtype: ConvertPrefix | None
        """
        for prefix_obj in self.prefix_list:
            if prefix_obj.abbreviation == abbreviation:
                return prefix_obj
        for prefix_obj in self.prefix_list:
            if prefix_obj.abbreviation.lower() == abbreviation.lower():
                return prefix_obj
        return None

    def get_appropriate_prefix(self, value):
        """
        :type value: float
        :rtype: ConvertPrefix | None
        """
        multiplier_bigger_than_one = True
        for prefix_obj in sorted(self.prefix_list, key=lambda x: x.multiplier, reverse=True):
            multiplier = prefix_obj.multiplier
            if multiplier_bigger_than_one and multiplier < 1:
                multiplier_bigger_than_one = False
                if value > 1:
                    return None
            after_prefix = value / prefix_obj.multiplier
            if after_prefix > 1:
                return prefix_obj
        return None

    @staticmethod
    def from_json(repo, json_obj):
        """
        Loads a new ConvertPrefixGroup from json dict
        :type repo: ConvertRepo
        :type json_obj: dict
        :rtype: ConvertPrefixGroup
        """
        name = json_obj["name"]
        new_group = ConvertPrefixGroup(repo, name)
        for prefix in json_obj["prefixes"]:
            new_group.add_prefix(ConvertPrefix.from_json(new_group, prefix))
        return new_group

    def to_json(self):
        """
        Outputs a ConvertPrefixGroup as a dict ready to be turned into json
        :return: dict
        """
        json_obj = dict()
        json_obj["name"] = self.name
        json_obj["prefixes"] = []
        for prefix in self.prefix_list:
            json_obj["prefixes"].append(prefix.to_json())
        return json_obj


class ConvertPrefix:
    """
    Conversion prefix.
    """

    def __init__(self, prefix_group, prefix, abbreviation, multiplier):
        """
        :type prefix_group: ConvertPrefixGroup
        :type prefix: str
        :type abbreviation: str
        :type multiplier: float
        """
        self.prefix_group = prefix_group
        self.prefix = prefix
        self.abbreviation = abbreviation
        self.multiplier = multiplier

    @staticmethod
    def from_json(prefix_group, json_obj):
        """
        Loads a new ConvertPrefix object from json dict
        :type prefix_group: ConvertPrefixGroup
        :type json_obj: dict
        :rtype: ConvertPrefix
        """
        name = json_obj["name"]
        abbr = json_obj["abbr"]
        value = json_obj["value"]
        new_prefix = ConvertPrefix(prefix_group, name, abbr, value)
        return new_prefix

    def to_json(self):
        """
        Outputs a ConvertPrefix in a dict for serialisation to json
        :return: dict
        """
        json_obj = dict()
        json_obj["name"] = self.prefix
        json_obj["abbr"] = self.abbreviation
        json_obj["value"] = self.multiplier
        return json_obj


class ConvertMeasure:
    """
    Convert measure object. An amount with a unit.
    """

    def __init__(self, amount, unit):
        """
        :type amount: float
        :type unit: ConvertUnit
        """
        self.amount = amount
        self.unit = unit

    def is_equal(self, other_measure):
        """
        Returns boolean, whether this Measure is equal to another.
        :type other_measure: ConvertMeasure
        :rtype: bool
        """
        return (self.unit == other_measure.unit) and (self.amount == other_measure.amount)

    def convert_to(self, unit):
        """
        Creates a new measure, equal in value but with a different unit.
        :param unit: The conversion unit to convert to
        :type unit: ConvertUnit
        :rtype: ConvertMeasure
        """
        # Check units are the same type
        if self.unit.type != unit.type:
            raise ConvertException("These are not the same unit type.")
        # Convert to base unit
        new_amount = self.amount * self.unit.value
        base_offset = self.unit.offset
        if base_offset is not None:
            new_amount += base_offset
        # Convert from base unit to new unit
        unit_offset = unit.offset
        if base_offset is not None:
            new_amount -= unit_offset
        new_amount /= unit.value
        new_measure = ConvertMeasure(new_amount, unit)
        return new_measure

    def convert_to_base(self):
        """
        Creates a new measure, equal in value, but with the base unit of the unit type.
        :rtype: ConvertMeasure
        """
        base_unit = self.unit.type.base_unit
        unit_value = self.unit.value
        new_amount = self.amount * unit_value
        offset = self.unit.offset
        if offset is not None:
            new_amount += offset
        new_measure = ConvertMeasure(new_amount, base_unit)
        return new_measure

    def to_string(self):
        """
        Converts the measure to a string for output.
        :rtype: str
        """
        prefix_group = self.unit.valid_prefix_group
        # If there is no prefix group, output raw.
        if prefix_group is None:
            return self.to_string_with_prefix(None)
        # Ask the prefix group for the most appropriate prefix for the value.
        appropriate_prefix = prefix_group.get_appropriate_prefix(self.amount)
        return self.to_string_with_prefix(appropriate_prefix)

    def __str__(self):
        return self.to_string()

    def to_string_with_prefix(self, prefix):
        """
        Converts the measure to a string with the specified prefix.
        :type prefix: ConvertPrefix | None
        :rtype: str
        """
        decimal_places = self.unit.type.decimals
        decimal_format = "{:." + str(decimal_places) + "f}"
        # Calculate the output amount
        prefix_multiplier = 1
        prefix_name = ""
        if prefix is not None:
            prefix_name = prefix.prefix
            prefix_multiplier = prefix.multiplier
        output_amount = self.amount / prefix_multiplier
        # Output string
        return decimal_format.format(output_amount) + " " + prefix_name + self.unit.name_list[0]

    @staticmethod
    def build_list_from_user_input(repo, user_input):
        """
        Creates a new measure from a user inputted line
        :type repo: ConvertRepo
        :type user_input: str
        :rtype: list[ConvertMeasure]
        """
        user_input_clean = user_input.strip()
        # Search through the line for digits, pull them amount as a preliminary amount and strip the rest of the line.
        # TODO: add calculation?
        preliminary_amount_str = Commons.get_digits_from_start_or_end(user_input_clean)
        if preliminary_amount_str is None:
            raise ConvertException("Cannot find amount.")
        preliminary_amount_value = float(preliminary_amount_str)
        # Remove amountString from userInput
        if user_input.startswith(preliminary_amount_str):
            user_input = user_input[len(preliminary_amount_str):]
        else:
            user_input = user_input[:-len(preliminary_amount_str)]
        # Loop all units, see which might match userInput with prefixes. Building a list of valid measures for input.
        new_measure_list = []
        for unit_obj in repo.get_full_unit_list():
            prefix_obj = unit_obj.get_prefix_from_user_input(user_input)
            if prefix_obj is False:
                continue
            prefix_multiplier = 1
            if prefix_obj is not None:
                prefix_multiplier = prefix_obj.multiplier
            new_amount = preliminary_amount_value * prefix_multiplier
            new_measure = ConvertMeasure(new_amount, unit_obj)
            new_measure_list.append(new_measure)
        # If list is still empty, throw an exception.
        if len(new_measure_list) == 0:
            raise ConvertException("Unrecognised unit.")
        # Return list of matching measures.
        return new_measure_list


class Convert(Function):
    """
    Function to convert units from one to another
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert"
        # Names which can be used to address the Function
        self.names = {"convert", "conversion"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "converts values from one unit to another. Format: convert <value> <old unit> to <new unit>"
        self.convert_repo = ConvertRepo.load_json()
        """ :type : ConvertRepo"""

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return Convert()

    def save_function(self):
        """Saves the function, persistent functions only."""
        self.convert_repo.save_json()

    def run(self, event):
        return event.create_response(self.convert_parse(event.command_args))

    def convert_parse(self, line, passive=False):
        """
        :type line: str
        :type passive: bool
        :rtype: str | None
        """
        # Create regex to find the place to split a user string.
        split_regex = re.compile(r' into | to |->| in ', re.IGNORECASE)
        # See if the input needs splitting.
        if split_regex.search(line) is None:
            try:
                from_measure_list = ConvertMeasure.build_list_from_user_input(self.convert_repo, line)
                return self.convert_one_unit(from_measure_list, passive)
            except Exception as e:
                if passive:
                    return None
                return "I don't understand your input. ({}) Please format like so: " \
                       "convert <value> <old unit> to <new unit>".format(e)
        # Split input
        line_split = split_regex.split(line)
        # If there are more than 2 parts, be confused.
        if len(line_split) > 2:
            if passive:
                return None
            return "I don't understand your input. (Are you specifying 3 units?) Please format like so: " \
                   "convert <value> <old unit> to <new unit>"
        # Try loading the first part as a measure
        try:
            from_measure_list = ConvertMeasure.build_list_from_user_input(self.convert_repo, line_split[0])
            return self.convert_two_unit(from_measure_list, line_split[1], passive)
        except ConvertException:
            # Try loading the second part as a measure
            try:
                from_measure_list = ConvertMeasure.build_list_from_user_input(self.convert_repo, line_split[1])
                return self.convert_two_unit(from_measure_list, line_split[0], passive)
            except ConvertException as e:
                # If both fail, send an error message
                if passive:
                    return None
                return "I don't understand your input. ({}) Please format like so: " \
                       "convert <value> <old unit> to <new unit>".format(e)

    def convert_one_unit(self, from_measure_list, passive):
        """
        Converts a single given measure into whatever base unit of the type the measure is.
        :type from_measure_list: list[ConvertMeasure]
        :type passive: bool
        :rtype: str | None
        """
        output_lines = []
        for from_measure in from_measure_list:
            to_measure = from_measure.convert_to_base()
            if from_measure.is_equal(to_measure):
                continue
            output_lines.append(self.output_line(from_measure, to_measure))
        if len(output_lines) == 0:
            if passive:
                return None
            return "I don't understand your input. (No units specified.) Please format like so: " \
                   "convert <value> <old unit> to <new unit>"
        return "\n".join(output_lines)

    def convert_two_unit(self, from_measure_list, user_input_to, passive):
        """
        Converts a single given measure into whatever unit is specified.
        :type from_measure_list: list[ConvertMeasure]
        :type user_input_to: str
        :type passive: bool
        :rtype: str | None
        """
        output_lines = []
        for from_measure in from_measure_list:
            for to_unit_obj in from_measure.unit.type.get_full_unit_list():
                prefix_obj = to_unit_obj.get_prefix_from_user_input(user_input_to)
                if prefix_obj is False:
                    continue
                to_measure = from_measure.convert_to(to_unit_obj)
                output_lines.append(self.output_line_with_to_prefix(from_measure, to_measure, prefix_obj))
        if len(output_lines) == 0:
            if passive:
                return None
            return "I don't understand your input. (No units specified or found.) Please format like so: " \
                   "convert <value> <old unit> to <new unit>"
        return "\n".join(output_lines)

    def output_line(self, from_measure, to_measure):
        """
        Creates a line to output for the equality of a fromMeasure and toMeasure.
        :type from_measure: ConvertMeasure
        :type to_measure: ConvertMeasure
        :rtype: str
        """
        last_update = to_measure.unit.last_updated_date or from_measure.unit.last_updated_date
        output_string = "{} = {}.".format(from_measure.to_string(), to_measure.to_string())
        if last_update is not None:
            output_string += " (Last updated: {})".format(last_update.strftime('%Y-%m-%d %H:%M:%S'))
        return output_string

    def output_line_with_to_prefix(self, from_measure, to_measure, to_prefix):
        """
        Creates a line to output for the equality of a fromMeasure and toMeasure,
        with a specified prefix for the toMeasure.
        :type from_measure: ConvertMeasure
        :type to_measure: ConvertMeasure
        :type to_prefix: ConvertPrefix
        :rtype: str
        """
        last_update = to_measure.unit.last_updated_date or from_measure.unit.last_updated_date
        output_string = "{} = {}.".format(from_measure.to_string(), to_measure.to_string_with_prefix(to_prefix))
        if last_update is not None:
            output_string += " (Last updated: {})".format(last_update.strftime('%Y-%m-%d %H:%M:%S'))
        return output_string

    def get_passive_events(self):
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        if not isinstance(event, EventMessage):
            return
        return self.convert_parse(event.text, True)


class UpdateCurrencies(Function):
    """
    Updates all currencies in the ConvertRepo
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "update currencies"
        # Names which can be used to address the Function
        self.names = {"update currencies", "convert update currencies", "currency update", "update currency",
                      "currencies update"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Update currency conversion figures, using data from the money converter, the European " \
                         "central bank, forex and preev."

    def run(self, event):
        # Get convert repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Update all sources
        output_lines = self.update_all(repo)
        # Return output
        return event.create_response("\n".join(output_lines))

    def get_passive_events(self):
        return {EventHour}

    def passive_run(self, event, hallo_obj):
        # Get convert repo
        function_dispatcher = hallo_obj.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Update all sources
        output_lines = self.update_all(repo)
        for line in output_lines:
            print(line)
        return None

    def update_all(self, repo):
        output_lines = []
        # Update with the European Bank
        try:
            output_lines.append(self.update_from_european_bank_data(repo) or
                                "Updated currency data from the European Central Bank.")
        except Exception as e:
            output_lines.append("Failed to update European Central Bank data. {}".format(e))
        # Update with Forex
        try:
            output_lines.append(self.update_from_forex_data(repo) or
                                "Updated currency data from Forex.")
        except Exception as e:
            output_lines.append("Failed to update Forex data. {}".format(e))
        # Update with Preev
        try:
            output_lines.append(self.update_from_cryptonator_data(repo) or
                                "Updated currency data from Cryptonator.")
        except Exception as e:
            output_lines.append("Failed to update Cryptonator data. {}".format(e))
        # Save repo
        repo.save_json()
        return output_lines

    def update_from_european_bank_data(self, repo):
        """
        Updates the value of conversion currency units using The European Bank data.
        :type repo: ConvertRepo
        """
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from european bank website
        url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        xml_string = Commons.load_url_string(url)
        # Parse data
        doc = minidom.parseString(xml_string)
        root = doc.getElementsByTagName("gesmes:Envelope")[0]
        cube_one_elem = root.getElementsByTagName("Cube")[0]
        cube_two_elem = cube_one_elem.getElementsByTagName("Cube")[0]
        for cube_three_elem in cube_two_elem.getElementsByTagName("Cube"):
            # Get currency code from currency Attribute
            currency_code = cube_three_elem.getAttributeNode("currency").nodeValue
            # Get value from rate attribute and get reciprocal.
            currency_value = 1 / float(cube_three_elem.getAttributeNode("rate").nodeValue)
            # Get currency unit
            currency_unit = currency_type.get_unit_by_name(currency_code)
            # If unrecognised currency, SKIP
            if currency_unit is None:
                continue
            # Set Value
            currency_unit.update_value(currency_value)

    def update_from_forex_data(self, repo):
        """
        Updates the value of conversion currency units using Forex data.
        :type repo: ConvertRepo
        """
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from forex website
        url = 'https://rates.fxcm.com/RatesXML3'
        xml_string = Commons.load_url_string(url)
        # Parse data
        doc = minidom.parseString(xml_string)
        rates_elem = doc.getElementsByTagName("Rates")[0]
        for rate_elem in rates_elem.getElementsByTagName("Rate"):
            # Get data from element
            symbol_data = rate_elem.getElementsByTagName("Symbol")[0].firstChild.data
            if not symbol_data.startswith("EUR"):
                continue
            bid_data = float(rate_elem.getElementsByTagName("Bid")[0].firstChild.data)
            ask_data = float(rate_elem.getElementsByTagName("Ask")[0].firstChild.data)
            # Get currency code and value from data
            currency_code = symbol_data[3:]
            currency_value = 1 / (0.5 * (bid_data + ask_data))
            # Get currency unit
            currency_unit = currency_type.get_unit_by_name(currency_code)
            # If unrecognised code, skip
            if currency_unit is None:
                continue
            # Set Value
            currency_unit.update_value(currency_value)

    def update_from_cryptonator_data(self, repo):
        """
        Updates the value of conversion cryptocurrencies using cryptonator data.
        :type repo: ConvertRepo
        """
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull json data from preev website, combine into 1 dict
        currency_codes = ["LTC", "BTC", "BCH", "DOGE", "XMR", "ETH", "ETC", "DASH"]
        for code in currency_codes:
            # Get data
            data = Commons.load_url_json("https://api.cryptonator.com/api/ticker/{}-eur".format(code))
            # Get the ConvertUnit object for the currency reference
            currency_unit = currency_type.get_unit_by_name(code)
            if currency_unit is None:
                continue
            # Update the value
            currency_unit.update_value(data["ticker"]["price"])


class ConvertViewRepo(Function):
    """
    Lists types, units, names, whatever.
    """

    NAMES_TYPE = ["type", "t"]
    NAMES_UNIT = ["unit", "u"]
    NAMES_PREFIXGROUP = ["prefixgroup", "prefix_group", "prefix-group", "group", "g", "pg"]
    NAMES_PREFIX = ["prefix", "p"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert view repo"
        # Names which can be used to address the Function
        self.names = {"convert view repo", "convert view", "convert list"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns information about the conversion repository."

    def run(self, event):
        # Load repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Check if type is specified
        if Commons.find_any_parameter(self.NAMES_TYPE, event.command_args):
            # Get type name and object
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, event.command_args)
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Unrecognised type.")
            # Check if unit & type are specified
            if Commons.find_any_parameter(self.NAMES_UNIT, event.command_args):
                # Get unit name and object
                unit_name = Commons.find_any_parameter(self.NAMES_UNIT, event.command_args)
                unit_obj = type_obj.get_unit_by_name(unit_name)
                if unit_obj is None:
                    return event.create_response("Unrecognised unit.")
                return event.create_response(self.output_unit_as_string(unit_obj))
            # Type is defined, but not unit.
            return event.create_response(self.output_type_as_string(type_obj))
        # Check if prefix group is specified
        if Commons.find_any_parameter(self.NAMES_PREFIXGROUP, event.command_args):
            # Check if prefix & group are specified
            prefix_group_name = Commons.find_any_parameter(self.NAMES_PREFIXGROUP, event.command_args)
            prefix_group_obj = repo.get_prefix_group_by_name(prefix_group_name)
            if prefix_group_obj is None:
                return event.create_response("Unrecognised prefix group.")
            # Check if prefix group & prefix are specified
            if Commons.find_any_parameter(self.NAMES_PREFIX, event.command_args):
                # Get prefix name and object
                prefix_name = Commons.find_any_parameter(self.NAMES_PREFIX, event.command_args)
                prefix_obj = prefix_group_obj.get_prefix_by_name(
                    prefix_name) or prefix_group_obj.get_prefix_by_abbr(prefix_name)
                if prefix_group_obj is None:
                    return event.create_response("Unrecognised prefix.")
                return event.create_response(self.output_prefix_as_string(prefix_obj))
            # Prefix group is defined, but not prefix
            return event.create_response(self.output_prefix_group_as_string(prefix_group_obj))
        # Check if unit is specified
        if Commons.find_any_parameter(self.NAMES_UNIT, event.command_args):
            unit_name = Commons.find_any_parameter(self.NAMES_UNIT, event.command_args)
            output_lines = []
            # Loop through types, getting units for each type
            for type_obj in repo.type_list:
                unit_obj = type_obj.get_unit_by_name(unit_name)
                # If unit exists by that name, add the string format to output list
                if unit_obj is not None:
                    output_lines.append(self.output_unit_as_string(unit_obj))
            if len(output_lines) == 0:
                return event.create_response("Unrecognised unit.")
            return event.create_response("\n".join(output_lines))
        # Check if prefix is specified
        if Commons.find_any_parameter(self.NAMES_PREFIX, event.command_args):
            prefix_name = Commons.find_any_parameter(self.NAMES_PREFIX, event.command_args)
            output_lines = []
            # Loop through groups, getting prefixes for each group
            for prefix_group_obj in repo.prefix_group_list:
                prefix_obj = prefix_group_obj.get_prefix_by_name(prefix_name)
                # If prefix exists by that name, add the string format to output list
                if prefix_obj is not None:
                    output_lines.append(self.output_prefix_as_string(prefix_obj))
            if len(output_lines) == 0:
                return event.create_response("Unrecognised prefix.")
            return event.create_response("\n".join(output_lines))
        # Nothing was specified, return info on the repo.
        return event.create_response(self.output_repo_as_string(repo))

    def output_repo_as_string(self, repo):
        """
        Outputs a Conversion Repository as a string
        :type repo: ConvertRepo
        :rtype: str
        """
        output_string = "Conversion Repo:\n"
        output_string += "Unit types: " + \
                         ", ".join([type_obj.name for type_obj in repo.type_list]) + \
                         "\n"
        output_string += "Prefix groups: " + ", ".join([type_obj.name for type_obj in repo.type_list])
        return output_string

    def output_type_as_string(self, type_obj):
        """
        Outputs a Conversion Type object as a string
        :type type_obj: ConvertType
        :rtype: str
        """
        unit_name_list = [unit_obj.name_list[0] for unit_obj in type_obj.get_full_unit_list() if
                          unit_obj != type_obj.base_unit]
        output_string = "Conversion Type: ({})\n".format(type_obj.name)
        output_string += "Decimals: {}\n".format(type_obj.decimals)
        output_string += "Base unit: {}\n".format(type_obj.base_unit.name_list[0])
        output_string += "Other units: {}".format(", ".join(unit_name_list))
        return output_string

    def output_unit_as_string(self, unit_obj):
        """
        Outputs a Conversion Unit object as a string
        :type unit_obj: ConvertUnit
        :rtype: str
        """
        output_lines = ["Conversion Unit: ({})".format(unit_obj.name_list[0]),
                        "Type: {}".format(unit_obj.type.name),
                        "Name list: {}".format(", ".join(unit_obj.name_list)),
                        "Abbreviation list: {}".format(", ".join(unit_obj.abbr_list)),
                        "Value: 1 {} - {} {}".format(unit_obj.name_list[0],
                                                     unit_obj.value,
                                                     unit_obj.type.base_unit.name_list[0]),
                        "Offset: 0 {} = {} {}".format(unit_obj.name_list[0],
                                                      unit_obj.offset,
                                                      unit_obj.type.base_unit.name_list[0])]
        last_update = unit_obj.last_updated_date
        if last_update is not None:
            output_lines.append("Last updated: " + last_update.strftime('%Y-%m-%d %H:%M:%S'))
        prefix_group_names = unit_obj.valid_prefix_group.name
        if prefix_group_names is not None:
            output_lines.append("Prefix group: " + prefix_group_names)
        return "\n".join(output_lines)

    def output_prefix_group_as_string(self, prefix_group_obj):
        """
        Outputs a Conversion PrefixGroup object as a string
        :type prefix_group_obj: ConvertPrefixGroup
        :rtype: str
        """
        prefix_list = [prefix_obj.prefix for prefix_obj in prefix_group_obj.prefix_list]
        output_string = "Prefix group: ({}\n".format(prefix_group_obj.name)
        output_string += "Prefix list: " + ", ".join(prefix_list)
        return output_string

    def output_prefix_as_string(self, prefix_obj):
        """
        Outputs a Conversion prefix object as a string
        :type prefix_obj: ConvertPrefix
        :rtype: str
        """
        output_string = "Prefix: ({})\n".format(prefix_obj.prefix)
        output_string += "Abbreviation: {}\n".format(prefix_obj.abbreviation)
        output_string += "Multiplier: {}".format(prefix_obj.prefix)
        return output_string


class ConvertSet(Function):
    """
    Function to set the value of a unit manually.
    Will create a new unit if no unit is found.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert set"
        # Names which can be used to address the Function
        self.names = {"convert set"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets the value of a unit, Format: <amount> <unit_set> = <amount>? <unit_reference>."

    def run(self, event):
        # Load Conversion Repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Create regex to find the place to split a user string.
        split_regex = re.compile(' into | to |->| in ', re.IGNORECASE)
        # Split input
        line_split = split_regex.split(event.command_args)
        # If there are more than 2 parts, be confused.
        if len(line_split) > 2:
            return event.create_response("I don't understand your input. (Are you specifying 3 units?) " +
                                         "Please format like so: convert <value> <old unit> to <new unit>")
        # Try loading the second part (reference measure) as a measure
        try:
            ref_measure_list = ConvertMeasure.build_list_from_user_input(repo, line_split[1])
        except ConvertException:
            try:
                ref_measure_list = ConvertMeasure.build_list_from_user_input(repo, "1" + line_split[1])
            except ConvertException:
                return event.create_response("I don't understand the second half of your input.")
        # Try loading the first part as a measure
        try:
            var_measure_list = ConvertMeasure.build_list_from_user_input(repo, line_split[0])
        except ConvertException:
            try:
                var_measure_list = ConvertMeasure.build_list_from_user_input(repo, "1" + line_split[0])
            except ConvertException:
                # Add a unit.
                return event.create_response(self.add_unit(line_split[0], ref_measure_list))
        return event.create_response(self.set_unit(var_measure_list, ref_measure_list))

    def set_unit(self, var_measure_list, ref_measure_list):
        """
        :type var_measure_list: list[ConvertMeasure]
        :type ref_measure_list: list[ConvertMeasure]
        :rtype: str
        """
        # Find list of pairs of measures, sharing a type
        measure_pair_list = []
        for var_measure in var_measure_list:
            var_measure_type = var_measure.unit.type
            for ref_measure in ref_measure_list:
                ref_measure_type = ref_measure.unit.type
                if var_measure_type == ref_measure_type:
                    measure_pair = {'var': var_measure, 'ref': ref_measure}
                    measure_pair_list.append(measure_pair)
        # Check lists have exactly 1 pair sharing a type
        if len(measure_pair_list) == 0:
            return "These units do not share the same type."
        if len(measure_pair_list) > 1:
            return "It is ambiguous which units you are referring to."
        # Get the correct var_measure and ref_measure and all associated required variables
        var_measure = measure_pair_list[0]['var']
        ref_measure = measure_pair_list[0]['ref']
        var_amount = var_measure.amount
        ref_amount = ref_measure.amount
        var_unit = var_measure.unit
        var_name = var_unit.name_list[0]
        base_name = var_unit.type.base_unit.name_list[0]
        ref_unit = ref_measure.unit
        var_value = var_unit.value
        ref_value = ref_unit.value
        var_offset = var_unit.offset
        ref_offset = ref_unit.offset
        # If var_unit is the base unit, it cannot be set.
        if var_unit == var_unit.type.base_unit:
            return "You cannot change values of the base unit."
        # If either given amount are zero, set the offset of var_unit.
        if var_amount == 0 or ref_amount == 0:
            # Calculate the new offset
            new_offset = (ref_amount - (var_amount * var_value)) * ref_value + ref_offset
            var_unit.update_offset(new_offset)
            # Save repo
            repo = var_unit.type.repo
            repo.save_json()
            # Output message
            return "Set new offset for {}: 0 {} = {} {}.".format(var_name, var_name, new_offset, base_name)
        # Get new value
        new_value = (ref_amount - ((var_offset - ref_offset) / ref_value)) / var_amount
        var_unit.update_value(new_value)
        # Save repo
        repo = var_unit.type.repo
        repo.save_json()
        # Output message
        return "Set new value for {}: Δ 1 {} = Δ {} {}.".format(var_name, var_name, new_value, base_name)

    def add_unit(self, user_input, ref_measure_list):
        """
        :type user_input: str
        :type ref_measure_list: list[ConvertMeasure]
        :rtype: str
        """
        # Check reference measure has exactly 1 unit option
        if len(ref_measure_list) == 0:
            return "There is no defined unit matching the reference name."
        if len(ref_measure_list) > 1:
            return "It is ambiguous which unit you are referring to."
        # Get unit type
        ref_measure = ref_measure_list[0]
        ref_amount = ref_measure.amount
        ref_unit = ref_measure.unit
        ref_type = ref_unit.type
        ref_value = ref_unit.value
        ref_offset = ref_unit.offset
        base_unit = ref_type.base_unit
        base_name = base_unit.name_list[0]
        # Get amount & unit name
        # TODO: accept calculation
        input_amount_string = Commons.get_digits_from_start_or_end(user_input)
        if input_amount_string is None:
            return "Please specify an amount when setting a new unit."
        input_amount_float = float(input_amount_string)
        # Remove amountString from userInput
        if user_input.startswith(input_amount_string):
            input_name = user_input[len(input_amount_string):]
        else:
            input_name = user_input[:-len(input_amount_string)]
        # Check name isn't already in use.
        if ref_type.get_unit_by_name(input_name) is not None:
            return "There's already a unit of that type by that name."
        # Add unit
        new_unit = ConvertUnit(ref_type, [input_name], 1)
        ref_type.add_unit(new_unit)
        # Update offset or value, based on what the user inputed.
        # If either given amount are zero, set the offset of varUnit.
        if input_amount_float == 0 or ref_amount == 0:
            # Calculate the new offset
            new_offset = (ref_amount - (input_amount_float * 1)) * ref_value + ref_offset
            new_unit.update_offset(new_offset)
            # Save repo
            repo = ref_unit.type.repo
            repo.save_json()
            # Output message
            return "Created new unit {} with offset: 0 {} = {} {}.".format(input_name,
                                                                           input_name,
                                                                           new_offset,
                                                                           base_name)
        # Get new value
        new_value = (ref_amount - ((0 - ref_offset) / ref_value)) / input_amount_float
        new_unit.update_value(new_value)
        # Save repo
        repo = ref_unit.type.repo
        repo.save_json()
        # Output message
        return "Created new unit {} with value: 1 {} = {} {}.".format(input_name, input_name, new_value, base_name)


class ConvertAddType(Function):
    """
    Adds a new conversion type.
    """

    NAMES_BASE_UNIT = ["base unit", "baseunit", "base_unit", "base-unit", "unit", "u", "b", "bu"]
    NAMES_DECIMALS = ["decimal places", "decimals", "decimal", "decimalplaces", "dp", "d"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert add type"
        # Names which can be used to address the Function
        self.names = {"convert add type"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new conversion unit type and base unit."

    def run(self, event):
        # Load repo, clean line
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Clean input
        line_clean = event.command_args.strip()
        parsed_input = ConvertInputParser(line_clean)
        # Check if base unit is defined
        unit_name = parsed_input.get_arg_by_names(self.NAMES_BASE_UNIT)
        # Check if decimal places is defined
        decimals = parsed_input.get_arg_by_names(self.NAMES_DECIMALS)
        decimals = int(decimals) if decimals is not None else None
        # Clean unit and type setting from the line to just get the name to remove
        input_name = parsed_input.remaining_text
        # Check that type name doesn't already exist.
        existing_type = repo.get_type_by_name(input_name)
        if existing_type is not None:
            return event.create_response("A type by this name already exists.")
        # Check base unit name was defined.
        if unit_name is None:
            return event.create_response("You must define a base unit for this type using unit=<unit name>.")
        # Create new type, Create new unit, set unit as base unit, set decimals
        new_type = ConvertType(repo, input_name)
        new_base_unit = ConvertUnit(new_type, [unit_name], 1)
        new_type.base_unit = new_base_unit
        if decimals is not None:
            new_type.decimals = decimals
        # add type to repo, save
        repo.add_type(new_type)
        repo.save_json()
        # Output message
        decimal_string = ""
        if decimals is not None:
            decimal_string = " and {} decimal places".format(decimals)
        output_string = "Created new type \"{}\" with base unit \"{}\"{}.".format(input_name, unit_name, decimal_string)
        return event.create_response(output_string)


class ConvertSetTypeDecimals(Function):
    """
    Sets the number of decimal places to show for a unit type.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert set type decimals"
        # Names which can be used to address the Function
        self.names = {"convert set type decimals", "convert set type decimal", "convert set decimals for type"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets the number of decimal places to show for a unit type."

    def run(self, event):
        # Load convert repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = ConvertInputParser(event.command_args)
        # If decimals is null, return error
        if len(parsed.number_words) == 0:
            return event.create_response("Please specify a conversion type and a number of decimal places " +
                                         "it should output.")
        # Convert decimals to integer
        decimals = int(parsed.number_words[0])
        # Get selected type
        input_type = repo.get_type_by_name(" ".join(parsed.string_words))
        # If type does not exist, return error
        if input_type is None:
            return event.create_response("This is not a recognised conversion type.")
        # Set decimals
        input_type.decimals = decimals
        # Save repo
        repo.save_json()
        # Output message
        return event.create_response("Set the number of decimal places to display for " +
                                     "\"{}\" type units at {} places.".format(input_type.name, decimals))


class ConvertRemoveUnit(Function):
    """
    Removes a specified unit from the conversion repo.
    """

    NAMES_TYPE = ["unit type", "type", "t"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert remove unit"
        # Names which can be used to address the Function
        self.names = {"convert remove unit", "convert delete unit", "convert unit remove", "convert unit delete"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a specified unit from the conversion repository."

    def run(self, event):
        # Load convert repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = ConvertInputParser(event.command_args)
        # Check if a type is specified
        type_name = parsed.get_arg_by_names(self.NAMES_TYPE)
        # Clean type setting from the line to just get the name to remove
        input_name = parsed.remaining_text
        # Find unit
        if type_name is not None:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("This conversion type is not recognised.")
            input_unit = type_obj.get_unit_by_name(input_name)
            if input_unit is None:
                return event.create_response("This unit name is not recognised for that unit type.")
        else:
            input_unit_list = []
            for type_obj in repo.type_list:
                input_unit = type_obj.get_unit_by_name(input_name)
                if input_unit is not None:
                    input_unit_list.append(input_unit)
            # Check if results are 0
            if len(input_unit_list) == 0:
                return event.create_response("No unit by that name is found in any type.")
            # Check if results are >=2
            if len(input_unit_list) >= 2:
                unit_outputs = []
                for input_unit in input_unit_list:
                    unit_outputs.append("{} (type={})".format(input_unit.name_list[0], input_unit.type.name))
                return event.create_response("There is more than one unit matching this name: {}"
                                             .format(", ".join(unit_outputs)))
            input_unit = input_unit_list[0]
        # Ensure it is not a base unit for its type
        if input_unit == input_unit.type.base_unit:
            return event.create_response("You cannot remove the base unit for a unit type.")
        # Remove unit
        input_unit_name = input_unit.name_list[0]
        input_unit.type.remove_unit(input_unit)
        # Done
        return event.create_response("Removed unit \"{}\" from conversion repository.".format(input_unit_name))


class ConvertUnitAddName(Function):
    """
    Adds a new name to a unit.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]
    NAMES_NEW = ["new name", "new", "new_name"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert unit add name"
        # Names which can be used to address the Function
        self.names = {"convert unit add name", "convert unit add new name"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new name to a unit."

    def run(self, event):
        # Load repository
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = ConvertInputParser(event.command_args)
        # Check for type=
        type_name = parsed.get_arg_by_names(self.NAMES_TYPE)
        # Check for unit=
        unit_name = parsed.get_arg_by_names(self.NAMES_UNIT)
        # Check for new name=
        new_name = parsed.get_arg_by_names(self.NAMES_NEW)
        # If unit= or new name= then remaining is the other one
        if unit_name is None and new_name is not None:
            unit_name = parsed.remaining_text
        if new_name is None and unit_name is not None:
            new_name = parsed.remaining_text
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Unrecognised type.")
            unit_list = type_obj.get_full_unit_list()
        # If no unit=, try splitting the line to find where the old name ends and new name begins
        input_unit_list = []
        if unit_name is None and new_name is None:
            # Start splitting from shortest left-string to longest.
            line_split = parsed.remaining_text.split()
            if len(line_split) == 1:
                return event.create_response("You must specify both a unit name and a new name to add.")
            input_sections = [[" ".join(line_split[:x+1]),
                               " ".join(line_split[x+1:])]
                              for x in range(len(line_split)-1)]
            new_options = []
            for input_pair in input_sections:
                # Check if the first input of the pair matches any units
                found_new = False
                for unit_obj in unit_list:
                    if unit_obj.has_name(input_pair[0]):
                        input_unit_list.append(unit_obj)
                        found_new = True
                if found_new:
                    new_options.append(input_pair[1])
                # Then check if the second input of the pair matches any units
                found_new = False
                for unit_obj in unit_list:
                    if unit_obj.has_name(input_pair[1]):
                        input_unit_list.append(unit_obj)
                        found_new = True
                if found_new:
                    new_options.append(input_pair[0])
            if len(new_options) != 1:
                return event.create_response("Could not parse where unit name ends and new name begins. "
                                             "Please specify with unit=<name> new_name=<name>")
            new_name = new_options[0]
        else:
            for unit_obj in unit_list:
                if unit_obj.has_name(unit_name):
                    input_unit_list.append(unit_obj)
        # If 0 units found, throw error
        if len(input_unit_list) == 0:
            return event.create_response("No unit found by that name.")
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return event.create_response("Unit name is too ambiguous, please specify with unit=<name> and type=<name>.")
        unit_obj = input_unit_list[0]
        # If new name is empty, throw error
        if len(new_name) == 0:
            return event.create_response("New name cannot be blank.")
        # Add the new name
        unit_obj.add_name(new_name)
        # Save repo
        repo.save_json()
        # Output message
        return event.create_response("Added \"{}\" as a new name for the \"{}\" unit.".format(new_name,
                                                                                              unit_obj.name_list[0]))


class ConvertUnitAddAbbreviation(Function):
    """
    Adds a new abbreviation to a unit.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]
    NAMES_ABBR = ["abbreviation", "abbr", "a"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert unit add abbreviation"
        # Names which can be used to address the Function
        self.names = {"convert unit add abbreviation", "convert unit add abbr"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new abbreviation to a unit."

    def run(self, event):
        # Load repository
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = ConvertInputParser(event.command_args)
        # Check for type=
        type_name = parsed.get_arg_by_names(self.NAMES_TYPE)
        # Check for unit=
        unit_name = parsed.get_arg_by_names(self.NAMES_UNIT)
        # Check for abbr=
        abbr_name = parsed.get_arg_by_names(self.NAMES_ABBR)
        # If unit= or abbr= then remaining is the other one.
        if unit_name is None and abbr_name is not None:
            unit_name = parsed.remaining_text
        if abbr_name is None and unit_name is not None:
            abbr_name = parsed.remaining_text
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Unrecognised type.")
            unit_list = type_obj.get_full_unit_list()
        # If no unit=, try splitting the line to find where the old name ends and new name begins
        input_unit_list = []
        if unit_name is None and abbr_name is None:
            # Start splitting from shortest left-string to longest.
            line_split = parsed.remaining_text.split()
            if len(line_split) == 1:
                return event.create_response("You must specify both a unit name and an abbreviation to add.")
            input_sections = [[" ".join(line_split[:x+1]),
                               " ".join(line_split[x+1:])]
                              for x in range(len(line_split)-1)]
            abbr_options = []
            for input_pair in input_sections:
                # Check if the first input of the pair matches any units
                found_abbr = False
                for unit_obj in unit_list:
                    if unit_obj.has_name(input_pair[0]):
                        input_unit_list.append(unit_obj)
                        found_abbr = True
                if found_abbr:
                    abbr_options.append(input_pair[1])
                # Then check if the second input of the pair matches any units
                found_abbr = False
                for unit_obj in unit_list:
                    if unit_obj.has_name(input_pair[1]):
                        input_unit_list.append(unit_obj)
                        found_abbr = True
                if found_abbr:
                    abbr_options.append(input_pair[0])
            if len(abbr_options) != 1:
                return event.create_response("Could not parse where unit name ends and abbreviation begins. "
                                             "Please specify with unit=<name>")
            abbr_name = abbr_options[0]
        else:
            for unit_obj in unit_list:
                if unit_obj.has_name(unit_name):
                    input_unit_list.append(unit_obj)
        # If 0 units found, throw error
        if len(input_unit_list) == 0:
            return event.create_response("No unit found by that name.")
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return event.create_response("Unit name is too ambiguous, please specify with unit=<name> and type=<name>.")
        unit_obj = input_unit_list[0]
        # If abbreviation name is empty, throw error
        if len(abbr_name) == 0:
            return event.create_response("Abbreviation name cannot be blank.")
        # Add the new name
        unit_obj.add_abbr(abbr_name)
        # Save repo
        repo.save_json()
        # Output message
        return event.create_response("Added \"{}\" as a new abbreviation for "
                                     "the \"{}\" unit.".format(abbr_name, unit_obj.name_list[0]))


class ConvertUnitRemoveName(Function):
    """
    Removes a name or abbreviation from a unit, unless it's the last name.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]
    NAMES_DEL = ["delete name", "remove name", "del", "delete", "remove"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert unit remove name"
        # Names which can be used to address the Function
        self.names = {"convert unit remove name", "convert unit delete name", "convert unit remove abbreviation",
                      "convert unit delete abbreviation", "convert unit remove abbr", "convert unit delete abbr",
                      "convert remove unit name", "convert delete unit name", "convert remove unit abbreviation",
                      "convert delete unit abbreviation", "convert remove unit abbr", "convert delete unit abbr"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a name or abbreviation from a unit, unless it's the last name."

    def run(self, event):
        # Load repo, clean line
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = ConvertInputParser(event.command_args)
        # Check if unit is defined
        unit_name = parsed.get_arg_by_names(self.NAMES_UNIT)
        # Check if type is defined
        type_obj = None
        type_name = parsed.get_arg_by_names(self.NAMES_TYPE)
        if type_name is not None:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Invalid type specified.")
        # Check if delete name is specified
        del_name = parsed.get_arg_by_names(self.NAMES_DEL)
        if del_name is None:
            del_name = parsed.remaining_text
        # Check if description is sufficient to narrow it to 1 and only 1 unit
        unit_list = repo.get_full_unit_list() if type_obj is None else type_obj.get_full_unit_list()
        user_unit_options = []
        for unit_obj in unit_list:
            # if unit name is defined and not a valid name for the unit, skip it.
            if unit_name is not None and not unit_obj.has_name(unit_name):
                continue
            # If input_name is not a valid name for the unit, skip it.
            if not unit_obj.has_name(del_name):
                continue
            # Otherwise it's the one, add it to the list
            user_unit_options.append(unit_obj)
        # Check if that narrowed it down correctly.
        if len(user_unit_options) == 0:
            return event.create_response("There are no units matching that description.")
        if len(user_unit_options) >= 2:
            return event.create_response("It is ambiguous which unit you refer to.")
        # Check this unit has other names.
        user_unit = user_unit_options[0]
        if len(user_unit.name_list) == 1:
            return event.create_response("This unit only has 1 name, you cannot remove its last name.")
        # Remove name
        user_unit.remove_name(del_name)
        # Save repo
        repo.save_json()
        # Output
        return event.create_response("Removed name \"{}\" from \"{}\" unit.".format(del_name, user_unit.name_list[0]))


class ConvertUnitSetPrefixGroup(Function):
    """
    Sets the prefix group for a unit.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]
    NAMES_PREFIX_GROUP = ["prefixgroup", "prefix_group", "prefix-group", "group", "g", "pg"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert set prefix group"
        # Names which can be used to address the Function
        self.names = {"convert set prefix group", "convert prefix group"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a name or abbreviation from a unit, unless it's the last name."

    def run(self, event):
        # Load repository
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(convert_function)  # type: Convert
        repo = convert_function_obj.convert_repo
        # Check for type=
        type_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, event.command_args):
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, event.command_args)
        # Check for unit=
        unit_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, event.command_args):
            unit_name = Commons.find_any_parameter(self.NAMES_TYPE, event.command_args)
        # Check for prefixgroup=
        prefix_group_name = None
        if Commons.find_any_parameter(self.NAMES_PREFIX_GROUP, event.command_args):
            prefix_group_name = Commons.find_any_parameter(self.NAMES_PREFIX_GROUP, event.command_args)
        # clean up the line
        param_regex = re.compile(r"(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        input_name = param_regex.sub("\1\4", event.command_args).strip()
        # Get prefix group
        if prefix_group_name is None:
            line_split = input_name.split()
            if repo.get_prefix_group_by_name(line_split[0]) is not None:
                prefix_group = repo.get_prefix_group_by_name(line_split[0])
                input_name = ' '.join(line_split[1:])
            elif repo.get_prefix_group_by_name(line_split[-1]) is not None:
                prefix_group = repo.get_prefix_group_by_name(line_split[-1])
                input_name = ' '.join(line_split[:-1])
            elif line_split[0].lower() == "none":
                prefix_group = None
                input_name = ' '.join(line_split[1:])
            elif line_split[-1].lower() == "none":
                prefix_group = None
                input_name = ' '.join(line_split[1:])
            else:
                return event.create_response("Prefix group not recognised.")
        else:
            prefix_group = repo.get_prefix_group_by_name(prefix_group_name)
            if prefix_group is None and prefix_group_name.lower() != "none":
                return event.create_response("Prefix group not recognised.")
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Unrecognised type.")
            unit_list = type_obj.get_full_unit_list()
        # If no unit=, try splitting the line to find where the old name ends and new name begins
        if unit_name is None:
            input_unit_list = []
            for unit_obj in unit_list:
                if unit_obj.has_name(input_name):
                    input_unit_list.append(unit_obj)
        else:
            input_unit_list = []
            for unit_obj in unit_list:
                if unit_obj.has_name(unit_name):
                    input_unit_list.append(unit_obj)
        # If 0 units found, throw error
        if len(input_unit_list) == 0:
            return event.create_response("No unit found by that name.")
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return event.create_response("Unit name is too ambiguous, please specify with unit= and type= .")
        unit_obj = input_unit_list[0]
        # Set the prefix group
        unit_obj.valid_prefix_group = prefix_group
        # Save repo
        repo.save_json()
        # Output message
        if prefix_group is None:
            prefix_group_name = "none"
        else:
            prefix_group_name = prefix_group.name
        return event.create_response("Set \"{}\" as the prefix group for " +
                                     "the \"{}\" unit.".format(prefix_group_name, unit_obj.name_list[0]))
