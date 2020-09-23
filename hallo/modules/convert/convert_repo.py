import datetime
import json
import logging

import dateutil.parser

from hallo.inc.commons import Commons

logger = logging.getLogger(__name__)


class ConvertException(Exception):
    pass


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
            new_repo.add_prefix_group(
                ConvertPrefixGroup.from_json(new_repo, prefix_group)
            )
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
        self.value = value  # A change of 1 of this unit, is equal to a change of how many units of base type.
        """:type : float"""
        self.offset = 0  # 0 of this unit is equal to how many base unit for this type.
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
                if not user_input.lower().startswith(
                    name_start
                ) or not user_input.lower().endswith(name_end):
                    continue
                user_prefix = user_input[len(name_start) : -len(name_end)]
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
            user_prefix = user_input[: -len(name)]
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
                if not user_input.lower().startswith(
                    abbreviation_start
                ) or not user_input.lower().endswith(abbreviation_end):
                    continue
                user_prefix = user_input[
                    len(abbreviation_start) : -len(abbreviation_end)
                ]
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
            user_prefix = user_input[: -len(abbreviation)]
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
            prefix_group = convert_type.repo.get_prefix_group_by_name(
                json_obj["valid_prefix_group"]
            )
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
        for prefix_obj in sorted(
            self.prefix_list, key=lambda x: x.multiplier, reverse=True
        ):
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
        return (self.unit == other_measure.unit) and (
            self.amount == other_measure.amount
        )

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
        return (
            decimal_format.format(output_amount)
            + " "
            + prefix_name
            + self.unit.name_list[0]
        )

    @staticmethod
    def build_list_from_user_input(repo, user_input):
        """
        Creates a new measure from a user inputted line
        :type repo: ConvertRepo
        :type user_input: str
        :rtype: list[ConvertMeasure]
        """
        user_input = user_input.strip()
        # Search through the line for digits, pull them amount as a preliminary amount and strip the rest of the line.
        # TODO: add calculation?
        preliminary_amount_str = Commons.get_digits_from_start_or_end(user_input)
        if preliminary_amount_str is None:
            raise ConvertException("Cannot find amount.")
        preliminary_amount_value = float(preliminary_amount_str)
        # Remove amountString from userInput
        if user_input.startswith(preliminary_amount_str):
            user_input = user_input[len(preliminary_amount_str) :]
        else:
            user_input = user_input[: -len(preliminary_amount_str)]
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
