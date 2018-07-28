from xml.dom import minidom
from inc.Commons import Commons
from Function import Function
import re
import time


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
        self.prefix_group_list = []

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
        """Returns the full list of ConvertUnit objects, in every ConvertType object."""
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
        """Gets a ConvertPrefixGroup object with the matching name."""
        for prefix_group_obj in self.prefix_group_list:
            if prefix_group_obj.name.lower() == name.lower():
                return prefix_group_obj
        return None

    @staticmethod
    def load_from_xml():
        """Loads Convert Repo from XML."""
        try:
            doc = minidom.parse("store/convert.xml")
        except (OSError, IOError):
            doc = minidom.parse("store/convert-default.xml")
        # Create new object
        new_repo = ConvertRepo()
        # Loop through prefix groups
        for prefix_group_elem in doc.getElementsByTagName("prefix_group"):
            prefix_group_obj = ConvertPrefixGroup.from_xml(new_repo, prefix_group_elem.toxml())
            new_repo.add_prefix_group(prefix_group_obj)
        # Loop through types
        for type_elem in doc.getElementsByTagName("type"):
            type_obj = ConvertType.from_xml(new_repo, type_elem.toxml())
            new_repo.add_type(type_obj)
        # Return new repo object
        return new_repo

    def save_to_xml(self):
        """Saves Convert Repo to XML."""
        # Create document, with DTD
        doc_imp = minidom.DOMImplementation()
        doc_type = doc_imp.createDocumentType(
            qualifiedName='convert',
            publicId='',
            systemId='convert.dtd',
        )
        doc = doc_imp.createDocument(None, 'convert', doc_type)
        # get root element
        root = doc.getElementsByTagName("convert")[0]
        # Add prefix groups
        for prefix_group_obj in self.prefix_group_list:
            prefix_group_elem = minidom.parseString(prefix_group_obj.to_xml()).firstChild
            root.appendChild(prefix_group_elem)
        # Add types
        for type_obj in self.type_list:
            type_elem = minidom.parseString(type_obj.to_xml()).firstChild
            root.appendChild(type_elem)
        # save XML
        with open("store/convert.xml", "w") as f:
            doc.writexml(f, addindent="\t", newl="\n")


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
        self.repo = repo
        self.name = name
        self.decimals = 2
        self.base_unit = None

    def get_full_unit_list(self):
        """Returns the full list of ConvertUnit objects"""
        return [self.base_unit] + self.unit_list

    def add_unit(self, unit):
        """Adds a new ConvertUnit object to unit list"""
        self.unit_list.append(unit)

    def remove_unit(self, unit):
        """Removes a ConvertUnit object to unit list"""
        if unit in self.unit_list:
            self.unit_list.remove(unit)

    def get_unit_by_name(self, name):
        """Get a unit by a specified name or abbreviation"""
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
    def from_xml(repo, xml_string):
        """Loads a new ConvertType object from XML"""
        # Load document
        doc = minidom.parseString(xml_string)
        # Get name and create ConvertType object
        new_name = doc.getElementsByTagName("name")[0].firstChild.data
        new_type = ConvertType(repo, new_name)
        # Get number of decimals
        if len(doc.getElementsByTagName("decimals")) > 0:
            new_decimals = int(doc.getElementsByTagName("decimals")[0].firstChild.data)
            new_type.decimals = new_decimals
        # Get base unit
        base_unit_elem = doc.getElementsByTagName("base_unit")[0].getElementsByTagName("unit")[0]
        base_unit_obj = ConvertUnit.from_xml(new_type, base_unit_elem.toxml())
        new_type.base_unit = base_unit_obj
        # Loop through unit elements, creating and adding objects.
        for unit_elem in doc.getElementsByTagName("unit"):
            if unit_elem == base_unit_elem:
                continue
            unit_obj = ConvertUnit.from_xml(new_type, unit_elem.toxml())
            new_type.add_unit(unit_obj)
        # Return created Type
        return new_type

    def to_xml(self):
        """Writes ConvertType object as XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("type")
        doc.appendChild(root)
        # Add name element
        name_elem = doc.createElement("name")
        name_elem.appendChild(doc.createTextNode(self.name))
        root.appendChild(name_elem)
        # Add decimals element
        decimals_elem = doc.createElement("decimals")
        decimals_elem.appendChild(doc.createTextNode(str(self.decimals)))
        root.appendChild(decimals_elem)
        # Add base unit element
        base_unit_elem = doc.createElement("base_unit")
        base_unit_unit_elem = minidom.parseString(self.base_unit.to_xml()).firstChild
        base_unit_elem.appendChild(base_unit_unit_elem)
        root.appendChild(base_unit_elem)
        # Add units
        for unit_obj in self.unit_list:
            unit_elem = minidom.parseString(unit_obj.to_xml()).firstChild
            root.appendChild(unit_elem)
        # Output XML
        return doc.toxml()


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
        self.type = convert_type
        self.name_list = names
        self.value = value
        self.offset = 0
        self.last_updated = None
        self.valid_prefix_group = None

    def add_name(self, name):
        """Adds a name to the list of names for a unit."""
        self.name_list.append(name)

    def remove_name(self, name):
        """Removes a name from the list of names for a unit."""
        if name in self.name_list:
            self.name_list.remove(name)

    def add_abbr(self, abbreviation):
        """Adds an abbreviation to the list of abbreviations for a unit."""
        self.abbr_list.append(abbreviation)

    def remove_abbr(self, abbreviation):
        """Removes an abbreviation from the list of abbreviations for a unit."""
        if abbreviation in self.abbr_list:
            self.abbr_list.remove(abbreviation)

    def set_value(self, value):
        """Changes the value of the unit."""
        # TODO, remove this
        self.last_updated = time.time()
        self.value = value

    def set_offset(self, offset):
        """Changes the offset of the unit."""
        # TODO, remove this
        self.last_updated = time.time()
        self.offset = offset

    def has_name(self, input_name):
        """Checks if a specified name is a valid name or abbreviation for this unit."""
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
    def from_xml(convert_type, xml_string):
        """
        Loads a new ConvertUnit object from XML.
        :type convert_type: ConvertType
        :type xml_string: str
        """
        # Load document
        doc = minidom.parseString(xml_string)
        # Get names, value and create object
        new_name_list = []
        for name_elem in doc.getElementsByTagName("name"):
            new_name = name_elem.firstChild.data
            new_name_list.append(new_name)
        new_value = float(doc.getElementsByTagName("value")[0].firstChild.data)
        new_unit = ConvertUnit(convert_type, new_name_list, new_value)
        # Loop through abbreviation elements, adding them.
        for abbr_elem in doc.getElementsByTagName("abbr"):
            new_abbr = abbr_elem.firstChild.data
            new_unit.add_abbr(new_abbr)
        # Add prefix group
        if len(doc.getElementsByTagName("valid_prefix_group")) != 0:
            convert_repo = convert_type.repo
            value_prefix_group_name = doc.getElementsByTagName("valid_prefix_group")[0].firstChild.data
            valid_prefix_group = convert_repo.get_prefix_group_by_name(value_prefix_group_name)
            new_unit.valid_prefix_group = valid_prefix_group
        # Get offset
        if len(doc.getElementsByTagName("offset")) != 0:
            new_offset = float(doc.getElementsByTagName("offset")[0].firstChild.data)
            new_unit.set_offset(new_offset)
        # Get update time
        if len(doc.getElementsByTagName("last_update")) != 0:
            new_last_updated = float(doc.getElementsByTagName("last_update")[0].firstChild.data)
            new_unit.last_updated = new_last_updated
        else:
            new_unit.last_updated = None
        # Return created ConvertUnit
        return new_unit

    def to_xml(self):
        """Outputs a ConvertUnit object as XML."""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("unit")
        doc.appendChild(root)
        # Add name elements
        for name_str in self.name_list:
            name_elem = doc.createElement("name")
            name_elem.appendChild(doc.createTextNode(name_str))
            root.appendChild(name_elem)
        # Add abbreviations
        for abbr_str in self.abbr_list:
            abbr_elem = doc.createElement("abbr")
            abbr_elem.appendChild(doc.createTextNode(abbr_str))
            root.appendChild(abbr_elem)
        # Add prefix group
        if self.valid_prefix_group is not None:
            valid_prefix_group_name = self.valid_prefix_group.name
            valid_prefix_group_elem = doc.createElement("valid_prefix_group")
            valid_prefix_group_elem.appendChild(doc.createTextNode(valid_prefix_group_name))
            root.appendChild(valid_prefix_group_elem)
        # Add value element
        value_elem = doc.createElement("value")
        value_elem.appendChild(doc.createTextNode(str(self.value)))
        root.appendChild(value_elem)
        # Add offset
        if self.offset != 0:
            offset_elem = doc.createElement("offset")
            offset_elem.appendChild(doc.createTextNode(str(self.offset)))
            root.appendChild(offset_elem)
        # Add update time
        if self.last_updated is not None:
            last_update_elem = doc.createElement("last_update")
            last_update_elem.appendChild(doc.createTextNode(str(self.last_updated)))
            root.appendChild(last_update_elem)
        # Output XML
        return doc.toxml()


class ConvertPrefixGroup:
    """
    Group of Conversion Prefixes.
    """

    def __init__(self, repo, name):
        self.prefix_list = []
        self.repo = repo
        self.name = name

    def add_prefix(self, prefix):
        """Adds a new prefix to the prefix list"""
        self.prefix_list.append(prefix)

    def remove_prefix(self, prefix):
        """Removes a prefix from the prefix list"""
        if prefix in self.prefix_list:
            self.prefix_list.remove(prefix)

    def get_prefix_by_name(self, name):
        """Gets the prefix with the specified name"""
        for prefix_obj in self.prefix_list:
            if prefix_obj.prefix == name:
                return prefix_obj
        for prefix_obj in self.prefix_list:
            if prefix_obj.prefix.lower() == name.lower():
                return prefix_obj
        return None

    def get_prefix_by_abbr(self, abbreviation):
        """Gets the prefix with the specified abbreviation"""
        for prefix_obj in self.prefix_list:
            if prefix_obj.abbreviation == abbreviation:
                return prefix_obj
        for prefix_obj in self.prefix_list:
            if prefix_obj.abbreviation.lower() == abbreviation.lower():
                return prefix_obj
        return None

    def get_appropriate_prefix(self, value):
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
    def from_xml(repo, xml_string):
        """Loads a new ConvertUnit object from XML."""
        # Load document
        doc = minidom.parseString(xml_string)
        # Get name and create object
        new_name = doc.getElementsByTagName("name")[0].firstChild.data
        new_prefix_group = ConvertPrefixGroup(repo, new_name)
        # Loop through prefix elements, creating and adding objects.
        for prefix_elem in doc.getElementsByTagName("prefix"):
            prefix_obj = ConvertPrefix.from_xml(new_prefix_group, prefix_elem.toxml())
            new_prefix_group.add_prefix(prefix_obj)
        # Return created PrefixGroup
        return new_prefix_group

    def to_xml(self):
        """Outputs a ConvertUnit object as XML."""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("prefix_group")
        doc.appendChild(root)
        # Add name element
        name_elem = doc.createElement("name")
        name_elem.appendChild(doc.createTextNode(self.name))
        root.appendChild(name_elem)
        # Add prefixes
        for prefix_obj in self.prefix_list:
            prefix_elem = minidom.parseString(prefix_obj.to_xml()).firstChild
            root.appendChild(prefix_elem)
        # Output XML
        return doc.toxml()


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
    def from_xml(prefix_group, xml_string):
        """Loads a new ConvertUnit object from XML."""
        doc = minidom.parseString(xml_string)
        new_name = doc.getElementsByTagName("name")[0].firstChild.data
        new_abbreviation = doc.getElementsByTagName("abbr")[0].firstChild.data
        new_value = float(doc.getElementsByTagName("value")[0].firstChild.data)
        new_prefix = ConvertPrefix(prefix_group, new_name, new_abbreviation, new_value)
        return new_prefix

    def to_xml(self):
        """Outputs a ConvertUnit object as XML."""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("prefix")
        doc.appendChild(root)
        # Add name
        name_elem = doc.createElement("name")
        name_elem.appendChild(doc.createTextNode(self.prefix))
        root.appendChild(name_elem)
        # Add abbreviation
        abbr_elem = doc.createElement("abbr")
        abbr_elem.appendChild(doc.createTextNode(self.abbreviation))
        root.appendChild(abbr_elem)
        # Add multiplier
        value_elem = doc.createElement("value")
        value_elem.appendChild(doc.createTextNode(str(self.multiplier)))
        root.appendChild(value_elem)
        # Return XML
        return doc.toxml()


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
        """Returns boolean, whether this Measure is equal to another."""
        return (self.unit == other_measure.unit) and (self.amount == other_measure.amount)

    def convert_to(self, unit):
        """
        Creates a new measure, equal in value but with a different unit.
        :param unit: The conversion unit to convert to
        :type unit: ConvertUnit
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
        """Creates a new measure, equal in value, but with the base unit of the unit type."""
        base_unit = self.unit.type.base_unit
        unit_value = self.unit.value
        new_amount = self.amount * unit_value
        offset = self.unit.offset
        if offset is not None:
            new_amount += offset
        new_measure = ConvertMeasure(new_amount, base_unit)
        return new_measure

    def to_string(self):
        """Converts the measure to a string for output."""
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
        """Converts the measure to a string with the specified prefix."""
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
        """Creates a new measure from a user inputted line"""
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

    def run(self, line, user_obj, destination_obj=None):
        return self.convert_parse(line)

    def convert_parse(self, line, passive=False):
        # Create regex to find the place to split a user string.
        split_regex = re.compile(' into | to |->| in ', re.IGNORECASE)
        # Load ConvertRepo
        repo = ConvertRepo.load_from_xml()
        # See if the input needs splitting.
        if split_regex.search(line) is None:
            try:
                from_measure_list = ConvertMeasure.build_list_from_user_input(repo, line)
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
            from_measure_list = ConvertMeasure.build_list_from_user_input(repo, line_split[0])
            return self.convert_two_unit(from_measure_list, line_split[1], passive)
        except ConvertException:
            # Try loading the second part as a measure
            try:
                from_measure_list = ConvertMeasure.build_list_from_user_input(repo, line_split[1])
                return self.convert_two_unit(from_measure_list, line_split[0], passive)
            except ConvertException as e:
                # If both fail, send an error message
                if passive:
                    return None
                return "I don't understand your input. ({}) Please format like so: " \
                       "convert <value> <old unit> to <new unit>".format(e)

    def convert_one_unit(self, from_measure_list, passive):
        """Converts a single given measure into whatever base unit of the type the measure is."""
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
        """Converts a single given measure into whatever unit is specified."""
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
        """Creates a line to output for the equality of a fromMeasure and toMeasure."""
        last_update = to_measure.unit.last_updated or from_measure.unit.last_updated
        output_string = "{} = {}.".format(from_measure.to_string(), to_measure.to_string())
        if last_update is not None:
            output_string += " (Last updated: {})".format(Commons.format_unix_time(last_update))
        return output_string

    def output_line_with_to_prefix(self, from_measure, to_measure, to_prefix):
        """
        Creates a line to output for the equality of a fromMeasure and toMeasure,
        with a specified prefix for the toMeasure.
        """
        last_update = to_measure.unit.last_updated or from_measure.unit.last_updated
        output_string = "{} = {}.".format(from_measure.to_string(), to_measure.to_string_with_prefix(to_prefix))
        if last_update is not None:
            output_string += " (Last updated: {})".format(Commons.format_unix_time(last_update))
        return output_string

    def get_passive_events(self):
        return {Function.EVENT_MESSAGE}

    def passive_run(self, event, full_line, hallo_obj, server_obj=None, user_obj=None, channel_obj=None):
        return self.convert_parse(full_line, True)


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

    def run(self, line, user_obj, destination_obj=None):
        output_lines = []
        # Load convert repo.
        repo = ConvertRepo.load_from_xml()
        # Update with the European Bank
        try:
            output_lines.append(self.update_from_european_bank_data(repo) or
                                "Updated currency data from The European Bank.")
        except Exception as e:
            output_lines.append("Failed to update european central bank data. {}".format(e))
        # Update with Forex
        try:
            output_lines.append(self.update_from_forex_data(repo) or
                                "Updated currency data from Forex.")
        except Exception as e:
            output_lines.append("Failed to update Forex data. {}".format(e))
        # Update with Preev
        try:
            output_lines.append(self.update_from_preev_data(repo) or
                                "Updated currency data from Preev.")
        except Exception as e:
            output_lines.append("Failed to update Preev data. {}".format(e))
        # Save repo
        repo.save_to_xml()
        # Return output
        return "\n".join(output_lines)

    def get_passive_events(self):
        return {Function.EVENT_HOUR}

    def passive_run(self, event, full_line, hallo_obj, server_obj=None, user_obj=None, channel_obj=None):
        # Load convert repo.
        repo = ConvertRepo.load_from_xml()
        # Update with the European Bank
        try:
            self.update_from_european_bank_data(repo)
        except Exception as e:
            print("Failed to update european central bank data. {}".format(e))
        # Update with Forex
        try:
            self.update_from_forex_data(repo)
        except Exception as e:
            print("Failed to update forex data. {}".format(e))
        # Update with Preev
        try:
            self.update_from_preev_data(repo)
        except Exception as e:
            print("Failed to update preev data. {}".format(e))
        # Save repo
        repo.save_to_xml()
        return None

    def update_from_money_converter_data(self, repo):
        """Updates the value of conversion currency units using The Money Convertor data."""
        # Disabling this API, as it seems to have removed actual exchange rates
        if True:
            return None
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from monet converter website
        url = 'http://themoneyconverter.com/rss-feed/EUR/rss.xml'
        xml_string = Commons.load_url_string(url)
        # Parse data
        doc = minidom.parseString(xml_string)
        root = doc.getElementsByTagName("rss")[0]
        channel_elem = root.getElementsByTagName("channel")[0]
        # Loop through items, finding currencies and values
        for item_elem in channel_elem.getElementsByTagName("item"):
            # Get currency code from title
            item_title = item_elem.getElementsByTagName("title")[0].firstChild.data
            currency_code = item_title.replace("/EUR", "")
            # Load value from description and get the reciprocal
            item_description = item_elem.getElementsByTagName("description")[0].firstChild.data
            currency_value = 1 / float(
                Commons.get_digits_from_start_or_end(item_description.split("=")[1].strip().replace(",", "")))
            # Get currency unit, set currency value.
            currency_unit = currency_type.get_unit_by_name(currency_code)
            # If unrecognised currency, continue
            if currency_unit is None:
                continue
            # Set value
            currency_unit.set_value(currency_value)

    def update_from_european_bank_data(self, repo):
        """Updates the value of conversion currency units using The European Bank data."""
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from european bank website
        url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
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
            currency_unit.set_value(currency_value)

    def update_from_forex_data(self, repo):
        """Updates the value of conversion currency units using Forex data."""
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull xml data from forex website
        url = 'http://rates.fxcm.com/RatesXML3'
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
            currency_unit.set_value(currency_value)

    def update_from_preev_data(self, repo):
        """Updates the value of conversion cryptocurrencies using Preev data."""
        # Get currency ConvertType
        currency_type = repo.get_type_by_name("currency")
        # Pull json data from preev website, combine into 1 dict
        json_dict = {'ltc': Commons.load_url_json(
                "http://preev.com/pulse/units:ltc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken"
            ),
            'ppc': Commons.load_url_json(
                "http://preev.com/pulse/units:ppc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken"
            ),
            'btc': Commons.load_url_json(
                "http://preev.com/pulse/units:btc+eur/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken"
            ),
            'xdg': Commons.load_url_json(
                "http://preev.com/pulse/units:xdg+btc/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken"
            )}
        # Loop through currency codes
        for json_key in json_dict:
            currency_code = json_key
            # currency_dict contains the actual information about the currency
            currency_dict = json_dict[json_key][json_key]
            currency_ref = list(currency_dict)[0]
            # Add up the volume and trade from each market, to find average trade price across them all
            total_volume = 0
            total_trade = 0
            for market in currency_dict[currency_ref]:
                market_volume = float(currency_dict[currency_ref][market]['volume'])
                market_last = float(currency_dict[currency_ref][market]['last'])
                total_volume += market_volume
                total_trade += market_last * market_volume
            # Calculate currency value, compared to referenced currency, from total market average
            currency_value_ref = total_trade / total_volume
            # Get the ConvertUnit object for the currency reference
            currency_ref_obj = currency_type.get_unit_by_name(currency_ref)
            if currency_ref_obj is None:
                continue
            # Work out the value compared to base unit by multiplying value of each
            currency_value = currency_value_ref * currency_ref_obj.value
            # Get the currency unit and update the value
            currency_unit = currency_type.get_unit_by_name(currency_code)
            if currency_unit is None:
                continue
            currency_unit.set_value(currency_value)


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

    def run(self, line, user_obj, destination_obj=None):
        # Load repo
        repo = ConvertRepo.load_from_xml()
        # Check if type is specified
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            # Get type name and object
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return "Unrecognised type."
            # Check if unit & type are specified
            if Commons.find_any_parameter(self.NAMES_UNIT, line):
                # Get unit name and object
                unit_name = Commons.find_any_parameter(self.NAMES_UNIT, line)
                unit_obj = type_obj.getUnitByName(unit_name)
                if unit_obj is None:
                    return "Unrecognised unit."
                return self.output_unit_as_string(unit_obj)
            # Type is defined, but not unit.
            return self.output_type_as_string(type_obj)
        # Check if prefix group is specified
        if Commons.find_any_parameter(self.NAMES_PREFIXGROUP, line):
            # Check if prefix & group are specified
            prefix_group_name = Commons.find_any_parameter(self.NAMES_PREFIXGROUP, line)
            prefix_group_obj = repo.get_prefix_group_by_name(prefix_group_name)
            if prefix_group_obj is None:
                return "Unrecognised prefix group."
            # Check if prefix group & prefix are specified
            if Commons.find_any_parameter(self.NAMES_PREFIX, line):
                # Get prefix name and object
                prefix_name = Commons.find_any_parameter(self.NAMES_PREFIX, line)
                prefix_obj = prefix_group_obj.getPrefixByName(
                    prefix_name) or prefix_group_obj.getPrefixByAbbreviation(prefix_name)
                if prefix_group_obj is None:
                    return "Unrecognised prefix."
                return self.output_prefix_as_string(prefix_obj)
            # Prefix group is defined, but not prefix
            return self.output_prefix_group_as_string(prefix_group_obj)
        # Check if unit is specified
        if Commons.find_any_parameter(self.NAMES_UNIT, line):
            unit_name = Commons.find_any_parameter(self.NAMES_UNIT, line)
            output_lines = []
            # Loop through types, getting units for each type
            for type_obj in repo.type_list:
                unit_obj = type_obj.get_unit_by_name(unit_name)
                # If unit exists by that name, add the string format to output list
                if unit_obj is not None:
                    output_lines.append(self.output_unit_as_string(unit_obj))
            if len(output_lines) == 0:
                return "Unrecognised unit."
            return "\n".join(output_lines)
        # Check if prefix is specified
        if Commons.find_any_parameter(self.NAMES_PREFIX, line):
            prefix_name = Commons.find_any_parameter(self.NAMES_PREFIX, line)
            output_lines = []
            # Loop through groups, getting prefixes for each group
            for prefix_group_obj in repo.prefix_group_list:
                prefix_obj = prefix_group_obj.get_prefix_by_name(prefix_name)
                # If prefix exists by that name, add the string format to output list
                if prefix_obj is not None:
                    output_lines.append(self.output_prefix_as_string(prefix_obj))
            if len(output_lines) == 0:
                return "Unrecognised prefix."
            return "\n".join(output_lines)
        # Nothing was specified, return info on the repo.
        return self.output_repo_as_string(repo)

    def output_repo_as_string(self, repo):
        """Outputs a Conversion Repository as a string"""
        output_string = "Conversion Repo:\n"
        output_string += "Unit types: " + \
                         ", ".join([type_obj.name for type_obj in repo.type_list]) + \
                         "\n"
        output_string += "Prefix groups: " + ", ".join([type_obj.name for type_obj in repo.type_list])
        return output_string

    def output_type_as_string(self, type_obj):
        """Outputs a Conversion Type object as a string"""
        unit_name_list = [unit_obj.get_names()[0] for unit_obj in type_obj.get_full_unit_list() if
                          unit_obj != type_obj.base_unit]
        output_string = "Conversion Type: ({})\n".format(type_obj.name)
        output_string += "Decimals: {}\n".format(type_obj.decimals)
        output_string += "Base unit: {}\n".format(type_obj.base_unit.name_list[0])
        output_string += "Other units: {}".format(", ".join(unit_name_list))
        return output_string

    def output_unit_as_string(self, unit_obj):
        """Outputs a Conversion Unit object as a string"""
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
        last_update = unit_obj.last_updated
        if last_update is not None:
            output_lines.append("Last updated: " + Commons.format_unix_time(last_update))
        prefix_group_names = unit_obj.getValidPrefixGroup().name
        if prefix_group_names is not None:
            output_lines.append("Prefix group: " + prefix_group_names)
        return "\n".join(output_lines)

    def output_prefix_group_as_string(self, prefix_group_obj):
        """Outputs a Conversion PrefixGroup object as a string"""
        prefix_list = [prefix_obj.prefix for prefix_obj in prefix_group_obj.prefix_list]
        output_string = "Prefix group: ({}\n".format(prefix_group_obj.name)
        output_string += "Prefix list: " + ", ".join(prefix_list)
        return output_string

    def output_prefix_as_string(self, prefix_obj):
        """Outputs a Conversion prefix object as a string"""
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

    def run(self, line, user_obj, destination_obj=None):
        # Load Conversion Repo
        repo = ConvertRepo.load_from_xml()
        # Create regex to find the place to split a user string.
        split_regex = re.compile(' into | to |->| in ', re.IGNORECASE)
        # Split input
        line_split = split_regex.split(line)
        # If there are more than 2 parts, be confused.
        if len(line_split) > 2:
            return "I don't understand your input. (Are you specifying 3 units?) Please format like so: " \
                   "convert <value> <old unit> to <new unit>"
        # Try loading the second part (reference measure) as a measure
        try:
            ref_measure_list = ConvertMeasure.build_list_from_user_input(repo, line_split[1])
        except ConvertException:
            try:
                ref_measure_list = ConvertMeasure.build_list_from_user_input(repo, "1" + line_split[1])
            except ConvertException:
                return "I don't understand the second half of your input."
        # Try loading the first part as a measure
        try:
            var_measure_list = ConvertMeasure.build_list_from_user_input(repo, line_split[0])
        except ConvertException:
            try:
                var_measure_list = ConvertMeasure.build_list_from_user_input(repo, "1" + line_split[0])
            except ConvertException:
                # Add a unit.
                return self.add_unit(line_split[0], ref_measure_list)
        return self.set_unit(var_measure_list, ref_measure_list)

    def set_unit(self, var_measure_list, ref_measure_list):
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
            var_unit.set_offset(new_offset)
            # Save repo
            repo = var_unit.type.repo
            repo.save_to_xml()
            # Output message
            return "Set new offset for {}: 0 {} = {} {}.".format(var_name, var_name, new_offset, base_name)
        # Get new value
        new_value = (ref_amount - ((var_offset - ref_offset) / ref_value)) / var_amount
        var_unit.set_value(new_value)
        # Save repo
        repo = var_unit.type.repo
        repo.save_to_xml()
        # Output message
        return "Set new value for {}: Δ 1 {} = Δ {} {}.".format(var_name, var_name, new_value, base_name)

    def add_unit(self, user_input, ref_measure_list):
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
            new_unit.set_offset(new_offset)
            # Save repo
            repo = ref_unit.type.repo
            repo.save_to_xml()
            # Output message
            return "Created new unit {} with offset: 0 {} = {} {}.".format(input_name,
                                                                           input_name,
                                                                           new_offset,
                                                                           base_name)
        # Get new value
        new_value = (ref_amount - ((0 - ref_offset) / ref_value)) / input_amount_float
        new_unit.set_value(new_value)
        # Save repo
        repo = ref_unit.type.repo
        repo.save_to_xml()
        # Output message
        return "Created new unit {} with value: 1 {} = {} {}.".format(input_name, input_name, new_value, base_name)


