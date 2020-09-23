from hallo.function import Function
from hallo.inc.input_parser import InputParser


class ConvertUnitSetPrefixGroup(Function):
    """
    Sets the prefix group for a unit.
    """

    NAMES_UNIT = ["unit", "u"]
    NAMES_TYPE = ["type", "t"]
    NAMES_PREFIX_GROUP = [
        "prefix group",
        "prefixgroup",
        "prefix_group",
        "prefix-group",
        "group",
        "prefixes",
        "prefix",
        "g",
        "pg",
    ]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "convert set prefix group"
        # Names which can be used to address the Function
        self.names = {
            "convert set prefix group",
            "convert prefix group",
            "convert unit set prefix group",
            "convert unit prefix group",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Sets a prefix group for a unit, set prefix group to None to remove it. "
            "Format: unit=<name> prefix_group=<name>. Can optionally add type=<name> argument."
        )

    def run(self, event):
        # Load repository
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = InputParser(event.command_args)
        # Check for type=
        type_name = parsed.get_arg_by_names(self.NAMES_TYPE)
        # Check for unit=
        unit_name = parsed.get_arg_by_names(self.NAMES_UNIT)
        # Check for prefixgroup=
        prefix_group_name = parsed.get_arg_by_names(self.NAMES_PREFIX_GROUP)
        # clean up the line
        input_name = parsed.remaining_text
        # If unit name xor prefix group is none, use input name
        if unit_name is None and prefix_group_name is not None:
            unit_name = input_name
        if prefix_group_name is None and unit_name is not None:
            prefix_group_name = input_name
        # Get unit list
        if type_name is None:
            unit_list = repo.get_full_unit_list()
        else:
            type_obj = repo.get_type_by_name(type_name)
            if type_obj is None:
                return event.create_response("Unrecognised type specified.")
            unit_list = type_obj.get_full_unit_list()
        # Get parse remaining text into unit name and prefix group name
        if unit_name is None and prefix_group_name is None:
            # Check at least 2 words are given
            line_split = parsed.remaining_text.split()
            if len(line_split) <= 1:
                return event.create_response(
                    "You must specify both a unit name and a prefix group to set."
                )

            # Scan remaining text for split

            def is_unit_name_valid(name):
                return any([u.has_name(name) for u in unit_list])

            def is_prefix_group_valid(name):
                return (
                    name.lower() == "none"
                    or repo.get_prefix_group_by_name(name) is not None
                )

            pairs = parsed.split_remaining_into_two(
                lambda x, y: is_unit_name_valid(x) and is_prefix_group_valid(y)
            )
            # If not exactly 1 split, return an error
            if len(pairs) != 1:
                return event.create_response(
                    "Could not parse where unit name ends and prefix group begins. "
                    "Please specify with unit=<name> prefix_group=<name>"
                )
            # Handle the returned pair
            unit_name = pairs[0][0]
            prefix_group_name = pairs[0][1]
            if prefix_group_name.lower() == "none":
                prefix_group = None
            else:
                prefix_group = repo.get_prefix_group_by_name(prefix_group_name)
        else:
            prefix_group = repo.get_prefix_group_by_name(prefix_group_name)
            if prefix_group is None and prefix_group_name.lower() != "none":
                return event.create_response("Prefix group not recognised.")
        # Get unit object from name
        input_unit_list = []
        for unit_obj in unit_list:
            if unit_obj.has_name(unit_name):
                input_unit_list.append(unit_obj)
        # If 0 units found, throw error
        if len(input_unit_list) == 0:
            return event.create_response("No unit found by that name.")
        # If 2+ units found, throw error
        if len(input_unit_list) >= 2:
            return event.create_response(
                "Unit name is too ambiguous, please specify with unit= and type= ."
            )
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
        return event.create_response(
            'Set "{}" as the prefix group for '
            'the "{}" unit.'.format(prefix_group_name, unit_obj.name_list[0])
        )
