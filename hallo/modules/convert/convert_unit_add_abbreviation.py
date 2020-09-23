from hallo.function import Function
from hallo.inc.input_parser import InputParser


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
        if unit_name is None and abbr_name is None:
            # Check at least 2 words are given
            line_split = parsed.remaining_text.split()
            if len(line_split) <= 1:
                return event.create_response(
                    "You must specify both a unit name and an abbreviation to add."
                )
            # Scan remaining text for split
            pairs = parsed.split_remaining_into_two(
                lambda x, y: any([u.has_name(x) for u in unit_list])
            )
            # If not exactly 1 split, return an error
            if len(pairs) != 1:
                return event.create_response(
                    "Could not parse where unit name ends and abbreviation begins. "
                    "Please specify with unit=<name>"
                )
            # Handle the returned pair
            unit_name = pairs[0][0]
            abbr_name = pairs[0][1]
        # Get the unit object from the name
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
                "Unit name is too ambiguous, please specify with unit=<name> and type=<name>."
            )
        unit_obj = input_unit_list[0]
        # If abbreviation name is empty, throw error
        if len(abbr_name) == 0:
            return event.create_response("Abbreviation name cannot be blank.")
        # Add the new name
        unit_obj.add_abbr(abbr_name)
        # Save repo
        repo.save_json()
        # Output message
        return event.create_response(
            'Added "{}" as a new abbreviation for '
            'the "{}" unit.'.format(abbr_name, unit_obj.name_list[0])
        )
