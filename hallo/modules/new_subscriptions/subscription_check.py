import logging
from typing import Set, Type, Optional

from hallo.errors import SubscriptionCheckError
from hallo.events import Event, EventMinute, EventMessage, ServerEvent
from hallo.function import Function
from hallo.hallo import Hallo
import hallo.modules.new_subscriptions.subscription_factory
import hallo.modules.new_subscriptions.subscription_repo

logger = logging.getLogger(__name__)


class SubscriptionCheck(Function):
    """
    Checks subscriptions for updates and returns them.
    """

    check_words = ["check"]
    sub_words = ["sub", "subs", "subscription", "subscriptions"]

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "check subscription"
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
                template.format(name, check, sub)
                for name in hallo.modules.new_subscriptions.subscription_factory.SubscriptionFactory.get_source_names()
                for template in name_templates
                for check in self.check_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Checks a specified feed for updates and returns them. Format: subscription check <feed name>"
        self.subscription_repo = None
        """ :type : hallo.modules.subscriptions.subscription_repo.SubscriptionRepo | None"""

    def get_sub_repo(self, hallo_obj: Hallo) -> hallo.modules.new_subscriptions.subscription_repo.SubscriptionRepo:
        if self.subscription_repo is None:
            self.subscription_repo = hallo.modules.new_subscriptions.subscription_repo.SubscriptionRepo.load_json(
                hallo_obj
            )
        return self.subscription_repo

    @staticmethod
    def is_persistent() -> bool:
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function() -> 'SubscriptionCheck':
        """Loads the function, persistent functions only."""
        return SubscriptionCheck()

    def save_function(self) -> None:
        """Saves the function, persistent functions only."""
        if self.subscription_repo is not None:
            self.subscription_repo.save_json()

    def get_passive_events(self) -> Set[Type[Event]]:
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMinute}

    def run(self, event: EventMessage) -> EventMessage:
        # Handy variables
        hallo_obj = event.server.hallo
        destination = event.user if event.channel is None else event.channel
        # Clean up input
        clean_input = event.command_args.strip().lower()
        # Acquire lock
        sub_repo = self.get_sub_repo(hallo_obj)
        with sub_repo.sub_lock:
            # Check whether input is asking to update all subscriptions
            if clean_input in self.NAMES_ALL or clean_input == "":
                matching_subs = sub_repo.sub_list
            else:
                # Otherwise see if a search subscription matches the specified one
                matching_subs = sub_repo.get_subs_by_name(clean_input, destination)
            if len(matching_subs) == 0:
                return event.create_response("Error, no subscriptions match that name.")
            # Loop through matching search subscriptions, getting updates
            update = False
            for search_sub in matching_subs:
                try:
                    update = search_sub.update() or update
                except Exception as e:
                    error = SubscriptionCheckError(search_sub, e)
                    logger.error(error.get_log_line())
            # Save list
            sub_repo.save_json()
        # Output response to user
        if not update:
            return event.create_response(
                "There were no updates for specified subscriptions."
            )
        return event.create_response(
            f"Subscription updates were found."
        )

    def passive_run(self, event: Event, hallo_obj: Hallo) -> Optional[ServerEvent]:
        # Check through all feeds to see which need updates
        sub_repo = self.get_sub_repo(hallo_obj)
        with sub_repo.sub_lock:
            logger.debug("SubCheck - Got lock")
            for search_sub in sub_repo.sub_list:
                # Only check those which have been too long since last check
                if search_sub.needs_check():
                    # Get new items
                    try:
                        logger.debug("SubCheck - Checking %s", search_sub)
                        search_sub.update()
                    except Exception as e:
                        error = SubscriptionCheckError(search_sub, e)
                        logger.error(error.get_log_line())
            # Save list
            sub_repo.save_json()
        return
