from hallo.events import EventMessage
from hallo.function import Function
import hallo.modules.subscriptions.subscription_factory
import hallo.modules.subscriptions.subscription_check
import hallo.modules.subscriptions.subscription


class SubscriptionAdd(Function):
    """
    Adds a new subscription, allowing specification of server and channel.
    """

    add_words = ["add"]
    sub_words = ["sub", "subscription"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "add subscription"
        # Names which can be used to address the function
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, add, sub)
                for name in hallo.modules.subscriptions.subscription_factory.SubscriptionFactory.get_source_names()
                for template in name_templates
                for add in self.add_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Adds a new subscription to be checked for updates which will be posted to the current location."
            " Format: add subscription <sub type> <sub details> <update period?>"
        )

    def run(self, event: EventMessage) -> EventMessage:
        # Construct type name
        sub_type_name = " ".join(
            [
                w
                for w in event.command_name.lower().split()
                if w not in self.sub_words + self.add_words
            ]
        ).strip()
        # Get class from sub type name
        source_class = hallo.modules.subscriptions.subscription_factory.SubscriptionFactory.get_source_class_by_name(
            sub_type_name
        )
        # Get subscription repo
        function_dispatcher = event.server.hallo.function_dispatcher
        # TODO: check if I need to do this?
        sub_check_class = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_class
        )  # type: hallo.modules.new_subscriptions.subscription_check.SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(event.server.hallo)
        # Create new subscription
        sub_obj = hallo.modules.subscriptions.subscription.Subscription.create_from_input(
            event, source_class, sub_repo
        )
        # Acquire lock and save sub
        with sub_repo.sub_lock:
            # Add new subscription to list
            sub_repo.add_sub(sub_obj)
            # Save list
            sub_repo.save_json()
        # Send response
        return event.create_response(
            f"Created a new {source_class.type_name} subscription for {sub_obj.source.title}"
        )
