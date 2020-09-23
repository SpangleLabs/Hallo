from hallo.function import Function
from hallo.inc.input_parser import InputParser


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
        if unit_name is None and new_name is None:
            # Start splitting from shortest left-string to longest.
            line_split = parsed.remaining_text.split()
            if len(line_split) == 1:
                return event.create_response(
                    "You must specify both a unit name and a new name to add."
                )
            # Scan remaining text for split
            pairs = parsed.split_remaining_into_two(
                lambda x, y: any([u.has_name(x) for u in unit_list])
            )
            # If not exactly 1 split, return an error
            if len(pairs) != 1:
                return event.create_response(
                    "Could not parse where unit name ends and new name begins. "
                    "Please specify with unit=<name> new_name=<name>"
                )
            # Handle the returned pair
            unit_name = pairs[0][0]
            new_name = pairs[0][1]
        # Get unit object
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
        # If new name is empty, throw error
        if len(new_name) == 0:
            return event.create_response("New name cannot be blank.")
        # Add the new name
        unit_obj.add_name(new_name)
        # Save repo
        repo.save_json()
        # Output message
        return event.create_response(
            'Added "{}" as a new name for the "{}" unit.'.format(
                new_name, unit_obj.name_list[0]
            )
        )