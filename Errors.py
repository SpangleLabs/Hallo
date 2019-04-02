import traceback
from datetime import datetime


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
        return "Error encountered in object: {}. Exception: {}".format(self.obj, self.exception)

    def get_print_line(self):
        return self.get_log_line()


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
        output = "Error encountered running function {} on event with the text: {}\n" \
                 "In chat: {} on server: {}.\n" \
                 "Exception: {}".format(
                    self.function,
                    self.event.text,
                    self.event.channel.name if self.event.channel is not None else self.event.user.name,
                    self.event.server.name,
                    self.exception)
        return output

    def get_print_line(self):
        return "Function: {} {}\nFunction error: {}\nFunction error location: {}".format(
            self.function.__class__.__module__,
            self.function.__class__.__name__,
            self.exception,
            self.traceback
        )


class PassiveFunctionError(Error):
    pass


class ServerError(Error):
    pass
