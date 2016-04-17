import time
import datetime
import urllib.request
import re
import json
import random
from datetime import timedelta


class ISO8601ParseError(SyntaxError):
    """
    ISO-8601 parsing error
    """
    pass


class Commons(object):
    """
    Class of commons methods, useful anywhere, but all static.
    """
    END_LINE = '\r\n'
    BOOL_STRING_DICT = {True: "True", False: "False", None: "None"}
    ALL_CHANNELS = "all_channels"
    ALL_SERVERS = "all_servers"

    @staticmethod
    def current_timestamp():
        """
        Constructor
        """
        return "[{:02d}:{:02d}:{:02d}]".format(*time.gmtime()[3:6])

    @staticmethod
    def chunk_string(string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]

    @staticmethod
    def chunk_string_dot(string, length):
        if len(string) <= length:
            return [string]
        else:
            list_of_strings = [string[:length - 3] + '...']
            rest_of_string = string[length - 3:]
            while len(rest_of_string) > length - 3:
                list_of_strings += ['...' + rest_of_string[:length - 6] + '...']
                rest_of_string = rest_of_string[length - 6:]
            list_of_strings += ['...' + rest_of_string]
            return list_of_strings

    @staticmethod
    def read_file_to_list(filename):
        f = open(filename, "r")
        file_list = []
        raw_line = f.readline()
        while raw_line != '':
            file_list.append(raw_line.replace("\n", ''))
            raw_line = f.readline()
        return file_list

    @staticmethod
    def get_domain_name(url):
        """
        Gets the domain name of a URL, removing the TLD
        :param url: URL to find domain of
        :type url: str
        """
        # Sanitise the URL, removing protocol and directories
        url = url.split("://")[-1]
        url = url.split("/")[0]
        url = url.split(":")[0]
        # Get the list of TLDs, from mozilla's http://publicsuffix.org
        tld_list = [x.strip() for x in open("store/tld_list.txt", "rb").read().decode("utf-8").split("\n")]
        url_split = url.split(".")
        url_tld = None
        for tld_test in ['.'.join(url_split[x:]) for x in range(len(url_split))]:
            if tld_test in tld_list:
                url_tld = tld_test
                break
        # If you didn't find the TLD, just return the longest bit.
        if url_tld is None:
            # noinspection PyTypeChecker
            return url_split.sort(key=len)[-1]
        # Else return the last part before the TLD
        return url[:-len(url_tld) - 1].split('.')[-1]

    @staticmethod
    def string_to_bool(string):
        """
        Converts a string to a boolean.
        :param string: String to convert to boolean
        :type string: str
        """
        string = string.lower()
        if string in ['1', 'true', 't', 'yes', 'y', 'on', 'enabled', 'enable']:
            return True
        if string in ['0', 'false', 'f', 'no', 'n', 'off', 'disabled', 'disable']:
            return False
        return None

    @staticmethod
    def is_string_null(string):
        """
        Checks if a string could mean null.
        :param string: String to check for meaning null
        :type string: str
        """
        string = string.lower()
        if string in ['0', 'false', 'off', 'disabled', 'disable', '', 'nul', 'null', 'none', 'nil']:
            return True
        return False

    @staticmethod
    def string_from_file(string):
        """
        Loads a string from a file. Converting booleans or null values accordingly.
        :param string: String to load as true, false, null or original string
        :type string: str
        """
        input_bool = Commons.string_to_bool(string)
        if input_bool in [True, False]:
            return input_bool
        if Commons.is_string_null(string):
            return None
        return string

    @staticmethod
    def ordinal(number):
        """
        Returns the ordinal of a number
        :param number: Number to get ordinal string for
        :type: number: int
        """
        if number % 10 == 1 and number % 100 != 11:
            return str(number) + "st"
        elif number % 10 == 2 and number % 100 != 12:
            return str(number) + "nd"
        elif number % 10 == 3 and number % 100 != 13:
            return str(number) + "rd"
        else:
            return str(number) + "th"

    @staticmethod
    def format_unix_time(time_stamp):
        """
        Returns a string, formatted datetime from a timestamp
        :param time_stamp: unix timestamp
        :type time_stamp: int
        """
        return datetime.datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def load_url_string(url, headers=None):
        """
        Takes a url to an xml resource, pulls it and returns a dictionary.
        :param url: URL to download
        :type url: str
        :param headers: List of HTTP headers to add to request
        :type headers: list
        """
        if headers is None:
            headers = []
        page_request = urllib.request.Request(url)
        page_request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        for header in headers:
            page_request.add_header(header[0], header[1])
        page_opener = urllib.request.build_opener()
        code = page_opener.open(page_request).read().decode('utf-8')
        return code

    @staticmethod
    def load_url_json(url, headers=None, json_fix=False):
        """
        Takes a url to a json resource, pulls it and returns a dictionary.
        :param url: URL of json to download
        :type url: str
        :param headers: List of HTTP headers to add to request
        :type headers: list
        :param json_fix: Whether to "fix" the JSON being returned for parse errors
        :type json_fix: bool
        """
        if headers is None:
            headers = []
        code = Commons.load_url_string(url, headers)
        if json_fix:
            code = re.sub(',+', ',', code)
            code = code.replace('[,', '[').replace(',]', ']')
        output_dict = json.loads(code)
        return output_dict

    @staticmethod
    def check_numbers(message):
        """
        Checks that an argument is purely numbers
        :param message: String to check for pure number-ness
        :type message: str
        """
        message = message.lower().replace(" ", "")
        if message.count(".") > 1:
            return False
        if message.replace(".", "").isdigit():
            return True
        return False

    @staticmethod
    def check_calculation(message):
        """
        Checks that an argument is purely numbers and calculation characters
        :param message: String to be checked to see if it's a calculation
        :type message: str
        """
        message = message.strip().lower()
        valid_chars = [str(x) for x in range(10)]
        valid_chars += [".", ")", "^", "*", "x", "/", "%", "+", "-", "pi", "e", " "]
        valid_chars += ["acos(", "asin(", "atan(", "cos(", "sin(", "tan(", "sqrt(", "log("]
        valid_chars += ["acosh(", "asinh(", "atanh(", "cosh(", "sinh(", "tanh(", "gamma(", "("]
        for char in valid_chars:
            message = message.replace(char, "")
        if message == "":
            return True
        else:
            return False

    @staticmethod
    def is_float_string(float_string):
        """
        Checks whether a string is a valid float
        :param float_string: String to check for validity in float conversion
        :type float_string: str
        """
        try:
            float(float_string)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_digits_from_start_or_end(string):
        """
        Gets the longest string of digits from the start or end of a string, or None
        :param string: String to find sequence of digits from
        :type string: str
        :return: str | None
        """
        start_digits = [string[:x] for x in range(1, len(string) + 1) if Commons.is_float_string(string[:x])]
        if len(start_digits) != 0:
            return start_digits[-1]
        end_digits = [string[x:] for x in range(len(string)) if Commons.is_float_string(string[x:])]
        if len(end_digits) != 0:
            return end_digits[0]
        return None
        # return ([string[:x] for x in range(1, len(string)+1) if Commons.is_float_string(string[:x])][::-1] +
        # [string[x:] for x in range(len(string)) if Commons.is_float_string(string[x:])] + [None])[0]

    @staticmethod
    def get_calc_from_start_or_end(string):
        """
        Gets the longest calculation of digits from the start or end of a string, or None
        :param string: String to find calculation from
        :type string: str
        :return: str | None
        """
        start_digits = [string[:x] for x in range(1, len(string) + 1) if Commons.check_calculation(string[:x])]
        if len(start_digits) != 0:
            return start_digits[-1]
        end_digits = [string[x:] for x in range(len(string)) if Commons.check_calculation(string[x:])]
        if len(end_digits) != 0:
            return end_digits[0]
        return None
        # return ([string[:x] for x in range(1, len(string)+1) if Commons.is_float_string(string[:x])][::-1] +
        # [string[x:] for x in range(len(string)) if Commons.is_float_string(string[x:])] + [None])[0]

    @staticmethod
    def list_greater(list_one, list_two):
        """
        Checks whether listOne is "greater" than listTwo.
        Checks if an earlier element of listOne is greater than the equally placed element in listTwo
        :param list_one: List of elements, for checking against listTwo
        :type list_one: list
        :param list_two: List of elements, to check against listOne
        :type list_two: list
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
    def get_random_int(min_int, max_int, count=1):
        """
        Returns a list of random integers in a given range
        :param min_int: Minimum integer to return
        :type min_int: int
        :param max_int: Maximum integer to return
        :type max_int: int
        :param count: Number of random integers to return
        :type count: int
        :return: list
        """
        # If there's no range, just return a list.
        if min_int == max_int:
            return [min_int] * count
        # random_org_url = "https://www.random.org/integers/?num=" + str(count) + "&format=plain&min=" + \
        #                  str(min_int) + "&max=" + str(max_int) + "&col=1&base=10"
        # user_agent_headers = [["User-Agent", "Hallo IRCBot hallo@dr-spangle.com"]]
        # api_response = Commons.load_url_string(random_org_url, user_agent_headers)
        # if "Error:" not in api_response:
        #     return [int(x) for x in api_response.split("\n") if x != ""]
        # Otherwise, use random module
        output_list = []
        for _ in range(count):
            output_list.append(random.randint(min_int, max_int))
        return output_list

    @staticmethod
    def get_random_choice(choice_list, count=1):
        """
        Replacement for random.choice
        :param choice_list: List of choices to choose from
        :type choice_list: list
        :param count: Number of choices to pick
        :type count: int
        :return: list
        """
        rand_int = Commons.get_random_int(0, len(choice_list) - 1, count)
        output_list = []
        for x in range(count):
            output_list.append(choice_list[rand_int[x]])
        return output_list

    @staticmethod
    def load_time_delta(delta_string):
        """
        Loads a timedelta object from an ISO8601 period string
        :param delta_string: ISO8601 period to convert to timedelta
        :type delta_string: str
        :return: timedelta
        """
        if delta_string[0] != "P" or delta_string[-1] != "S":
            raise ISO8601ParseError("Invalid ISO-8601 period string")
        clean_string = delta_string[1:-1]
        split_string = clean_string.split("T")
        if len(split_string) != 2:
            raise ISO8601ParseError("Invalid ISO-8601 period string")
        if split_string[0] == "":
            split_string[0] = "0"
        if split_string[1] == "":
            split_string[1] = "0"
        new_delta = timedelta(int(split_string[0]), int(split_string[1]))
        return new_delta

    @staticmethod
    def format_time_delta(delta):
        """
        Exports a timedelta into an ISO806 format string
        :param delta: timedelta
        :type delta: timedelta
        :return: string
        """
        output = "P" + str(delta.days) + "T" + str(delta.seconds) + "S"
        return output
