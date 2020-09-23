from hallo.function import Function
from hallo.inc.input_parser import InputParser


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
        self.names = {
            "convert unit remove name",
            "convert unit delete name",
            "convert unit remove abbreviation",
            "convert unit delete abbreviation",
            "convert unit remove abbr",
            "convert unit delete abbr",
            "convert remove unit name",
            "convert delete unit name",
            "convert remove unit abbreviation",
            "convert delete unit abbreviation",
            "convert remove unit abbr",
            "convert delete unit abbr",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Removes a name or abbreviation from a unit, unless it's the last name."
        )

    def run(self, event):
        # Load repo, clean line
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = InputParser(event.command_args)
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
        unit_list = (
            repo.get_full_unit_list()
            if type_obj is None
            else type_obj.get_full_unit_list()
        )
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
            return event.create_response(
                "There are no units matching that description."
            )
        if len(user_unit_options) >= 2:
            return event.create_response("It is ambiguous which unit you refer to.")
        # Check this unit has other names.
        user_unit = user_unit_options[0]
        if len(user_unit.name_list) == 1:
            return event.create_response(
                "This unit only has 1 name, you cannot remove its last name."
            )
        # Remove name
        user_unit.remove_name(del_name)
        # Save repo
        repo.save_json()
        # Output
        return event.create_response(
            'Removed name "{}" from "{}" unit.'.format(del_name, user_unit.name_list[0])
        )