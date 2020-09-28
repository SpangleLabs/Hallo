from typing import List

from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.new_subscriptions.subscription_factory
import hallo.modules.new_subscriptions.subscription_check
import hallo.modules.new_subscriptions.subscription


class SubscriptionRemove(Function):
    """
    Remove an RSS feed and no longer receive updates from it.
    """

    remove_words = ["remove", "delete"]
    sub_words = ["sub", "subscription"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "remove subscription"
        # Names which can be used to address the function
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {2}",
            "{2} {1}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, remove, sub)
                for name in hallo.modules.new_subscriptions.subscription_factory.SubscriptionFactory.get_source_names()
                for template in name_templates
                for remove in self.remove_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Removes a specified subscription the current location. "
            " Format: remove subscription <feed type> <feed title or url>"
        )

    def run(self, event: EventMessage) -> EventMessage:
        # Handy variables
        server = event.server
        hallo_obj = server.hallo
        function_dispatcher = hallo_obj.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name(
            "check subscription"
        )
        sub_check_obj: hallo.modules.new_subscriptions.subscription_check.SubscriptionCheck = \
            function_dispatcher.get_function_object(
                sub_check_function
            )
        sub_repo = sub_check_obj.get_sub_repo(hallo_obj)
        # Clean up input
        clean_input = event.command_args.strip()
        # Acquire lock
        with sub_repo.sub_lock:
            # Find any feeds with specified title
            test_subs: List[hallo.modules.new_subscriptions.subscription.Subscription] = sub_repo.get_subs_by_name(
                clean_input.lower(),
                event.user if event.channel is None else event.channel,
            )
            if len(test_subs) > 0:
                for del_sub in test_subs:
                    sub_repo.remove_sub(del_sub)
                title_line = f"Removed {len(test_subs)} subscriptions:"
                if len(test_subs) == 1:
                    title_line = "Removed subscription:"
                sub_lines = "\n".join([
                    f"{del_sub.source.type_name} - {del_sub.source.title}"
                    for del_sub in test_subs
                ])
                return event.create_response(f"{title_line}\n{sub_lines}")
        return event.create_response(
            "Error, there are no subscriptions in this channel matching that name."
        )
