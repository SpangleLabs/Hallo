from datetime import datetime


def indent_all_but_first_line(text):
    return text.replace("\n", "\n   ")


class Error:

    def __init__(self, exception, obj):
        """
        :type exception: Exception
        :type obj: Any
        """
        self.exception = exception
        self.obj = obj
        self.time = datetime.now()
        self.traceback = traceback.format_exc()

    def get_log_line(self):
        return indent_all_but_first_line(
            "Error encountered in object: {}. Exception: {}".format(self.obj, self.exception))


class SubscriptionError(Error):

    def __init__(self, exception, obj):
        super().__init__(exception, obj)


class FunctionError(Error):

    def __init__(self, exception, obj, function, event):
        """
        :type exception: Exception
        :type obj: FunctionDispatcher.FunctionDispatcher
        :type function: Function.Function
        :type event: Event.EventMessage
        """
        super().__init__(exception, obj)
        self.function = function
        self.event = event

    def get_log_line(self):
        return indent_all_but_first_line(
            "Error encountered running function {} on event with the text: {}\n"
            "in chat: {} on server: {}.\n"
            "Exception: {}".format(
                self.function,
                self.event.text,
                self.event.channel.name if self.event.channel is not None else self.event.user.name,
                self.event.server.name,
                self.exception))


class PassiveFunctionError(Error):
    pass


class ServerError(Error):
    pass
