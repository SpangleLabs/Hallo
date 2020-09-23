import re

from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.convert.convert_repo


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
        self.convert_repo = hallo.modules.convert.convert_repo.ConvertRepo.load_json()
        """ :type : ConvertRepo"""

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return Convert()

    def save_function(self):
        """Saves the function, persistent functions only."""
        self.convert_repo.save_json()

    def run(self, event):
        return event.create_response(self.convert_parse(event.command_args))

    def convert_parse(self, line, passive=False):
        """
        :type line: str
        :type passive: bool
        :rtype: str | None
        """
        # Create regex to find the place to split a user string.
        split_regex = re.compile(r" into | to |->| in ", re.IGNORECASE)
        # See if the input needs splitting.
        if split_regex.search(line) is None:
            try:
                from_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                    self.convert_repo, line
                )
                return self.convert_one_unit(from_measure_list, passive)
            except Exception as e:
                if passive:
                    return None
                return (
                    "I don't understand your input. ({}) Please format like so: "
                    "convert <value> <old unit> to <new unit>".format(e)
                )
        # Split input
        line_split = split_regex.split(line)
        # If there are more than 2 parts, be confused.
        if len(line_split) > 2:
            if passive:
                return None
            return (
                "I don't understand your input. (Are you specifying 3 units?) Please format like so: "
                "convert <value> <old unit> to <new unit>"
            )
        # Try loading the first part as a measure
        try:
            from_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                self.convert_repo, line_split[0]
            )
            return self.convert_two_unit(from_measure_list, line_split[1], passive)
        except hallo.modules.convert.convert_repo.ConvertException:
            # Try loading the second part as a measure
            try:
                from_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                    self.convert_repo, line_split[1]
                )
                return self.convert_two_unit(from_measure_list, line_split[0], passive)
            except hallo.modules.convert.convert_repo.ConvertException as e:
                # If both fail, send an error message
                if passive:
                    return None
                return (
                    "I don't understand your input. ({}) Please format like so: "
                    "convert <value> <old unit> to <new unit>".format(e)
                )

    def convert_one_unit(self, from_measure_list, passive):
        """
        Converts a single given measure into whatever base unit of the type the measure is.
        :type from_measure_list: list[ConvertMeasure]
        :type passive: bool
        :rtype: str | None
        """
        output_lines = []
        for from_measure in from_measure_list:
            to_measure = from_measure.convert_to_base()
            if from_measure.is_equal(to_measure):
                continue
            output_lines.append(self.output_line(from_measure, to_measure))
        if len(output_lines) == 0:
            if passive:
                return None
            return (
                "I don't understand your input. (No units specified.) Please format like so: "
                "convert <value> <old unit> to <new unit>"
            )
        return "\n".join(output_lines)

    def convert_two_unit(self, from_measure_list, user_input_to, passive):
        """
        Converts a single given measure into whatever unit is specified.
        :type from_measure_list: list[ConvertMeasure]
        :type user_input_to: str
        :type passive: bool
        :rtype: str | None
        """
        output_lines = []
        for from_measure in from_measure_list:
            for to_unit_obj in from_measure.unit.type.get_full_unit_list():
                prefix_obj = to_unit_obj.get_prefix_from_user_input(user_input_to)
                if prefix_obj is False:
                    continue
                to_measure = from_measure.convert_to(to_unit_obj)
                output_lines.append(
                    self.output_line_with_to_prefix(
                        from_measure, to_measure, prefix_obj
                    )
                )
        if len(output_lines) == 0:
            if passive:
                return None
            return (
                "I don't understand your input. (No units specified or found.) Please format like so: "
                "convert <value> <old unit> to <new unit>"
            )
        return "\n".join(output_lines)

    def output_line(self, from_measure, to_measure):
        """
        Creates a line to output for the equality of a fromMeasure and toMeasure.
        :type from_measure: ConvertMeasure
        :type to_measure: ConvertMeasure
        :rtype: str
        """
        last_update = (
            to_measure.unit.last_updated_date or from_measure.unit.last_updated_date
        )
        output_string = "{} = {}.".format(
            from_measure.to_string(), to_measure.to_string()
        )
        if last_update is not None:
            output_string += " (Last updated: {})".format(
                last_update.strftime("%Y-%m-%d %H:%M:%S")
            )
        return output_string

    def output_line_with_to_prefix(self, from_measure, to_measure, to_prefix):
        """
        Creates a line to output for the equality of a fromMeasure and toMeasure,
        with a specified prefix for the toMeasure.
        :type from_measure: ConvertMeasure
        :type to_measure: ConvertMeasure
        :type to_prefix: ConvertPrefix
        :rtype: str
        """
        last_update = (
            to_measure.unit.last_updated_date or from_measure.unit.last_updated_date
        )
        output_string = "{} = {}.".format(
            from_measure.to_string(), to_measure.to_string_with_prefix(to_prefix)
        )
        if last_update is not None:
            output_string += " (Last updated: {})".format(
                last_update.strftime("%Y-%m-%d %H:%M:%S")
            )
        return output_string

    def get_passive_events(self):
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        if not isinstance(event, EventMessage):
            return
        output = self.convert_parse(event.text, True)
        if output is None:
            return None
        return event.create_response(output)