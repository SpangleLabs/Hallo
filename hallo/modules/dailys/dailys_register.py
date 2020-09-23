from urllib.error import HTTPError

from hallo.function import Function
from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


class DailysRegister(Function):
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "dailys register"
        # Names which can be used to address the function
        self.names = set(
            [
                template.format(setup, dailys)
                for template in ["{0} {1}", "{1} {0}"]
                for setup in ["setup", "register"]
                for dailys in ["dailys", "dailys api"]
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Registers a new dailys API to be fed from the current location."
            " Format: dailys register <dailys API URL> <dailys auth key?>"
        )

    def run(self, event):
        # Get dailys repo
        hallo = event.server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("dailys")
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_function
        )  # type: Dailys
        dailys_repo = sub_check_obj.get_dailys_repo(hallo)
        # Check if there's already a spreadsheet here
        if dailys_repo.get_by_location(event) is not None:
            return event.create_response(
                "There is already a dailys API configured in this location."
            )
        # Create new spreadsheet object
        clean_input = event.command_args.strip().split()
        # Check which argument is which
        # If no second argument, that means there is no key
        spreadsheet = None
        if len(clean_input) == 1:
            spreadsheet = DailysSpreadsheet(
                event.user, event.channel, clean_input[0], None
            )
        elif len(clean_input) == 2:
            try:
                spreadsheet = DailysSpreadsheet(
                    event.user, event.channel, clean_input[0], clean_input[1]
                )
                resp = spreadsheet.read_path("stats/")
                if isinstance(resp, list):
                    spreadsheet = None
            except HTTPError:
                pass
            if spreadsheet is None:
                spreadsheet = DailysSpreadsheet(
                    event.user, event.channel, clean_input[1], clean_input[0]
                )
        if len(clean_input) == 0 or len(clean_input) > 2 or spreadsheet is None:
            return event.create_response(
                "Please specify a dailys API URL and an optional auth key."
            )
        # Check the stats/ endpoint returns a list.
        resp = spreadsheet.read_path("stats/")
        if not isinstance(resp, list):
            return event.create_response("Could not locate Dailys API at this URL.")
        # Save the spreadsheet
        dailys_repo.add_spreadsheet(spreadsheet)
        dailys_repo.save_json()
        # Send response
        return event.create_response(
            "Dailys API found, currently with data for {}.".format(resp)
        )