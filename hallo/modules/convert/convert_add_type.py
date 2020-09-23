from hallo.function import Function
from hallo.inc.input_parser import InputParser
import hallo.modules.convert.convert_repo


class ConvertAddType(Function):
    """
    Adds a new conversion type.
    """

    NAMES_BASE_UNIT = [
        "base unit",
        "baseunit",
        "base_unit",
        "base-unit",
        "unit",
        "u",
        "b",
        "bu",
    ]
    NAMES_DECIMALS = [
        "decimal places",
        "decimals",
        "decimal",
        "decimalplaces",
        "dp",
        "d",
    ]

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
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Clean input
        line_clean = event.command_args.strip()
        parsed_input = InputParser(line_clean)
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
            return event.create_response(
                "You must define a base unit for this type using unit=<unit name>."
            )
        # Create new type, Create new unit, set unit as base unit, set decimals
        new_type = hallo.modules.convert.convert_repo.ConvertType(repo, input_name)
        new_base_unit = hallo.modules.convert.convert_repo.ConvertUnit(new_type, [unit_name], 1)
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
        output_string = 'Created new type "{}" with base unit "{}"{}.'.format(
            input_name, unit_name, decimal_string
        )
        return event.create_response(output_string)
