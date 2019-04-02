import traceback
from abc import ABCMeta
from datetime import datetime


class Error(metaclass=ABCMeta):

    def __init__(self):
        self.time = datetime.now()

    def get_log_line(self):
        raise NotImplementedError

    def get_print_line(self):
        raise NotImplementedError


class ExceptionError(Error):

    def __init__(self, exception, obj):
        """
        :type exception: Exception
        :type obj: Any
        """
        super().__init__()
        self.exception = exception
        self.obj = obj
        self.traceback = traceback.format_exc()

    def get_log_line(self):
        return "Error encountered in object: {}. Exception: {}".format(self.obj, self.exception)

    def get_print_line(self):
        return self.get_log_line()


class FunctionSaveError(ExceptionError):

    def __init__(self, exception, obj):
        """
        :type exception: Exception
        :type obj: Function.Function
        """
        super().__init__(exception, obj)
        self.obj = obj

    def get_log_line(self):
        return "Error encountered while saving function: {}. Exception: {}".format(self.obj.__name__, self.exception)

    def get_print_line(self):
        return self.get_log_line()


class SubscriptionError(ExceptionError):

    def __init__(self, exception, obj):
        super().__init__(exception, obj)


class PassiveFunctionError(ExceptionError):

    def __init__(self, exception, dispatcher, function, event):
        """
        :type exception: Exception
        :type dispatcher: FunctionDispatcher.FunctionDispatcher
        :type function: Function.Function
        :type event: Events.Event
        """
        super().__init__(exception, dispatcher)
        self.function = function
        self.event = event

    def get_log_line(self):
        output = "Error encountered running passive function {} {} on event type: {}\n" \
                 "Event log line: {}\n" \
                 "Exception: {}".format(
                    self.function.__class__.__module__,
                    self.function.__class__.__name__,
                    self.event.__class__.__name__,
                    self.event.get_log_line(),
                    self.exception)
        return output

    def get_print_line(self):
        return "Passive function: {} {}\nFunction event: {}\nFunction error: {}\nFunction error location: {}".format(
            self.function.__class__.__module__,
            self.function.__class__.__name__,
            self.event,
            self.exception,
            self.traceback
        )


class FunctionError(PassiveFunctionError):

    def __init__(self, exception, dispatcher, function, event):
        """
        :type exception: Exception
        :type dispatcher: FunctionDispatcher.FunctionDispatcher
        :type function: Function.Function
        :type event: Events.EventMessage
        """
        super().__init__(exception, dispatcher, function, event)
        self.event = event  # Enables type annotations to work correctly.

    def get_log_line(self):
        output = "Error encountered running function {} {} on event with the text: {}\n" \
                 "In chat: {} on server: {} by user: {}.\n" \
                 "Exception: {}".format(
                    self.function.__class__.__module__,
                    self.function.__class__.__name__,
                    self.event.text,
                    self.event.channel.name if self.event.channel is not None else self.event.user.name,
                    self.event.server.name,
                    self.event.user.name if self.event.user is not None else None,
                    self.exception)
        return output

    def get_print_line(self):
        return "Function: {} {}\nFunction error: {}\nFunction error location: {}".format(
            self.function.__class__.__module__,
            self.function.__class__.__name__,
            self.exception,
            self.traceback
        )


class FunctionNotFoundError(Error):

    def __init__(self, dispatcher, event):
        """
        :type dispatcher: FunctionDispatcher.FunctionDispatcher
        :type event: Events.EventMessage
        """
        super().__init__()
        self.dispatcher = dispatcher
        self.event = event

    def get_log_line(self):
        return "Failed to find a function matching the event with text: {}\n" \
               "In chat: {} on server: {} by user {}.".format(
                    self.event.text,
                    self.event.channel.name if self.event.channel is not None else self.event.user.name,
                    self.event.server.name,
                    self.event.user.name if self.event.user is not None else None
                )

    def get_print_line(self):
        return "Function not found matching message: {}".format(
                    self.event.text
                )


class FunctionNotAllowedError(Error):

    def __init__(self, dispatcher, function, event):
        """
        :type dispatcher: FunctionDispatcher.FunctionDispatcher
        :type function: class[Function.Function]
        :type event: Events.EventMessage
        """
        super().__init__()
        self.dispatcher = dispatcher
        self.function = function
        self.event = event

    def get_log_line(self):
        return "User {} in channel {} on server {} tried to use function: {}.\n" \
               "The message was: {}".format(
                    self.event.user.name if self.event.user is not None else None,
                    self.event.channel.name if self.event.channel is not None else self.event.user.name,
                    self.event.server.name,
                    self.function.__name__,
                    self.event.text
                )

    def get_print_line(self):
        return "Permissions forbid function {} {} being used by {} in channel {} on server {}.\n" \
               "The message was: {}".format(
                    self.function.__module__,
                    self.function.__name__,
                    self.event.user.name if self.event.user is not None else None,
                    self.event.channel.name if self.event.channel is not None else self.event.user.name,
                    self.event.server.name,
                    self.event.text
                )


class ServerError(Error):
    pass
