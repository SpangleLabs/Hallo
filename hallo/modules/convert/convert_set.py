import re

from hallo.function import Function
from hallo.inc.input_parser import InputParser
import hallo.modules.convert.convert_repo


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

    def run(self, event):
        # Load Conversion Repo
        function_dispatcher = event.server.hallo.function_dispatcher
        convert_function = function_dispatcher.get_function_by_name("convert")
        convert_function_obj = function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        repo = convert_function_obj.convert_repo
        # Create regex to find the place to split a user string.
        split_regex = re.compile(r"\b(?:into|to|in|is)\b|=|->", re.IGNORECASE)
        # Split input
        line_split = split_regex.split(event.command_args)
        # If there are more than 2 parts, be confused.
        if len(line_split) != 2:
            return event.create_response(
                "I don't understand your input. (Are you specifying 3 units?) "
                + "Please format like so: convert set <value> <old unit> to <new unit>"
            )
        # Try loading the second part (reference measure) as a measure
        try:
            ref_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                repo, line_split[1]
            )
        except hallo.modules.convert.convert_repo.ConvertException:
            try:
                ref_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                    repo, "1" + line_split[1]
                )
            except hallo.modules.convert.convert_repo.ConvertException:
                return event.create_response(
                    "I don't understand the second half of your input."
                )
        # Try loading the first part as a measure
        try:
            var_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                repo, line_split[0]
            )
        except hallo.modules.convert.convert_repo.ConvertException:
            try:
                var_measure_list = hallo.modules.convert.convert_repo.ConvertMeasure.build_list_from_user_input(
                    repo, "1" + line_split[0]
                )
            except hallo.modules.convert.convert_repo.ConvertException:
                # Add a unit.
                return event.create_response(
                    self.add_unit(line_split[0], ref_measure_list)
                )
        return event.create_response(self.set_unit(var_measure_list, ref_measure_list))

    def set_unit(self, var_measure_list, ref_measure_list):
        """
        :type var_measure_list: list[ConvertMeasure]
        :type ref_measure_list: list[ConvertMeasure]
        :rtype: str
        """
        # Find list of pairs of measures, sharing a type
        measure_pair_list = []
        for var_measure in var_measure_list:
            var_measure_type = var_measure.unit.type
            for ref_measure in ref_measure_list:
                ref_measure_type = ref_measure.unit.type
                if var_measure_type == ref_measure_type:
                    measure_pair = {"var": var_measure, "ref": ref_measure}
                    measure_pair_list.append(measure_pair)
        # Check lists have exactly 1 pair sharing a type
        if len(measure_pair_list) == 0:
            return "These units do not share the same type."
        if len(measure_pair_list) > 1:
            return "It is ambiguous which units you are referring to."
        # Get the correct var_measure and ref_measure and all associated required variables
        var_measure = measure_pair_list[0]["var"]
        ref_measure = measure_pair_list[0]["ref"]
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
            new_offset = ref_offset + ref_amount * ref_value - var_amount * var_value
            var_unit.update_offset(new_offset)
            # Save repo
            repo = var_unit.type.repo
            repo.save_json()
            # Output message
            return "Set new offset for {}: 0 {} = {} {}.".format(
                var_name, var_name, new_offset, base_name
            )
        # Get new value
        new_value = (ref_offset + ref_amount * ref_value - var_offset) / var_amount
        var_unit.update_value(new_value)
        # Save repo
        repo = var_unit.type.repo
        repo.save_json()
        # Output message
        return "Set new value for {}: Δ 1 {} = Δ {} {}.".format(
            var_name, var_name, new_value, base_name
        )

    def add_unit(self, user_input, ref_measure_list):
        """
        :type user_input: str
        :type ref_measure_list: list[ConvertMeasure]
        :rtype: str
        """
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
        parsed = InputParser(user_input)
        if len(parsed.number_words) != 1:
            return "Please specify an amount when setting a new unit."
        input_amount_float = float(parsed.number_words[0])
        # Remove amountString from userInput
        input_name = " ".join(parsed.string_words)
        # Check name isn't already in use.
        if ref_type.get_unit_by_name(input_name) is not None:
            return "There's already a unit of that type by that name."
        # Add unit
        new_unit = hallo.modules.convert.convert_repo.ConvertUnit(ref_type, [input_name], 1)
        ref_type.add_unit(new_unit)
        # Update offset or value, based on what the user inputed.
        # If either given amount are zero, set the offset of varUnit.
        if input_amount_float == 0 or ref_amount == 0:
            # Calculate the new offset
            new_offset = ref_offset + ref_amount * ref_value - input_amount_float * 1
            new_unit.update_offset(new_offset)
            # Save repo
            repo = ref_unit.type.repo
            repo.save_json()
            # Output message
            return "Created new unit {} with offset: 0 {} = {} {}.".format(
                input_name, input_name, new_offset, base_name
            )
        # Get new value
        new_value = (ref_offset + ref_amount * ref_value - 0) / input_amount_float
        new_unit.update_value(new_value)
        # Save repo
        repo = ref_unit.type.repo
        repo.save_json()
        # Output message
        return "Created new unit {} with value: 1 {} = {} {}.".format(
            input_name, input_name, new_value, base_name
        )