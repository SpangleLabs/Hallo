from hallo.function import Function
from hallo.inc.commons import Commons


def hallo_has_op(channel):
    """
    Checks whether hallo has op in a given channel.
    :param channel: channel to check op status for
    :type channel: destination.Channel
    :return: whether hallo has op
    :rtype: bool
    """
    server = channel.server
    hallo_user = server.get_user_by_address(
        server.get_nick().lower(), server.get_nick()
    )
    hallo_membership = channel.get_membership_by_user(hallo_user)
    return hallo_membership.is_op


class ChannelCaps(Function):
    """
    Set caps lock for a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "caps lock"
        # Names which can be used to address the function
        self.names = {
            "caps lock",
            "channel caps",
            "channel caps lock",
            "chan caps",
            "chan caps lock",
            "channelcapslock",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets caps lock for channel on or off."

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, toggle caps lock in current destination
        line_clean = event.command_args.strip()
        if line_clean == "":
            event.channel.use_caps_lock = not event.channel.use_caps_lock
            return event.create_response("Caps lock toggled.")
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                event.channel.use_caps_lock = input_bool
                return event.create_response(
                    "Caps lock set {}.".format({False: "off", True: "on"}[input_bool])
                )
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.use_caps_lock = not target_channel.use_caps_lock
                return event.create_response(
                    "Caps lock toggled in {}.".format(target_channel.name)
                )
            # Otherwise input unknown
            return event.create_response(
                "Error, I don't understand your input, "
                + "please specify a channel and whether to turn caps lock on or off."
            )
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return event.create_response(
                "Error, I don't understand your input, please specify a channel and "
                + "whether to turn caps lock on or off."
            )
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if target_channel is None or not target_channel.in_channel:
            return event.create_response("Error, I'm not in that channel.")
        target_channel.use_caps_lock = input_bool
        return event.create_response(
            "Caps lock set {} in {}.".format(
                {False: "off", True: "on"}[input_bool], target_channel.name
            )
        )


class ChannelLogging(Function):
    """
    Set logging for a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "logging"
        # Names which can be used to address the function
        self.names = {
            "logging",
            "channel logging",
            "channel log",
            "chan logging",
            "chan log",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets or toggles logging for channel."

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, toggle logging in current destination
        line_clean = event.command_args.strip()
        if line_clean == "":
            event.channel.logging = not event.channel.logging
            return event.create_response("Logging toggled.")
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                event.channel.logging = input_bool
                return event.create_response(
                    "Logging set {}.".format({False: "off", True: "on"}[input_bool])
                )
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.logging = not target_channel.logging
                return event.create_response(
                    "Logging toggled in {}.".format(target_channel.name)
                )
            # Otherwise input unknown
            return event.create_response(
                "Error, I don't understand your input, please specify a channel and "
                + "whether to turn logging on or off."
            )
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return event.create_response(
                "Error, I don't understand your input, please specify a channel and "
                + "whether to turn logging on or off."
            )
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if not target_channel.in_channel:
            return event.create_response("Error, I'm not in that channel.")
        target_channel.logging = input_bool
        return event.create_response(
            "Logging set {} in {}.".format(
                {False: "off", True: "on"}[input_bool], target_channel.name
            )
        )


class ChannelPassiveFunctions(Function):
    """
    Set whether passive functions are enabled in a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "passive"
        # Names which can be used to address the function
        self.names = {"passive"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets or toggles logging for channel."

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = {"passive"}
        for chan in ["chan ", "channel ", ""]:
            for passive in [
                "passive",
                "passive func",
                "passive funcs",
                "passive function",
                "passive functions",
            ]:
                self.names.add(chan + passive)
        return self.names

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, toggle passive functions in current destination
        line_clean = event.command_args.strip()
        if line_clean == "":
            event.channel.passive_enabled = not event.channel.passive_enabled
            return event.create_response("Passive functions toggled.")
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                event.channel.passive_enabled = input_bool
                return event.create_response(
                    "Passive functions set {}.".format(
                        {False: "disabled", True: "enabled"}[input_bool]
                    )
                )
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.passive_enabled = not target_channel.passive_enabled
                return event.create_response(
                    "Passive functions toggled in {}.".format(target_channel.name)
                )
            # Otherwise input unknown
            return event.create_response(
                "Error, I don't understand your input, please specify a channel and "
                + "whether to turn passive functions on or off."
            )
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return event.create_response(
                "Error, I don't understand your input, please specify a channel and "
                + "whether to turn passive functions on or off."
            )
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if not target_channel.in_channel:
            return event.create_response("Error, I'm not in that channel.")
        target_channel.passive_enabled = input_bool
        return event.create_response(
            "Passive functions set {} in {}.".format(
                "enabled" if input_bool else "disabled", target_channel.name
            )
        )


class ChannelPassword(Function):
    """
    Set password for a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "channel password"
        # Names which can be used to address the function
        self.names = {"channel password", "chan password", "channel pass", "chan pass"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets or disables channel password."

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, turn the password for current channel off.
        line_clean = event.command_args.strip()
        if line_clean == "":
            event.channel.password = None
            return event.create_response("Channel password disabled.")
        # If line has 1 argument, set password for current channel
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if null was specified
            input_null = Commons.is_string_null(line_split[0])
            if input_null:
                event.channel.password = None
                return event.create_response("Channel password disabled.")
            else:
                event.channel.password = line_split[0]
                return event.create_response("Channel password set.")
        # Otherwise line has 2 or more arguments.
        # Assume first is channel, and second is password.
        input_null = Commons.is_string_null(line_split[1])
        target_channel_name = line_split[0]
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if input_null:
            target_channel.password = None
            return event.create_response(
                "Channel password disabled for {}.".format(target_channel.name)
            )
        else:
            target_channel.password = line_split[1]
            return event.create_response(
                "Channel password set for {}.".format(target_channel.name)
            )
