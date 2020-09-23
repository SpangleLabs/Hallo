from hallo.function import Function
import hallo.modules.dailys.dailys_field


class DailysAddField(Function):
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "add dailys field"
        # Names which can be used to address the function
        self.names = set(
            [
                template.format(setup, dailys)
                for template in ["{0} {1}", "{1} {0}"]
                for setup in ["setup", "register", "add"]
                for dailys in ["dailys field", "field to dailys"]
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Registers a new dailys field to the spreadsheet in the current chat location."
            " Format: add dailys field <field name>"
        )

    def run(self, event):
        # Get spreadsheet repo
        hallo_obj = event.server.hallo
        function_dispatcher = hallo_obj.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("dailys")
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_function
        )
        dailys_repo = sub_check_obj.get_dailys_repo(hallo_obj)
        # Get the active spreadsheet for this person and destination
        spreadsheet = dailys_repo.get_by_location(event)
        if spreadsheet is None:
            return event.create_response(
                "There is no dailys API configured in this channel. "
                "Please register a dailys API first with `dailys register`"
            )
        # Get args
        clean_input = event.command_args.strip().lower()
        # If args are empty, list available fields
        if clean_input == "":
            return event.create_response(
                "Please specify a field, available fields are: {}".format(
                    ", ".join(field.type_name for field in hallo.modules.dailys.dailys_field.DailysFieldFactory.fields)
                )
            )
        # Check that there's exactly one field matching that name
        matching_fields = [
            field
            for field in hallo.modules.dailys.dailys_field.DailysFieldFactory.fields
            if clean_input.startswith(field.type_name)
        ]
        if len(matching_fields) != 1:
            return event.create_response(
                "I don't understand what field you would like to add. "
                "Please specify a field less ambiguously."
            )
        # Try and create the field
        matching_field = matching_fields[0]
        new_field = matching_field.create_from_input(event, spreadsheet)
        # TODO: check if field already assigned, or if we already have a field of that type?
        spreadsheet.add_field(new_field)
        dailys_repo.save_json()
        return event.create_response("Added a new field to your dailys API data.")
