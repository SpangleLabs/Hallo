from hallo.function import Function
from hallo.inc.input_parser import InputParser


class ConvertViewRepo(Function):
    """
    Lists types, units, names, whatever.
    """

    NAMES_TYPE = ["type", "t"]
    NAMES_UNIT = ["unit", "u"]
    NAMES_PREFIXGROUP = [
        "prefix group",
        "prefixgroup",
        "prefix_group",
        "prefix-group",
        "group",
        "g",
        "pg",
    ]
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
        self.help_docs = (
            "Returns information about the conversion repository. Specify type=<name>, unit=<name>, "
            "prefix=<name> or prefix_group=<name> for more detail."
        )

    def run(self, event):
        # Load repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = InputParser(event.command_args)
        # Check if type is specified
        type_name = parsed.get_arg_by_names(self.NAMES_TYPE)
        unit_name = parsed.get_arg_by_names(self.NAMES_UNIT)
        prefix_group_name = parsed.get_arg_by_names(self.NAMES_PREFIXGROUP)
        prefix_name = parsed.get_arg_by_names(self.NAMES_PREFIX)
        if type_name is not None:
            # Get type name and object
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Unrecognised type specified.")
            # Check if unit & type are specified
            if unit_name is not None:
                # Get unit name and object
                unit_obj = type_obj.get_unit_by_name(unit_name)
                if unit_obj is None:
                    return event.create_response("Unrecognised unit specified.")
                return event.create_response(self.output_unit_as_string(unit_obj))
            # Type is defined, but not unit.
            return event.create_response(self.output_type_as_string(type_obj))
        # Check if prefix group is specified
        if prefix_group_name is not None:
            # Check if prefix & group are specified
            prefix_group_obj = repo.get_prefix_group_by_name(prefix_group_name)
            if prefix_group_obj is None:
                return event.create_response("Unrecognised prefix group specified.")
            # Check if prefix group & prefix are specified
            if prefix_name is not None:
                # Get prefix name and object
                prefix_obj = prefix_group_obj.get_prefix_by_name(
                    prefix_name
                ) or prefix_group_obj.get_prefix_by_abbr(prefix_name)
                if prefix_obj is None:
                    return event.create_response("Unrecognised prefix specified.")
                return event.create_response(self.output_prefix_as_string(prefix_obj))
            # Prefix group is defined, but not prefix
            return event.create_response(
                self.output_prefix_group_as_string(prefix_group_obj)
            )
        # Check if unit is specified
        if unit_name is not None:
            output_lines = []
            # Loop through types, getting units for each type
            for type_obj in repo.type_list:
                unit_obj = type_obj.get_unit_by_name(unit_name)
                # If unit exists by that name, add the string format to output list
                if unit_obj is not None:
                    output_lines.append(self.output_unit_as_string(unit_obj))
            if len(output_lines) == 0:
                return event.create_response("Unrecognised unit specified.")
            return event.create_response("\n".join(output_lines))
        # Check if prefix is specified
        if prefix_name is not None:
            output_lines = []
            # Loop through groups, getting prefixes for each group
            for prefix_group_obj in repo.prefix_group_list:
                prefix_obj = prefix_group_obj.get_prefix_by_name(
                    prefix_name
                ) or prefix_group_obj.get_prefix_by_abbr(prefix_name)
                # If prefix exists by that name, add the string format to output list
                if prefix_obj is not None:
                    output_lines.append(self.output_prefix_as_string(prefix_obj))
            if len(output_lines) == 0:
                return event.create_response("Unrecognised prefix specified.")
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
        output_string += (
            "Unit types: "
            + ", ".join([type_obj.name for type_obj in repo.type_list])
            + "\n"
        )
        output_string += "Prefix groups: " + ", ".join(
            [group.name for group in repo.prefix_group_list]
        )
        return output_string

    def output_type_as_string(self, type_obj):
        """
        Outputs a Conversion Type object as a string
        :type type_obj: ConvertType
        :rtype: str
        """
        unit_name_list = [unit_obj.name_list[0] for unit_obj in type_obj.unit_list]
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
        output_lines = [
            "Conversion Unit: ({})".format(unit_obj.name_list[0]),
            "Type: {}".format(unit_obj.type.name),
            "Name list: {}".format(", ".join(unit_obj.name_list)),
            "Abbreviation list: {}".format(", ".join(unit_obj.abbr_list)),
            "Value: 1 {} = {} {}".format(
                unit_obj.name_list[0],
                unit_obj.value,
                unit_obj.type.base_unit.name_list[0],
            ),
            "Offset: 0 {} = {} {}".format(
                unit_obj.name_list[0],
                unit_obj.offset,
                unit_obj.type.base_unit.name_list[0],
            ),
        ]
        last_update = unit_obj.last_updated_date
        if last_update is not None:
            output_lines.append(
                "Last updated: " + last_update.strftime("%Y-%m-%d %H:%M:%S")
            )
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
        output_string += "Multiplier: {}".format(prefix_obj.multiplier)
        return output_string
