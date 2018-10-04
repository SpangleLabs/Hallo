from abc import ABCMeta
from threading import Lock

from Function import Function


class UserDataRepo:

    def __init__(self):
        self.data = dict()
        """ :type : dict[User, dict[str, UserDatum]]"""
        self.lock = Lock()
        """ :type : threading.Lock"""

    def get_data_by_user(self, user):
        """
        :type user: User
        :rtype: dict[str, UserData]
        """
        return self.data[user] if user in self.data else None

    def get_data_by_user_and_type(self, user, data_class):
        """
        :type user: User
        :type data_class: type
        :rtype: UserDatum
        """
        class_str = data_class.__name__
        return self.data[user][class_str] if user in self.data and class_str in self.data[user] else None

    def add_data_to_user(self, user, data):
        """
        :type user: User
        :type data: UserData
        """
        class_str = data.__class__.__name__
        if user not in self.data:
            self.data[user] = dict()
        if class_str in self.data[user]:
            raise Exception(
                "This user \"{}\" already has an entry for that userdata type \"{}\".".format(user.name, class_str))
        self.data[user][class_str] = data

    def to_json(self):
        pass  # TODO

    def from_json(self):
        pass  # TODO


class UserData(metaclass=ABCMeta):
    names = []

    def to_json(self):
        raise NotImplementedError()  # TODO

    def from_json(self):
        raise NotImplementedError()  # TODO


class FAKeyData(UserData):
    names = ["furaffinity key", "fa key", "fa cookies", "furaffinity cookies"]

    def __init__(self):
        self.cookie_a = None
        self.cookie_b = None


class WeatherLocationData(UserData):
    names = ["weather location"]

    def __init__(self):
        self.country_code = None
        self.type = None
        self.city_name = None
        self.zip_code = None
        self.latitude = None
        self.longitude = None


class UserDataFactory:
    data_classes = [FAKeyData, WeatherLocationData]

    @staticmethod
    def get_data_type_names():
        return [name for common_class in UserDataFactory.data_classes for name in common_class.names]

    @staticmethod
    def get_data_class_by_name(name):
        classes = [data_class for data_class in UserDataFactory.data_classes if name in data_class.names]
        if len(classes) != 1:
            raise Exception("Failed to find a common configuration type matching the name {}".format(name))
        return classes[0]


class UserDataSetup(Function):
    """
    Sets up a user's common configuration in the subscription repository
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "setup user data"
        # Names which can be used to address the function
        name_templates = {"setup {} user data", "setup user data {}", "setup user data for {}", "{} user data setup"}
        self.names = set([template.format(name)
                          for name in UserDataFactory.get_data_type_names()
                          for template in name_templates])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets up user data which other functions may require. " \
                         "Format: setup user data <type> <parameters>"
        self.user_data_repo = None
        """ :type : UserDataRepo | None"""

    def get_sub_repo(self, hallo):
        """
        :type hallo: Hallo.Hallo
        :rtype: SubscriptionRepo
        """
        if self.user_data_repo is None:
            self.user_data_repo = UserDataRepo.load_json(hallo)
        return self.subscription_repo

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return SubscriptionCheck()

    def save_function(self):
        """Saves the function, persistent functions only."""
        if self.subscription_repo is not None:
            self.subscription_repo.save_json()

    def run(self, event):
        # Construct type name
        common_type_name = " ".join([w for w in event.command_name.lower().split()
                                     if w not in ["setup", "user", "data", "for"]]).strip()
        # Get class from type name
        common_class = UserDataFactory.get_data_class_by_name(common_type_name)
        # Get current subscription repo
        user_data_repo = self.user_data_repo
        # Acquire lock to update the common config object
        with user_data_repo.lock:
            # Get common configuration item and update
            common_obj = user_data_repo.get_common_config_by_type(common_class)
            common_obj.update_from_input(event)
            # Save repo
            user_data_repo.save_json()
        # Send response
        return event.create_response("Set up a new {} common configuration for {}".format(common_class.type_name,
                                                                                          common_obj.get_name(event)))


class SubscriptionTeardown(Function):
    """
    Tears down a user's common configuration in the subscription repository
    """
    tear_down_words = ["tear down", "teardown"]
    sub_words = ["sub", "subs", "subscription", "subscriptions"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "tear down subscription"
        # Names which can be used to address the function
        name_templates = {"{0} {1}", "{1} {0}",
                          "{1} {0} {2}", "{1} {2} {0}", "{2} {0} {1}", "{0} {2} {1}"}
        self.names = set([template.format(name, tearDown, sub)
                          for name in SubscriptionFactory.get_common_names()
                          for template in name_templates
                          for tearDown in self.tear_down_words
                          for sub in self.sub_words])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Tears down a subscription common configuration for the current channel. " \
                         "Format: tear down subscription <type> <parameters>"

    def run(self, event):
        # Construct type name
        common_type_name = " ".join([w for w in event.command_name.split()
                                     if w not in self.sub_words+self.tear_down_words]).strip()
        # Get class from type name
        common_class = SubscriptionFactory.get_common_class_by_name(common_type_name)
        # Get current subscription repo
        function_dispatcher = event.server.hallo.function_dispatcher
        sub_check_class = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_class)  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(event.server.hallo)
        # Acquire lock to update the common config object
        with sub_repo.sub_lock:
            # Get common configuration item and update
            common_obj = sub_repo.get_common_config_by_type(common_class)
            common_obj.remove_by_input(event)
            # Save repo
            sub_repo.save_json()
        # Send response
        return event.create_response("Removed {} common configuration for {}".format(common_class.type_name,
                                                                                     common_obj.get_name(event)))