class ConvertAddType(Function):
    """
    Adds a new conversion type.
    """

    NAMES_BASE_UNIT = ["baseunit", "base_unit", "base-unit", "unit", "u", "b", "bu"]
    NAMES_DECIMALS = ["decimals", "decimal", "decimalplaces", "dp", "d"]

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

    def run(self, line, user_obj, destination_obj=None):
        # Load repo, clean line
        repo = ConvertRepo.load_from_xml()
        line_clean = line.strip()
        # Check if base unit is defined
        unit_name = None
        if Commons.find_any_parameter(self.NAMES_BASE_UNIT, line_clean):
            unit_name = Commons.find_any_parameter(self.NAMES_BASE_UNIT, line_clean)
        # Check if decimal places is defined
        decimals = None
        if Commons.find_any_parameter(self.NAMES_DECIMALS, line_clean):
            try:
                decimals = int(Commons.find_any_parameter(self.NAMES_DECIMALS, line_clean))
            except ConvertException:
                decimals = None
        # Clean unit and type setting from the line to just get the name to remove
        param_regex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        multispace_regex = re.compile("\s+")
        input_name = param_regex.sub("\1\4", line_clean).strip()
        input_name = multispace_regex.sub(" ", input_name)
        # Check that type name doesn't already exist.
        existing_type = repo.get_type_by_name(input_name)
        if existing_type is not None:
            return "A type by this name already exists."
        # Check base unit name was defined.
        if unit_name is None:
            return "You must define a base unit for this type using unit=<unit name>."
        # Create new type, Create new unit, set unit as base unit, set decimals
        new_type = ConvertType(repo, input_name)
        new_base_unit = ConvertUnit(new_type, [unit_name], 1)
        new_type.base_unit = new_base_unit
        if decimals is not None:
            new_type.decimals = decimals
        # add type to repo, save
        repo.add_type(new_type)
        repo.save_to_xml()
        # Output message
        decimal_string = ""
        if decimals is not None:
            decimal_string = " and {} decimal places".format(decimals)
        output_string = "Created new type \"{}\" with base unit \"{}\"{}.".format(input_name, unit_name, decimal_string)
        return output_string


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
        self.names = {"convert set type decimals", "convert set type decimal"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets the number of decimal places to show for a unit type."

    def run(self, line, user_obj, destination_obj=None):
        # Load convert repo
        repo = ConvertRepo.load_from_xml()
        # Get decimals from input
        input_decimals = Commons.get_digits_from_start_or_end(line)
        # If decimals is null, return error
        if input_decimals is None:
            return "Please specify a conversion type and a number of decimal places it should output."
        # Get type name from input
        if line.startswith(input_decimals):
            input_name = line[len(input_decimals):].strip()
        else:
            input_name = line[:-len(input_decimals)].strip()
        # Convert decimals to integer
        decimals = int(float(input_decimals))
        # Get selected type
        input_type = repo.get_type_by_name(input_name)
        # If type does not exist, return error
        if input_type is None:
            return "This is not a recognised conversion type."
        # Set decimals
        input_type.setDecimals(decimals)
        # Save repo
        repo.save_to_xml()
        # Output message
        return "Set the number of decimal places to display for \"{}\" type units at {} places.".format(input_type.name,
                                                                                                        decimals)


class ConvertRemoveUnit(Function):
    """
    Removes a specified unit from the conversion repo.
    """

    NAMES_TYPE = ["type", "t"]

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

    def run(self, line, user_obj, destination_obj=None):
        # Load convert repo
        repo = ConvertRepo.load_from_xml()
        # Check if a type is specified
        type_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # Clean type setting from the line to just get the name to remove
        param_regex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        input_name = param_regex.sub("\1\4", line).strip()
        # Find unit
        if type_name is not None:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return "This conversion type is not recognised."
            input_unit = type_obj.getUnitByName(input_name)
            if input_unit is None:
                return "This unit name is not recognised for that unit type."
        else:
            input_unit_list = []
            for type_obj in repo.type_list:
                input_unit = type_obj.get_unit_by_name(input_name)
                if input_unit is not None:
                    input_unit_list.append(input_unit)
            # Check if results are 0
            if len(input_unit_list) == 0:
                return "No unit by that name is found in any type."
            # Check if results are >=2
            if len(input_unit_list) >= 2:
                return ""
            input_unit = input_unit_list[0]
        # Ensure it is not a base unit for its type
        if input_unit == input_unit.type.base_unit:
            return "You cannot remove the base unit for a unit type."
        # Remove unit
        input_unit_name = input_unit.name_list[0]
        input_unit.type.remove_unit(input_unit)
        # Done
        return "Removed unit \"{}\" from conversion repository.".format(input_unit_name)


class ConvertUnitAddName(Function):
    """
    Adds a new name to a unit.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert unit add name"
        # Names which can be used to address the Function
        self.names = {"convert unit add name"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new name to a unit."

    def run(self, line, user_obj, destination_obj=None):
        # Load repository
        repo = ConvertRepo.load_from_xml()
        # Check for type=
        type_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # Check for unit=
        unit_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            unit_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # clean up the line
        param_regex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        input_name = param_regex.sub("\1\4", line).strip()
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return "Unrecognised type."
            unit_list = type_obj.getUnitList()
        # If no unit=, try splitting the line to find where the old name ends and new name begins
        if unit_name is None:
            # Start splitting from shortest left-string to longest.
            line_split = input_name.split()
            input_unit_list = []
            found_name = False
            input_unit_name = ""
            for input_unit_name in [' '.join(line_split[:x + 1]) for x in range(len(line_split))]:
                for unit_obj in unit_list:
                    if unit_obj.has_name(input_unit_name):
                        input_unit_list.append(unit_obj)
                        found_name = True
                if found_name:
                    break
            new_unit_name = input_name[len(input_unit_name):].strip()
        else:
            input_unit_list = []
            for unit_obj in unit_list:
                if unit_obj.has_name(unit_name):
                    input_unit_list.append(unit_obj)
            new_unit_name = input_name
        # If 0 units found, throw error
        if len(input_unit_list) == 0:
            return "No unit found by that name."
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return "Unit name is too ambiguous, please specify with unit= and type= ."
        unit_obj = input_unit_list[0]
        # Add the new name
        unit_obj.add_name(new_unit_name)
        # Save repo
        repo.save_to_xml()
        # Output message
        return "Added \"{}\" as a new name for the \"{}\" unit.".format(new_unit_name, unit_obj.name_list[0])


class ConvertUnitAddAbbreviation(Function):
    """
    Adds a new abbreviation to a unit.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]

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

    def run(self, line, user_obj, destination_obj=None):
        # Load repository
        repo = ConvertRepo.load_from_xml()
        # Check for type=
        type_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # Check for unit=
        unit_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            unit_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # clean up the line
        param_regex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        input_abbr = param_regex.sub("\1\4", line).strip()
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return "Unrecognised type."
            unit_list = type_obj.getUnitList()
        # If no unit=, try splitting the line to find where the old name ends and new name begins
        if unit_name is None:
            # Start splitting from shortest left-string to longest.
            line_split = input_abbr.split()
            input_unit_list = []
            found_abbr = False
            input_unit_name = ""
            for input_unit_name in [' '.join(line_split[:x + 1]) for x in range(len(line_split))]:
                for unit_obj in unit_list:
                    if unit_obj.has_name(input_unit_name):
                        input_unit_list.append(unit_obj)
                        found_abbr = True
                if found_abbr:
                    break
            new_unit_abbr = input_abbr[len(input_unit_name):].strip()
        else:
            input_unit_list = []
            for unit_obj in unit_list:
                if unit_obj.has_name(unit_name):
                    input_unit_list.append(unit_obj)
            new_unit_abbr = input_abbr
        # If 0 units found, throw error
        if len(input_unit_list) == 0:
            return "No unit found by that name."
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return "Unit name is too ambiguous, please specify with unit= and type= ."
        unit_obj = input_unit_list[0]
        # Add the new name
        unit_obj.add_abbr(new_unit_abbr)
        # Save repo
        repo.save_to_xml()
        # Output message
        return "Added \"{}\" as a new abbreviation for the \"{}\" unit.".format(new_unit_abbr, unit_obj.name_list[0])


