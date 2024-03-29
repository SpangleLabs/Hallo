import inspect
import datetime
import logging
import re
import json
import random
from datetime import timedelta
from typing import List, Optional, Dict, TypeVar, Union, Callable, Generic, Type, Set

import requests
from prometheus_client import Gauge
from publicsuffixlist import PublicSuffixList

logger = logging.getLogger(__name__)
T = TypeVar('T')
S = TypeVar('S')


subscription_count = Gauge(
    "hallo_subscriptionrepo_subscription_count",
    "Total number of subscriptions in the subscription repo by type",
    labelnames=["source_type"]
)
subscription_menu_count = Gauge(
    "hallo_subscriptionrepo_menu_count",
    "Total number of active menus in the subscription repo"
)


def all_subclasses(cls: Type) -> Set[Type]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


class Commons(object):
    """
    Class of commons methods, useful anywhere, but all static.
    """

    @staticmethod
    def chunk_string_dot(string: str, length: int) -> List[str]:
        if len(string) <= length:
            return [string]
        else:
            list_of_strings = [string[: length - 3] + "..."]
            rest_of_string = string[length - 3:]
            while len(rest_of_string) > length - 3:
                list_of_strings += ["..." + rest_of_string[: length - 6] + "..."]
                rest_of_string = rest_of_string[length - 6:]
            list_of_strings += ["..." + rest_of_string]
            return list_of_strings

    @staticmethod
    def read_file_to_list(filename: str) -> List[str]:
        with open(filename, "r") as f:
            file_list = []
            raw_line = f.readline()
            while raw_line != "":
                file_list.append(raw_line.replace("\n", ""))
                raw_line = f.readline()
            return file_list

    @staticmethod
    def get_domain_name(url: str) -> str:
        """
        Gets the domain name of a URL, removing the TLD
        :param url: URL to find domain of
        """
        # Sanitise the URL, removing protocol and directories
        url = url.split("://")[-1]
        url = url.split("/")[0]
        url = url.split(":")[0]
        # Get the public suffix
        public_suffix = PublicSuffixList()
        url_tld = public_suffix.publicsuffix(url)
        # Else return the last part before the TLD
        return url[: -len(url_tld) - 1].split(".")[-1]

    @staticmethod
    def string_to_bool(string: str) -> Optional[bool]:
        """
        Converts a string to a boolean.
        :param string: String to convert to boolean
        """
        string = string.lower()
        if string in ["1", "true", "t", "yes", "y", "on", "enabled", "enable"]:
            return True
        if string in ["0", "false", "f", "no", "n", "off", "disabled", "disable"]:
            return False
        return None

    @staticmethod
    def is_string_null(string: str) -> bool:
        """
        Checks if a string could mean null.
        :param string: String to check for meaning null
        """
        string = string.lower()
        if string in [
            "0",
            "false",
            "off",
            "disabled",
            "disable",
            "",
            "nul",
            "null",
            "none",
            "nil",
        ]:
            return True
        return False

    @staticmethod
    def ordinal(number: int) -> str:
        """
        Returns the ordinal of a number
        :param number: Number to get ordinal string for
        :type: number: int
        """
        if number % 10 == 1 and number % 100 != 11:
            return "{}st".format(number)
        elif number % 10 == 2 and number % 100 != 12:
            return "{}nd".format(number)
        elif number % 10 == 3 and number % 100 != 13:
            return "{}rd".format(number)
        else:
            return "{}th".format(number)

    @staticmethod
    def format_unix_time(time_stamp: float) -> str:
        """
        Returns a string, formatted datetime from a timestamp
        :param time_stamp: unix timestamp
        """
        return datetime.datetime.utcfromtimestamp(time_stamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def create_headers_dict(headers: List[List[str]]) -> Dict[str, str]:
        """
        Creates a headers dictionary, for requests, and adds user agent
        :param headers: List of HTTP headers to add to request
        """
        if headers is None:
            headers = []
        headers_dict = {"User-Agent": "Hallo IRCBot hallo@dr-spangle.com"}
        for header in headers:
            headers_dict[header[0]] = header[1]
        return headers_dict

    @staticmethod
    def load_url_string(url: str, headers: List[List[str]] = None) -> str:
        """
        Takes a url to an xml resource, pulls it and returns a dictionary.
        :param url: URL to download
        :param headers: List of HTTP headers to add to request
        """
        headers_dict = Commons.create_headers_dict(headers)
        resp = requests.get(url, headers=headers_dict, timeout=10)
        return resp.text

    @staticmethod
    def load_url_json(url: str, headers: List[List[str]] = None, json_fix: bool = False) -> Dict:
        """
        Takes a url to a json resource, pulls it and returns a dictionary.
        :param url: URL of json to download
        :param headers: List of HTTP headers to add to request
        :param json_fix: Whether to "fix" the JSON being returned for parse errors
        """
        if headers is None:
            headers = []
        code = Commons.load_url_string(url, headers)
        if json_fix:
            code = re.sub(",+", ",", code)
            code = code.replace("[,", "[").replace(",]", "]")
        try:
            output_dict = json.loads(code)
        except Exception as e:
            logger.error("Failed to parse received JSON: %s", code, exc_info=e)
            raise e
        return output_dict

    @staticmethod
    def put_json_to_url(url: str, data: Dict, headers: List[List[str]] = None) -> None:
        """
        Converts data to JSON and PUT it to the specified URL
        :param url: URL to send PUT request to
        :param data: data to send, as JSON
        :param headers: List of HTTP headers to add to the request
        """
        headers_dict = Commons.create_headers_dict(headers)
        requests.put(url, headers=headers_dict, json=data)

    @staticmethod
    def check_numbers(message: str) -> bool:
        """
        Checks that an argument is purely numbers
        :param message: String to check for pure number-ness
        """
        message = message.lower().replace(" ", "")
        if message.count(".") > 1:
            return False
        if message.replace(".", "").isdigit():
            return True
        return False

    @staticmethod
    def check_calculation(message: str) -> bool:
        """
        Checks that an argument is purely numbers and calculation characters
        :param message: String to be checked to see if it's a calculation
        """
        message = message.strip().lower()
        valid_chars = [str(x) for x in range(10)]
        valid_chars += [".", ")", "^", "*", "x", "/", "%", "+", "-", "pi", "e", " "]
        valid_chars += [
            "acos(",
            "asin(",
            "atan(",
            "cos(",
            "sin(",
            "tan(",
            "sqrt(",
            "log(",
        ]
        valid_chars += [
            "acosh(",
            "asinh(",
            "atanh(",
            "cosh(",
            "sinh(",
            "tanh(",
            "gamma(",
            "(",
        ]
        for char in valid_chars:
            message = message.replace(char, "")
        if message == "":
            return True
        else:
            return False

    @staticmethod
    def is_float_string(float_string: str) -> bool:
        """
        Checks whether a string is a valid float
        :param float_string: String to check for validity in float conversion
        """
        try:
            float(float_string)
            return True
        except ValueError:
            return False

    @classmethod
    def is_int_string(cls, int_string: str) -> bool:
        try:
            int(int_string)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_digits_from_start_or_end(string: str) -> Optional[str]:
        """
        Gets the longest string of digits from the start or end of a string, or None
        :param string: String to find sequence of digits from
        """
        start_digits = [
            string[:x]
            for x in range(1, len(string) + 1)
            if Commons.is_float_string(string[:x])
        ]
        if len(start_digits) != 0:
            return start_digits[-1]
        end_digits = [
            string[x:]
            for x in range(len(string))
            if Commons.is_float_string(string[x:])
        ]
        if len(end_digits) != 0:
            return end_digits[0]
        return None

    @staticmethod
    def get_calc_from_start_or_end(string: str) -> Optional[str]:
        """
        Gets the longest calculation of digits from the start or end of a string, or None
        :param string: String to find calculation from
        """
        start_digits = [
            string[:x]
            for x in range(1, len(string) + 1)
            if Commons.check_calculation(string[:x])
        ]
        if len(start_digits) != 0:
            return start_digits[-1]
        end_digits = [
            string[x:]
            for x in range(len(string))
            if Commons.check_calculation(string[x:])
        ]
        if len(end_digits) != 0:
            return end_digits[0]
        return None

    @staticmethod
    def list_greater(list_one: List[float], list_two: List[float]) -> Optional[bool]:
        """
        Checks whether listOne is "greater" than listTwo.
        Checks if an earlier element of listOne is greater than the equally placed element in listTwo
        :param list_one: List of elements, for checking against listTwo
        :param list_two: List of elements, to check against listOne
        """
        if len(list_one) != len(list_two):
            raise ValueError("Lists must be the same length.")
        for index in range(len(list_one)):
            if list_one[index] == list_two[index]:
                continue
            if list_one[index] > list_two[index]:
                return True
            return False
        return None

    @staticmethod
    def get_random_int(min_int: int, max_int: int, count: int = 1) -> List[int]:
        """
        Returns a list of random integers in a given range
        :param min_int: Minimum integer to return
        :param max_int: Maximum integer to return
        :param count: Number of random integers to return
        """
        # If there's no range, just return a list.
        if min_int == max_int:
            return [min_int] * count
        output_list = []
        for _ in range(count):
            output_list.append(random.randint(min_int, max_int))
        return output_list

    @staticmethod
    def get_random_choice(choice_list: List[T], count: int = 1) -> List[T]:
        """
        Replacement for random.choice
        :param choice_list: List of choices to choose from
        :param count: Number of choices to pick
        """
        rand_int = Commons.get_random_int(0, len(choice_list) - 1, count)
        output_list = []
        for x in range(count):
            output_list.append(choice_list[rand_int[x]])
        return output_list

    @staticmethod
    def upper(data: str) -> str:
        """
        Converts a string to upper case, except for the URL
        """
        # Find any URLs, convert line to uppercase, then convert URLs back to original
        urls = re.findall(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+",
            data,
        )
        data = data.upper()
        for url in urls:
            data = data.replace(url.upper(), url)
        return data

    @staticmethod
    def find_parameter(param_name: str, line: str) -> Optional[str]:
        """
        Finds a parameter value in a line, if the format parameter=value exists in the line
        """
        param_value = None
        param_regex = re.compile(
            r"(^|\s){}=([^\s]+)(\s|$)".format(param_name), re.IGNORECASE
        )
        param_search = param_regex.search(line)
        if param_search is not None:
            param_value = param_search.group(2)
        return param_value

    @staticmethod
    def find_any_parameter(param_list: List[str], line: str) -> Union[str, bool]:
        """
        Finds one of any parameter in a line.
        """
        for param_name in param_list:
            find = Commons.find_parameter(param_name, line)
            if find is not None:
                return find
        return False

    @staticmethod
    def html_escape(string: str) -> str:
        """
        Escapes a string to ensure it can be used in html without issues
        """
        return string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class CachedObject(Generic[S]):
    def __init__(self, setter: Callable[[], S], cache_expiry: Optional[timedelta] = None) -> None:
        """
        :type setter: Callable
        :type cache_expiry: timedelta
        """
        self.setter: Callable[[], S] = setter
        self.cache_expiry: timedelta = (
            cache_expiry if cache_expiry is not None else timedelta(minutes=5)
        )
        self.cache_time: Optional[datetime.datetime] = None
        self.value: Optional[S] = None

    def get(self) -> S:
        if (
            self.cache_time is None
            or (self.cache_time + self.cache_expiry) < datetime.datetime.now()
        ):
            self.value = self.setter()
            self.cache_time = datetime.datetime.now()
        return self.value


def inherits_from(child: Type, parent_name: str) -> bool:
    if inspect.isclass(child):
        if parent_name in [c.__name__ for c in inspect.getmro(child)[1:]]:
            return True
    return False
