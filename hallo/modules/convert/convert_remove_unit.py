from hallo.function import Function
from hallo.inc.input_parser import InputParser


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
        self.names = {
            "convert remove unit",
            "convert delete unit",
            "convert unit remove",
            "convert unit delete",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a specified unit from the conversion repository."

    def run(self, event):
        # Load convert repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Parse input
        parsed = InputParser(event.command_args)
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
                return event.create_response(
                    "This unit name is not recognised for that unit type."
                )
        else:
            input_unit_list = []
            for type_obj in repo.type_list:
                input_unit = type_obj.get_unit_by_name(input_name)
                if input_unit is not None:
                    input_unit_list.append(input_unit)
            # Check if results are 0
            if len(input_unit_list) == 0:
                return event.create_response(
                    "No unit by that name is found in any type."
                )
            # Check if results are >=2
            if len(input_unit_list) >= 2:
                unit_outputs = []
                for input_unit in input_unit_list:
                    unit_outputs.append(
                        "{} (type={})".format(
                            input_unit.name_list[0], input_unit.type.name
                        )
                    )
                return event.create_response(
                    "There is more than one unit matching this name: {}".format(
                        ", ".join(unit_outputs)
                    )
                )
            input_unit = input_unit_list[0]
        # Ensure it is not a base unit for its type
        if input_unit == input_unit.type.base_unit:
            return event.create_response(
                "You cannot remove the base unit for a unit type."
            )
        # Remove unit
        input_unit_name = input_unit.name_list[0]
        input_unit.type.remove_unit(input_unit)
        # Done
        return event.create_response(
            'Removed unit "{}" from conversion repository.'.format(input_unit_name)
        )