class ConvertUnitRemoveName(Function):
    """
    Removes a name or abbreviation from a unit, unless it's the last name.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]

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

    def run(self, line, user_obj, destination_obj=None):
        # Load repo, clean line
        repo = ConvertRepo.load_from_xml()
        line_clean = line.strip()
        # Check if unit is defined
        unit_name = None
        if Commons.find_any_parameter(self.NAMES_UNIT, line_clean):
            unit_name = Commons.find_any_parameter(self.NAMES_UNIT, line_clean)
        # Check if type is defined
        type_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line_clean):
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, line_clean)
            if repo.get_type_by_name(type_name) is None:
                return "Invalid type specified."
        # Clean unit and type setting from the line to just get the name to remove
        param_regex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        input_name = param_regex.sub("\1\4", line_clean).strip()
        # Check if description is sufficient to narrow it to 1 and only 1 unit
        user_unit_options = []
        for unit_obj in repo.get_full_unit_list():
            # If type is defined and not the same as current unit, skip it
            if type_name is not None and type_name != unit_obj.type.name:
                continue
            # if unit name is defined and not a valid name for the unit, skip it.
            if unit_name is not None and not unit_obj.has_name(unit_name):
                continue
            # If input_name is not a valid name for the unit, skip it.
            if not unit_obj.has_name(input_name):
                continue
            # Otherwise it's the one, add it to the list
            user_unit_options.append(unit_obj)
        # Check if that narrowed it down correctly.
        if len(user_unit_options) == 0:
            return "There are no units matching that description."
        if len(user_unit_options) >= 2:
            return "It is ambiguous which unit you refer to."
        # Check this unit has other names.
        user_unit = user_unit_options[0]
        if len(user_unit.name_list) == 1:
            return "This unit only has 1 name, you cannot remove its last name."
        # Remove name
        user_unit.remove_name(input_name)
        # Save repo
        repo.save_to_xml()
        # Output
        return "Removed name \"{}\" from \"{}\" unit.".format(input_name, user_unit.name_list[0])


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

    def run(self, line, user_obj, destination_obj=None):
        # Load repository
        repo = ConvertRepo.load_from_xml()
        # Check for type=
        type_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            type_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # Check for unit=
        unit_name = None
        if Commons.find_any_parameter(self.NAMES_TYPE, line):
            unit_name = Commons.find_any_parameter(self.NAMES_TYPE, line)
        # Check for prefixgroup=
        prefix_group_name = None
        if Commons.find_any_parameter(self.NAMES_PREFIX_GROUP, line):
            prefix_group_name = Commons.find_any_parameter(self.NAMES_PREFIX_GROUP, line)
        # clean up the line
        param_regex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)", re.IGNORECASE)
        input_name = param_regex.sub("\1\4", line).strip()
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
                return "Prefix group not recognised."
        else:
            prefix_group = repo.get_prefix_group_by_name(prefix_group_name)
            if prefix_group is None and prefix_group_name.lower() != "none":
                return "Prefix group not recognised."
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return "Unrecognised type."
            unit_list = type_obj.getUnitList()
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
            return "No unit found by that name."
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return "Unit name is too ambiguous, please specify with unit= and type= ."
        unit_obj = input_unit_list[0]
        # Set the prefix group
        unit_obj.valid_prefix_group = prefix_group
        # Save repo
        repo.save_to_xml()
        # Output message
        if prefix_group is None:
            prefix_group_name = "none"
        else:
            prefix_group_name = prefix_group.name
        return "Set \"{}\" as the prefix group for the \"{}\" unit.".format(prefix_group_name, unit_obj.name_list[0])
