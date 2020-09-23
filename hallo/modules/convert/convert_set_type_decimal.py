from hallo.function import Function
from hallo.inc.input_parser import InputParser


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
        self.names = {
            "convert set type decimals",
            "convert set type decimal",
            "convert set decimals for type",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets the number of decimal places to show for a unit type."

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
        # If decimals is null, return error
        if len(parsed.number_words) == 0:
            return event.create_response(
                "Please specify a conversion type and a number of decimal places it should output."
            )
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
        return event.create_response(
            "Set the number of decimal places to display for "
            + '"{}" type units at {} places.'.format(input_type.name, decimals)
        )
